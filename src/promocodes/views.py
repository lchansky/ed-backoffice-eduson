from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views.generic import ListView

from .models import Promocode


def home(request: WSGIRequest):
    return render(request, 'promocodes/promocode_list.html', {'title': 'Промокоды'})


class PromocodeList(LoginRequiredMixin, ListView):
    model = Promocode
    template_name = 'promocodes/promocode_list.html'
    context_object_name = 'promocodes'
    extra_context = {'title': 'Промокоды'}
    login_url = 'login'
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        is_active = self.request.GET.get('is_active')
        if is_active:
            context['active_filters_query'] = f'is_active={is_active}'
        else:
            context['active_filters_query'] = ''
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        is_active = self.request.GET.get('is_active')

        if is_active:
            is_active = True if is_active == 'true' else False
            queryset = queryset.filter(is_active=is_active)

        return queryset

