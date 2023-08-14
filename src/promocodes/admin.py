from django.contrib import admin

from .models import Promocode


class PromocodeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Promocode._meta.fields]
    list_filter = ('code', 'type', 'is_active', 'created_at', 'updated_at', 'created_by', 'updated_by')
    search_fields = ('code', 'type')


admin.site.register(Promocode, PromocodeAdmin)
