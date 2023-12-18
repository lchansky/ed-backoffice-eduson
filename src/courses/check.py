from functools import wraps

import pandas as pd

NAN = float('nan')
CLUSTERS = [
    "Аналитика",
    "Бухгалтерия",
    "Менеджмент",
    "Маркетинг",
    "HR",
    "Общее",
    "IT",
    "Финансы",
    "Подарочный",
    "Бесплатный курс",
]
COURSE_TYPES = ('Курс', 'Профессия')


def check_column_exists(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args[1] not in args[0].df.keys():
            args[0].df[f"Проверка {args[1]}"] = "Не найден столбец"
            return
        else:
            return func(*args, **kwargs)
    return wrapper


class CoursesTableChecker:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._is_processed = False
        self._is_checked = False
        self.is_valid = None

    def process_values(self):
        self.df["% скидки"] *= 100
        self.df["% скидки"] = self.df["% скидки"].fillna(0).astype(int)
        self.df["ID продукта"] = self.df["ID продукта"].fillna(0).astype(int)
        # self.df["Категория"] = self.df["Категория"].fillna(0).astype(int)
        # self.df["Статус"] = self.df["Статус"].fillna(0).astype(int)
        self.df["Полная цена"] = self.df["Полная цена"].fillna(0).astype(int)
        # self.df = self.df.convert_dtypes(convert_floating=False)
        # self.df = self.df.applymap(lambda x: NAN if isinstance(x, NAType) else x)
        self._is_processed = True

    def check(self):
        if not self._is_processed:
            raise ValueError('Перед проверкой нужно вызвать метод обработки данных self.process_values()')

        self.check_name("Продукт для шаблонов (название курса)")
        self.check_number("Цена со скидкой")
        self.check_number("Полная цена")
        self.check_text_length("Описание продукта", 3000)
        self.check_cluster("Кластер")
        self.check_number("ID продукта")
        self.check_number("% скидки")
        self.check_course_type("Тип курса")
        self.check_number("Продолжительность")
        # self.check_not_empty("Лендинг")  # TODO: вернуть
        # self.check_not_empty("Formname")  # TODO: вернуть
        self.check_not_empty_for_free_courses("Ссылка для входа", "Кластер")
        self.check_not_empty_for_free_courses("Ссылка регистрации", "Кластер")
        self.check_price_of_free_and_paid_courses("Цена со скидкой", "Кластер")

        self._is_checked = True

        errors = self.errors_dict
        if errors["Активные курсы"]:
            self.is_valid = False
        else:
            self.is_valid = True

        return errors

    @property
    def errors_dict(self) -> dict:
        """
        Состав выходного словаря:
        {
            "кластер 1": [
                {
                    "product_name": "продукт 1",
                    "errors": {
                        "Колонка X": "Ошибка ла-ла-ла",
                        "Колонка T": "Ошибка ту-ту-ту",
                    },
                },
                {
                    "product_name": "продукт 2",
                    "errors": {
                        "Колонка X": "Ошибка ла-ла-ла",
                    },
                },
            ]
            "кластер 2": {
                .....
            },
        }
        """
        if not self._is_checked:
            raise ValueError('Сначала нужно вызвать метод проверки данных self.check()')
        errors = {
            "Активные курсы": {},
            "Архивные курсы": {},
        }
        df = self.df.copy(deep=True)
        df = df.fillna(0)
        for idx, row in df.iterrows():
            cluster = row["Кластер"]
            product_name = row["Продукт для шаблонов (название курса)"]
            is_active = False
            if isinstance(row["Статус"], list):
                for status in row["Статус"]:
                    if status == "Активный в фиде":
                        is_active = True
            product_errors = {}
            for col, value in row.items():
                if str(col).startswith('Проверка ') and value:
                    column_name = str(col).replace('Проверка ', '')
                    product_errors[column_name] = value
            if product_errors:
                if is_active:
                    key = "Активные курсы"
                else:
                    key = "Архивные курсы"

                if not errors[key].get(cluster):
                    errors[key][cluster] = []
                errors[key][cluster].append(
                    {
                        "product_name": product_name,
                        "errors": product_errors,
                    }
                )
        return errors

    @check_column_exists
    def check_cluster(self, column: str):
        self.df[f"Проверка {column}"] = self.df[column].apply(
            lambda x: NAN if x in CLUSTERS else "Неизвестный кластер"
        )

    @check_column_exists
    def check_name(self, column):
        def check(x):
            if not x or not isinstance(x, str):
                return 'Поле должно быть не пустым и заполнено текстом'
            return NAN
        self.df[f"Проверка {column}"] = self.df[column].apply(check)

    @check_column_exists
    def check_text_length(self, column: str, length: int):
        def check(x):
            if isinstance(x, str) and len(x) > length:
                return f'Поле должно быть не более {length} символов'
            else:
                return NAN
        self.df[f"Проверка {column}"] = self.df[column].apply(check)

    @check_column_exists
    def check_number(self, column: str):
        def check(x):
            try:
                int(x)
            except (ValueError, TypeError):
                return 'Поле должно быть числом и не быть пустым'
            else:
                return NAN
        self.df[f"Проверка {column}"] = self.df[column].apply(check)

    @check_column_exists
    def check_not_empty(self, column: str):
        def check(x):
            if x or x == 0:
                return NAN
            else:
                return 'Поле не должно быть пустым'
        self.df[f"Проверка {column}"] = self.df[column].apply(check)

    @check_column_exists
    def check_not_empty_for_free_courses(self, column_for_check: str, cluster_column: str):
        new_column = []
        for idx, row in self.df.iterrows():
            cluster_name = row[cluster_column]
            value = row[column_for_check]
            if cluster_name == "Бесплатный курс":
                if value != "" and value != NAN and value is not None:
                    new_column.append(NAN)
                else:
                    new_column.append("Поле должно быть заполнено для бесплатных курсов")
            else:
                new_column.append(NAN)
        self.df[f"Проверка {column_for_check}"] = new_column

    @check_column_exists
    def check_course_type(self, column: str):
        def check(x):
            if x not in COURSE_TYPES:
                return f'Поле должно быть одним из этих вариантов: {COURSE_TYPES}'
            else:
                return NAN
        self.df[f"Проверка {column}"] = self.df[column].apply(check)

    @check_column_exists
    def check_price_of_free_and_paid_courses(self, price_column: str, cluster_column: str):
        new_column = []
        for idx, row in self.df.iterrows():
            cluster_name = row[cluster_column]
            price = row[price_column]
            if cluster_name == "Бесплатный курс":
                if price != 0 or price != "0":
                    new_column.append("Цена должна быть 0 для бесплатных курсов")
                else:
                    new_column.append(NAN)
            else:
                if price == 0 or price == "0":
                    new_column.append("Цена не должна быть 0 для платных курсов")
                else:
                    new_column.append(NAN)

        self.df[f"Проверка {price_column}"] = new_column


def main():
    df = pd.read_csv('feed_export_notion.csv')
    fc = CoursesTableChecker(df)
    fc.process_values()
    fc.check()
    df.to_excel('result.xlsx')
    pass


if __name__ == '__main__':
    main()
