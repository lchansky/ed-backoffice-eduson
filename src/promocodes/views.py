import datetime
import io
from copy import deepcopy
from urllib.parse import urlencode

import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, FormView, DetailView, UpdateView, CreateView
from rest_framework.response import Response
from rest_framework.views import APIView

from mix_panel import mp
from mixins.permission_required import PermissionRequiredMixin
from promocodes.forms import PromocodeSearchForm, PromocodeCreateForm, PromocodeEditForm, PromocodesUploadForm
from promocodes.models import Promocode, PromocodeRequest
from promocodes.serializers import PromocodeSerializer
from promocodes.utils import import_promocodes_from_xlsx, PromocodeImportException


class PromocodeList(LoginRequiredMixin, PermissionRequiredMixin, ListView, FormView):
    model = Promocode
    template_name = 'promocodes/promocode_list.html'
    context_object_name = 'promocodes'
    extra_context = {'title': 'Промокоды'}
    login_url = 'login'
    paginate_by = 10
    form_class = PromocodeSearchForm
    permission_required = 'promocodes.view_promocode'
    permission_denied_redirect = 'home'
    permission_denied_message = 'У вас нет прав для просмотра промокодов'

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


class PromocodeDetail(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Promocode
    template_name = 'promocodes/promocode_detail.html'
    context_object_name = 'promocode'
    extra_context = {'title': 'Промокод'}
    login_url = 'login'
    permission_required = 'promocodes.view_promocode'
    permission_denied_redirect = 'home'
    permission_denied_message = 'У вас нет прав для просмотра промокода'


class PromocodeCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Promocode
    template_name = 'promocodes/promocode_create.html'
    context_object_name = 'promocode'
    form_class = PromocodeCreateForm
    extra_context = {'title': 'Добавление промокода'}
    login_url = 'login'
    permission_required = 'promocodes.add_promocode'
    permission_denied_redirect = 'promocode_list'
    permission_denied_message = 'У вас нет прав для создания промокода'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Промокод добавлен.')

        url_name = self.request.resolver_match.url_name if self.request.resolver_match else "Unknown URL"
        mp.track(
            self.request.user.username,
            'promocode_created',
            {
                'url_name': url_name,
                'app_name': self.__module__.split('.')[0],
            },
            user_properties={
                '$username': self.request.user.username,
                '$first_name': self.request.user.first_name,
                '$last_name': self.request.user.last_name,
                '$email': self.request.user.email,
            },
        )
        return super().form_valid(form)


class PromocodeEdit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Promocode
    context_object_name = 'promocode'
    template_name = 'promocodes/promocode_edit.html'
    extra_context = {'title': 'Редактирование промокода'}
    form_class = PromocodeEditForm
    login_url = 'login'
    permission_required = 'promocodes.change_promocode'
    permission_denied_redirect = 'promocode_list'
    permission_denied_message = 'У вас нет прав для редактирования промокода'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Изменения сохранены')
        url_name = self.request.resolver_match.url_name if self.request.resolver_match else "Unknown URL"
        mp.track(
            self.request.user.username,
            'promocode_edited',
            {
                'url_name': url_name,
                'app_name': self.__module__.split('.')[0],
            },
            user_properties={
                '$username': self.request.user.username,
                '$first_name': self.request.user.first_name,
                '$last_name': self.request.user.last_name,
                '$email': self.request.user.email,
            },
        )
        return super().form_valid(form)


@login_required(login_url='login')
def promocode_import_xlsx(request: WSGIRequest):
    if request.method == 'POST':
        form = PromocodesUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                import_promocodes_from_xlsx(request.FILES['file'], request.user)
            except PromocodeImportException as exc:
                messages.error(request, str(exc))
                return redirect('promocode_import_xlsx')
            else:
                messages.success(request, "Промокоды успешно импортированы.")

    else:
        form = PromocodesUploadForm()

    return render(
        request,
        'promocodes/promocode_import.html',
        {'form': form, 'title': 'Импорт промокодов'}
    )


@login_required(login_url='login')
def promocode_export_xlsx(request: WSGIRequest):
    promocodes = Promocode.objects.all().values()

    df = pd.DataFrame(promocodes)
    df['deadline'] = df['deadline'].apply(lambda x: x.strftime('%d.%m.%Y') if x else None)
    df['created_at'] = df['created_at'].apply(lambda x: x.strftime('%d.%m.%Y') if x else None)
    df['updated_at'] = df['updated_at'].apply(lambda x: x.strftime('%d.%m.%Y') if x else None)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        df.to_excel(writer, index=False)

    date = datetime.date.today()
    response = HttpResponse(buffer.getvalue(), content_type="application/vnd.ms-excel")
    response['Content-Disposition'] = f'attachment; filename=Выгрузка всех промокодов {date}.xlsx'
    return response


@method_decorator(csrf_exempt, name='dispatch')
class PromocodeAPIView(APIView):
    def get(self, request):
        name = request.query_params.get('name', '')
        uuid = request.query_params.get('uuid', '')
        yandex_client_id = request.query_params.get('yandex_client_id', '')
        promocode_request = PromocodeRequest(promocode_name=name, uuid=uuid, yandex_client_id=yandex_client_id)
        try:
            promocode = Promocode.objects.get(name=name)
        except Promocode.DoesNotExist:
            promocode_request.response_status_code = 404
            promocode_request.save()
            return Response({'status': 404, 'error': 'Промокод не найден'}, status=404)

        promocode_request.promocode_type = promocode.type
        promocode_request.promocode_discount = promocode.discount
        promocode_request.promocode_deadline = promocode.deadline

        if not promocode.is_active:
            promocode_request.response_status_code = 201
            promocode_request.save()
            return Response({'status': 201, 'error': 'Промокод деактивирован'}, status=201)

        if not promocode.is_expired:
            serializer = PromocodeSerializer(promocode)
            promocode_request.response_status_code = 200
            promocode_request.save()
            return Response(serializer.data, status=200)
        else:
            promocode_request.response_status_code = 201
            promocode_request.save()
            return Response({'status': 201, 'error': 'Срок действия промокода истек'}, status=201)
