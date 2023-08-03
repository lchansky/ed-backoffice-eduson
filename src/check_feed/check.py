from functools import wraps

import pandas as pd
from requests import RequestException

from .utils import get_image_size_in_pixels, healthcheck_url

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
CLUSTERS_NUMBERS = {
    1: 'Бухгалтерия',
    2: 'Аналитика',
    3: 'Excel',
    4: 'HR',
    5: 'Управление и бизнес',
    6: 'Маркетинг',
    7: 'Профессии на удаленке',
    8: 'Продажи',
    9: 'Soft-Skills',
    10: 'Популярные курсы',
    11: 'IT',
    12: 'Финансы',
}
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


class FeedChecker:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.checks_log = {}
        self.__is_processed = False
        self.__is_checked = False

    def process_values(self):
        self.df["% скидки"] *= 100
        self.df["% скидки"] = self.df["% скидки"].fillna(0).astype(int)
        self.__is_processed = True

    def check(self):
        if not self.__is_processed:
            raise ValueError('Перед проверкой нужно вызвать метод обработки данных self.process_values()')

        self.check_name("﻿Название курса (лендинги и amoCRM)")
        self.check_url_health_and_length("product_url", 2048)
        self.check_picture_size("picture_url")
        self.check_integer("Цена со скидкой")
        self.check_integer_or_empty("Полная цена")
        self.check_text_length("product_description", 3000)

        self.check_cluster("Кластер")
        self.check_url_health_and_length("Ссылка на программу", 35)
        self.check_integer("product_enum")
        self.check_integer_or_empty("% скидки")
        self.check_cluster_number("category_id", "Кластер")
        self.check_course_type("course_type")
        self.check_integer("duration_months")
        self.check_not_empty("Ссылка на лендинг")
        self.check_not_empty("Formname")
        self.check_not_empty("demo_url")
        self.check_not_empty("Категория (продукт)")
        self.check_not_empty_for_free_courses("Ссылка для входа", "Кластер")
        self.check_not_empty_for_free_courses("Ссылка регистрации", "Кластер")

        self.__is_checked = True

        return self.errors_dict

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
        if not self.__is_checked:
            raise ValueError('Сначала нужно вызвать метод проверки данных self.check()')
        errors = {}
        df = self.df.copy(deep=True)
        df = df.fillna(0)
        for idx, row in df.iterrows():
            cluster = row["Кластер"]
            product_name = row["﻿Название курса (лендинги и amoCRM)"]
            product_errors = {}
            for col, value in row.items():
                if str(col).startswith('Проверка ') and value:
                    column_name = str(col).replace('Проверка ', '')
                    product_errors[column_name] = value
            if product_errors:
                if not errors.get(cluster):
                    errors[cluster] = []
                errors[cluster].append(
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
            error_texts = []
            if not x or not isinstance(x, str):
                return 'Поле должно быть не пустым и заполнено текстом'
            if '(' in x or ')' in x:
                error_texts.append('Название рекомендуется указывать без скобок')
            if len(x) > 50:
                error_texts.append('Длина более 50 символов, рекомендуется укоротить')
            if error_texts:
                return ';'.join(error_texts)
            else:
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
    def check_integer(self, column: str):
        def check(x):
            try:
                int(x)
            except (ValueError, TypeError):
                return 'Поле должно быть числом и не быть пустым'
            else:
                return NAN
        self.df[f"Проверка {column}"] = self.df[column].apply(check)

    @check_column_exists
    def check_integer_or_empty(self, column: str):
        def check(x):
            if x == NAN or x is None:
                return NAN
            try:
                int(x)
            except (ValueError, TypeError):
                return 'Поле должно быть числом или пустым'
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
    def check_url_health_and_length(self, column: str, length: int):
        def check(x):
            error_texts = []
            if x == NAN or x is None or x == "":
                return 'Поле не должно быть пустым'
            if not isinstance(x, str):
                return 'Поле должно быть строкой'

            try:
                healthcheck_url(x)
            except RequestException as e:
                error_texts.append(f'Ошибка подключения: {e}')

            if len(x) > length:
                error_texts.append(f'Рекомендуется сократить ссылку на {len(x) - length} символов')
            if error_texts:
                return ';'.join(error_texts)
            else:
                return NAN

        self.df[f"Проверка {column}"] = self.df[column].apply(check)

    @check_column_exists
    def check_picture_size(self, column: str):
        def check(x):
            if x == NAN or x is None or x == "":
                return 'Поле не должно быть пустым'
            elif isinstance(x, str):
                try:
                    image_size = get_image_size_in_pixels(x)
                except (RequestException, IOError) as e:
                    return f"Ошибка при получении размера изображения: {e}"
                else:
                    width, height = image_size
                    if width <= 500 and height <= 500:
                        return NAN
                    else:
                        return 'Изображение должно быть 500х500 или меньше, это требование партнёров CPA'
            else:
                return 'URL должен быть строкой'
        self.df[f"Проверка {column}"] = self.df[column].apply(check)

    @check_column_exists
    def check_cluster_number(self, cluster_number_column: str, cluster_column: str):
        new_column = []
        for idx, row in self.df.iterrows():
            cluster_name = row[cluster_column]
            cluster_number = row[cluster_number_column]
            try:
                cluster_number = int(cluster_number)
            except (ValueError, TypeError):
                value = 'Поле должно содержать число и не быть пустым'
            else:
                if cluster_number in CLUSTERS_NUMBERS.keys():
                    found_cluster_name = CLUSTERS_NUMBERS.get(cluster_number)
                    if found_cluster_name != cluster_name and found_cluster_name in CLUSTERS:
                        value = f'Значение не совпадает! Номер {cluster_number} соответствует кластеру {found_cluster_name}'
                    else:
                        value = NAN
                else:
                    value = f'Поле должно содержать следующие значения: {list(CLUSTERS_NUMBERS.keys())}'
            new_column.append(value)

        self.df[f"Проверка {cluster_number_column}"] = new_column

    @check_column_exists
    def check_course_type(self, column: str):
        def check(x):
            if x not in COURSE_TYPES:
                return f'Поле должно быть одним из этих вариантов: {COURSE_TYPES}'
            else:
                return NAN
        self.df[f"Проверка {column}"] = self.df[column].apply(check)


def main():
    df = pd.read_csv('feed_export_notion.csv')
    fc = FeedChecker(df)
    fc.process_values()
    fc.check()
    df.to_excel('result.xlsx')
    pass


if __name__ == '__main__':
    main()
