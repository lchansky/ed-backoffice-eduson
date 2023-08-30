import datetime
import io

import pandas as pd
from django.contrib import admin
from django.contrib.admin import AllValuesFieldListFilter
from django.http import HttpResponse
from django.utils import timezone
from rangefilter.filters import DateTimeRangeFilterBuilder, DateRangeFilterBuilder, NumericRangeFilter

from promocodes.models import Promocode, PromocodeRequest


class PromocodeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Promocode._meta.fields]
    list_filter = ('type', 'is_active', 'created_at', 'updated_at', 'created_by', 'updated_by')
    search_fields = ('type', 'is_active')


class PromocodeRequestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PromocodeRequest._meta.fields]
    search_fields = ('promocode_name', )
    list_filter = (
        (
            "dt",
            DateTimeRangeFilterBuilder(
                title="Дата запроса",
                default_start=datetime.datetime(timezone.now().year, 1, 1),
                default_end=datetime.datetime(timezone.now().year, 12, 31),
            ),
        ),
        ("promocode_type", AllValuesFieldListFilter),
        ("promocode_discount", NumericRangeFilter),
        (
            "promocode_deadline",
            DateRangeFilterBuilder(
                title='Дедлайн промокода',
                default_start=timezone.now().date() - datetime.timedelta(days=30),
                default_end=timezone.now().date(),
            )
        ),
        ("response_status_code", AllValuesFieldListFilter),
    )

    def export_xlsx(self, request, queryset):
        data = queryset.values()
        df = pd.DataFrame(data)
        df['dt'] = df['dt'].astype(str)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer) as writer:
            df.to_excel(writer, index=False)
        date = datetime.date.today()
        response = HttpResponse(buffer.getvalue(), content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = f'attachment; filename=Выгрузка запросов {date}.xlsx'

        self.message_user(request, f'Файл с запросами сформирован. Всего {len(queryset)} шт.')
        return response

    export_xlsx.short_description = 'Скачать XLSX'
    actions = ['export_xlsx']

    def has_delete_permission(self, request, obj=None):
        # Disable delete for anyone
        return False


admin.site.register(Promocode, PromocodeAdmin)
admin.site.register(PromocodeRequest, PromocodeRequestAdmin)
