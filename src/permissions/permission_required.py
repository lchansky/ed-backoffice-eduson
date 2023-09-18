from functools import wraps

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


def permission_required(perm, redirect_url=None, message="У вас отсутствуют права"):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.has_perm(perm):
                return view_func(request, *args, **kwargs)
            else:
                if redirect_url:
                    messages.warning(request, message)
                    return redirect(redirect_url)
                else:
                    return redirect('home')

        return _wrapped_view

    return decorator
