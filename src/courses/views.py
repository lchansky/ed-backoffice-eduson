import pandas as pd
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView

from courses.models import ErrorLog, CoursesVersion


class ErrorLogView(DetailView):
    model = ErrorLog
    context_object_name = 'error_log'
    template_name = 'courses/error_log.html'


def get_df_with_amocrm_friendly_columns(courses_version: CoursesVersion):
    df = pd.DataFrame(courses_version.table)
    df["ID продукта"] = df["ID продукта"].fillna(0).astype(int)
    df["Полная цена"] = df["Полная цена"].fillna(0).astype(int)
    df["% скидки"] *= 100
    df["% скидки"] = df["% скидки"].fillna(0).astype(int)
    df["is_active"] = df["Статус"].apply(lambda x: 1 if "Активный в фиде" in x else 0)
    df["category_id"] = df["category_id"].fillna(0).astype(int)
    df["Продолжительность"] = df["Продолжительность"].fillna(0).astype(int)
    df["Архивный курс"] = df["Статус"].apply(lambda x: 1 if "Архивный курс" in x else 0)
    df["is_blog"] = df["Статус"].apply(lambda x: 1 if "SEO" in x else 0)
    df["course_type"] = df["Тип курса"].apply(lambda x: "Профессия" if x == "Профессия" else "Курс")

    new_columns = {
        'Продукт для шаблонов (название курса)': 'Название',
        'ID продукта': 'product_key',
        'Описание продукта': 'product_description',
        'Лендинг': 'product_url',
        'Ссылка на программу': 'program_url',
        'Ссылка на демо': 'demo_url',
        'Полная цена': 'fake_price',
        'Цена со скидкой': 'real_price',
        '% скидки': 'discount',
        'В мес со скидкой': 'installment_price',
        'Ссылка на картинку с лендинга': 'picture_url',
        'Продолжительность': 'duration_months',
        'Описание статьи для шаблонов': 'article description',
    }
    df_renamed = df.rename(columns=new_columns)

    columns_to_keep = [
        "Название",
        "product_key",
        "product_description",
        "product_url",
        "program_url",
        "demo_url",
        "fake_price",
        "real_price",
        "discount",
        "discount_amount",
        "installment_price",
        "is_active",
        "category_id",
        "picture_url",
        "course_type",
        "duration_months",
        "Архивный курс",
        "is_blog",
        "article description",
    ]
    result_df = df_renamed[columns_to_keep]

    columns_to_add = [
        "Группа",
        "Ставка НДС",
        "discount deadline",
        "This is set",
        "Предмет расчета",
        "Способ расчета",
        "program_list",
        "ya_category_id",
        "webinars_exist",
        "community_exist",
        "course_difficulty",
    ]
    for column in columns_to_add:
        result_df[column] = None

    return result_df


def table_for_amo_update_prices_view(request: WSGIRequest):
    last_actual_courses_version = CoursesVersion.objects.filter(actual=True).last()
    try:
        df = get_df_with_amocrm_friendly_columns(last_actual_courses_version)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="amocrm_update_prices.csv"'
        df.to_csv(path_or_buf=response, index=False)
    except Exception as exc:
        messages.error(request, f"Ошибка при формировании файла для обновления цен: {exc}")
        return redirect('home')
    messages.success(request, "CSV файл для обновления цен успешно сформирован.")
    return response

