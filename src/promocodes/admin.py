import datetime
import io

import pandas as pd
from django.contrib import admin
from django.http import HttpResponse
from rangefilter.filters import DateTimeRangeFilterBuilder

from promocodes.models import Promocode, PromocodeRequest


class PromocodeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Promocode._meta.fields]
    list_filter = ('type', 'is_active', 'created_at', 'updated_at', 'created_by', 'updated_by')
    search_fields = ('type', 'is_active')


class PromocodeRequestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PromocodeRequest._meta.fields]
    list_filter = (
        "dt",
        DateTimeRangeFilterBuilder(
            title="Custom title",
            default_start=datetime.datetime(2023, 1, 1),
            default_end=datetime.datetime(2023, 12, 31),
        ),
    ),

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
