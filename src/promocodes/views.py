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

