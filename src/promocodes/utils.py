import datetime

import pandas as pd
from django.db import IntegrityError

from promocodes.models import Promocode


class PromocodeImportException(Exception):
    pass


def str_to_date(date_str):
    try:
        if date_str == '01.01.2100':
            return pd.NA
        return datetime.datetime.strptime(date_str, '%d.%m.%Y')
    except ValueError:
        return pd.NA


def import_promocodes_from_xlsx(file, user):
    try:
        df = pd.read_csv(file.file)
    except:
        try:
            df = pd.read_excel(file.file)
        except:
            raise PromocodeImportException(
                f"Не удалось прочитать файл. "
                f"Убедитесь, что файл имеет расширение .csv или .xlsx."
            )
    try:
        df['deadline'] = df['deadline'].apply(str_to_date)
    except ValueError:
        raise PromocodeImportException(
            f"Не удалось прочитать файл. "
            f"Убедитесь, что все даты введены корректно, в формате 'дд.мм.гггг'."
        )
    df['name'] = df['name'].apply(lambda x: str(x).upper())
    promocodes_to_create = []
    for index, row in df.iterrows():
        try:
            if pd.isna(row['deadline']):
                deadline = None
            else:
                deadline = row['deadline'].date()

            if row['type'] in ('additional_discount', 'fix_discount'):
                discount = row['discount'] * 100
            elif row['type'] == 'additional_price':
                discount = row['discount']
            elif row['type'] in ('free_course', 'consultation'):
                discount = None
            else:
                discount = None

            promocode = Promocode(
                name=row['name'],
                type=row['type'],
                discount=discount,
                course_title=None if pd.isna(row['course_title']) else row['course_title'],
                deadline=deadline,
                created_by=user,
                updated_by=user,
            )
            if promocode.type == 'free_course' and not promocode.course_title:
                raise PromocodeImportException(
                    f"Не удалось импортировать промокоды. "
                    f"Для промокодов с типом 'Бесплатный курс' (free_course) "
                    f"необходимо указать название курса (course_title)"
                )
            if not pd.isna(row['discount']):
                if row['type'] in ('additional_discount', 'fix_discount') and not (0 < row['discount'] < 100):
                    raise PromocodeImportException("Скидка в процентах должна быть в диапазоне от 0 до 100")
                if row['type'] == 'additional_price' and not (0 < row['discount'] < 1000000):
                    raise PromocodeImportException("Скидка в рублях должна быть в диапазоне от 0 до 1.000.000")
            elif pd.isna(row['discount']) and row['type'] in ('additional_discount', 'fix_discount', 'additional_price'):
                raise PromocodeImportException(
                    "Скидка не может быть пустой для промокодов с типами "
                    "additional_discount, fix_discount и additional_price."
                )
            if row['type'] == 'free_course' and not row['course_title']:
                raise PromocodeImportException(
                    "Для промокода с типом 'Бесплатный курс' необходимо указать название курса."
                )
        except KeyError as exc:
            raise PromocodeImportException(
                f"Не удалось импортировать промокоды. "
                f"Убедитесь, что колонки имеют такие названия: 'name', 'type', 'discount', 'deadline', 'course_title'."
            )
        promocodes_to_create.append(promocode)
    try:
        Promocode.objects.bulk_create(promocodes_to_create)
    except IntegrityError:
        names = df['name'].tolist()
        promocodes_with_existing_name = Promocode.objects.filter(name__in=names)
        if promocodes_with_existing_name:
            promocodes_text = ', '.join([promocode.name for promocode in promocodes_with_existing_name])
            raise PromocodeImportException(
                f"Не удалось импортировать промокоды, т.к. некоторые из таблицы уже есть в базе. "
                f"Данные промокоды необходимо убрать из таблицы: {promocodes_text}"
            )
        elif len(names) != len(set(names)):
            duplicates = list(set([name for name in names if names.count(name) > 1]))
            raise PromocodeImportException(
                f"Не удалось импортировать промокоды. "
                f"Уберите из таблицы промокоды, которые встречаются в таблице более 1 раза: {duplicates}"
            )
        else:
            raise PromocodeImportException(f"Не удалось импортировать промокоды. Непредвиденная ошибка.")
