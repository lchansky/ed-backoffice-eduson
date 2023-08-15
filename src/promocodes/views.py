from copy import deepcopy
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, FormView, DetailView, UpdateView, CreateView

from .forms import PromocodeSearchForm, PromocodeCreateForm, PromocodeEditForm
from .models import Promocode


def home(request: WSGIRequest):
    return render(request, 'promocodes/promocode_list.html', {'title': 'Промокоды'})


class PromocodeList(LoginRequiredMixin, ListView, FormView):
    model = Promocode
    template_name = 'promocodes/promocode_list.html'
    context_object_name = 'promocodes'
    extra_context = {'title': 'Промокоды'}
    login_url = 'login'
    paginate_by = 10
    form_class = PromocodeSearchForm

    def form_valid(self, form):
        query_string = urlencode(form.cleaned_data)
        base_url = reverse('promocodes')
        url = f'{base_url}?{query_string}'  # /?name=КАКОЕ-ТО-ИМЯ
        return redirect(url)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        params = deepcopy(self.request.GET)
        params.pop('page', None)
        context['active_filters_query'] = params.urlencode()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        is_active = self.request.GET.get('is_active')
        if is_active:
            is_active = True if is_active == 'true' else False
            queryset = queryset.filter(is_active=is_active)

        name = self.request.GET.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class PromocodeDetail(LoginRequiredMixin, DetailView):
    model = Promocode
    template_name = 'promocodes/promocode_detail.html'
    context_object_name = 'promocode'
    extra_context = {'title': 'Промокод'}
    login_url = 'login'


class PromocodeCreate(LoginRequiredMixin, CreateView):
    model = Promocode
    template_name = 'promocodes/promocode_create.html'
    context_object_name = 'promocode'
    form_class = PromocodeCreateForm
    extra_context = {'title': 'Добавление промокода'}
    login_url = 'login'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Промокод добавлен.')
        return super().form_valid(form)


class PromocodeEdit(LoginRequiredMixin, UpdateView):
    model = Promocode
    context_object_name = 'promocode'
    template_name = 'promocodes/promocode_edit.html'
    extra_context = {'title': 'Редактирование промокода'}
    form_class = PromocodeEditForm
    login_url = 'login'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Изменения сохранены')
        return super().form_valid(form)

