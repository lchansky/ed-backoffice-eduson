import io
import os
import traceback

import pandas as pd
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from telebot import TeleBot

from courses.check import CoursesTableChecker
from courses.difference_definer import compare_two_tables
from courses.models import CoursesVersion, ErrorLog, PricesHistory
from courses.notion import NotionAPI


notion = NotionAPI()
bot = TeleBot(os.getenv("TG_TOKEN"))
TG_INTEGRATIONS_CHAT_ID = os.getenv("TG_INTEGRATIONS_CHAT_ID")


@shared_task
def load_notion_and_process_notion_courses_info():
    try:
        load_notion_data_compare_with_previous_and_load_to_db()
    except Exception as e:
        send_exception_to_tg(e)


def send_exception_to_tg(exc: Exception):
    buffer = io.StringIO()
    buffer.write(traceback.format_exc())
    buffer.seek(0)
    bot.send_document(
        TG_INTEGRATIONS_CHAT_ID,
        document=("traceback.txt", buffer.getvalue()),
        caption=f"Ошибка при загрузке и обработке данных из Notion: {exc}",
    )
    buffer.close()


def write_prices_changes_to_db(notion_courses_table: list[dict]):
    prices = []
    for row in notion_courses_table:
        dt = timezone.now().date()
        prices.append(
            PricesHistory(
                dt=dt,
                notion_id=row["id"],
                product_name=row["Продукт для шаблонов (название курса)"],
                full_price=row["Полная цена"],
                discount_percent=row["% скидки"],
                price_with_discount=row["Цена со скидкой"],
                price_per_month_with_discount=row["В мес со скидкой"],
                price_per_month_without_discount=row["В мес без скидки"],
            )
        )
    PricesHistory.objects.bulk_create(prices)


def load_notion_data_compare_with_previous_and_load_to_db():
    notion_courses_table = notion.get_courses_table_data()

    df = pd.DataFrame(notion_courses_table)
    checker = CoursesTableChecker(df)
    checker.process_values()
    errors = checker.check()

    if not checker.is_valid:
        error_log = ErrorLog.objects.create(errors=errors)
        bot.send_message(
            TG_INTEGRATIONS_CHAT_ID,
            f"Ошибка при загрузке данных из Notion.\n"
            f"[Посмотреть логи]({settings.BASE_URL}{error_log.get_absolute_url()})",
            parse_mode="Markdown",
        )
        return

    previous_actual_course_version = CoursesVersion.objects.filter(actual=True).order_by("-pk").first()
    if not previous_actual_course_version:
        if not CoursesVersion.objects.all():
            CoursesVersion.objects.create(table=notion_courses_table, valid=True, actual=True)
            bot.send_message(
                TG_INTEGRATIONS_CHAT_ID,
                "Первая версия сводной таблицы успешно загружена в БД, т.к. в БД не было ни одной версии таблицы"
            )
        else:
            bot.send_message(
                TG_INTEGRATIONS_CHAT_ID,
                """Ошибка! В БД нет таблицы с пометкой "актуальная", но есть предыдущие версии."""
            )
        return
    
    previous_table = previous_actual_course_version.table

    difference = compare_two_tables(previous_table, notion_courses_table)

    if not difference:
        bot.send_message(
            TG_INTEGRATIONS_CHAT_ID,
            "Новая версия сводной таблицы не отличается от предыдущей. "
            "Ничего не загружено в БД. (Отладочное сообщение, убрать потом)",
        )
        return

    if difference:
        CoursesVersion.objects.create(table=notion_courses_table, valid=True, actual=True)
        bot.send_message(
            TG_INTEGRATIONS_CHAT_ID,
            "Новая версия сводной таблицы успешно загружена в БД",
        )
        if difference.has_prices_changes():
            write_prices_changes_to_db(notion_courses_table)
            bot.send_message(
                TG_INTEGRATIONS_CHAT_ID,
                "В новой версии таблицы есть изменения цен. Слепок цен записан в БД.",
            )



