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

    promocodes_to_create = []
    for index, row in df.iterrows():
        try:
            if pd.isna(row['deadline']):
                deadline = None
            else:
                deadline = row['deadline'].date()

            promocode = Promocode(
                name=row['name'],
                type=row['type'],
                discount=row['discount'],
                deadline=deadline,
                created_by=user,
                updated_by=user,
            )
        except Exception as exc:
            raise PromocodeImportException(
                f"Не удалось импортировать промокоды. "
                f"Убедитесь, что колонки имеют такие названия: 'name', 'type', 'discount', 'deadline'."
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
                f"Не удалось импортировать промокоды. "
                f"Данные промокоды уже есть в базе: {promocodes_text}"
            )
        elif len(names) != len(set(names)):
            duplicates = list(set([name for name in names if names.count(name) > 1]))
            raise PromocodeImportException(
                f"Не удалось импортировать промокоды. "
                f"Данные промокоды встречаются в таблице более 1 раза: {duplicates}"
            )
        else:
            raise PromocodeImportException(f"Не удалось импортировать промокоды. Непредвиденная ошибка.")
