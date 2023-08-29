import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models import (
    Model,
    BooleanField,
    DateTimeField,
    ForeignKey,
    DO_NOTHING,
    UUIDField,
    ManyToManyField
)
from django.utils import timezone

User = get_user_model()


class Invitation(Model):
    invite_code = UUIDField(unique=True, verbose_name='Код приглашения', default=uuid.uuid4, editable=False)
    permissions = ManyToManyField(Permission, verbose_name='Права доступа для нового пользователя', blank=True)

    created_at = DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    used_at = DateTimeField(blank=True, null=True, verbose_name='Дата использования')

    is_used = BooleanField(default=False, verbose_name='Использован')
    used_by = ForeignKey(User, blank=True, null=True, on_delete=DO_NOTHING)


    class Meta:
        verbose_name = 'Инвайт код'
        verbose_name_plural = 'Инвайт коды'

    def use(self, used_by: User):
        self.is_used = True
        self.used_by = used_by
        self.used_at = timezone.now()
        for permission in self.permissions.all():
            used_by.user_permissions.add(permission)
        used_by.save()
        self.save()
