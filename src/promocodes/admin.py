from django.contrib import admin

from .models import Promocode, PromocodeRequest


class PromocodeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Promocode._meta.fields]
    list_filter = ('name', 'type', 'is_active', 'created_at', 'updated_at', 'created_by', 'updated_by')
    search_fields = ('type', 'is_active')


class PromocodeRequestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PromocodeRequest._meta.fields]


admin.site.register(Promocode, PromocodeAdmin)
admin.site.register(PromocodeRequest, PromocodeRequestAdmin)
