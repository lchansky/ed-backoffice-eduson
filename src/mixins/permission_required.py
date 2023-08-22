from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin as DjangoPermissionRequiredMixin
from django.shortcuts import redirect


class PermissionRequiredMixin(DjangoPermissionRequiredMixin):
    permission_denied_message = 'У вас нет прав для этого действия'
    permission_denied_redirect = 'home'

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            messages.warning(request, self.get_permission_denied_message())
            return redirect(self.permission_denied_redirect)
        return super().dispatch(request, *args, **kwargs)
