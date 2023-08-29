from django.contrib import admin

from main.models import Invitation


class InvitationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Invitation._meta.fields]


admin.site.register(Invitation, InvitationAdmin)
