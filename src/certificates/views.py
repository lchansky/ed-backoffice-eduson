import datetime
import io
import os

import pandas as pd
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect, HttpRequest, Http404, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from telebot import TeleBot

from .forms import CertificateCreateForm, UserLoginForm, CertificateEditForm, CourseCreateForm, CourseEditForm, \
    UserSettingsForm
from .images import CertificateImageGenerator
from .models import Certificate, Course
from .serializers import CertificateSerializer


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы успешно авторизованы')
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    """Деавторизует пользователя. Редирект на home"""
    logout(request)
    return redirect('login')


class CertificateList(LoginRequiredMixin, ListView):
    model = Certificate
    template_name = 'certificates/certificate_list.html'
    context_object_name = 'certificates'
    extra_context = {'title': 'Список удостоверений об образовании'}
    login_url = 'login'


class CertificateDetail(LoginRequiredMixin, DetailView):
    model = Certificate
    template_name = 'certificates/certificate_detail.html'
    context_object_name = 'certificate'
    extra_context = {'title': 'Удостоверение'}
    login_url = 'login'


class CertificateCreate(LoginRequiredMixin, CreateView):
    model = Certificate
    template_name = 'certificates/certificate_create.html'
    context_object_name = 'certificate'
    form_class = CertificateCreateForm
    extra_context = {'title': 'Добавление удостоверения'}
    login_url = 'login'

    def form_valid(self, form):
        messages.success(
            self.request,
            'Удостоверение добавлено. Чтобы сгенерировать изображение, нажмите на кнопку ниже',
        )
        return super().form_valid(form)


@method_decorator(csrf_exempt, name='dispatch')
class CertificateAPIView(APIView):
    def post(self, request):
        serializer = CertificateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            image_generator = CertificateImageGenerator()
            image = image_generator.generate_rgb_certificate(certificate=serializer.instance)
            filename = f'Удостоверение {serializer.instance.pk}.png'
            image2 = image_generator.generate_certificate_for_print(certificate=serializer.instance)
            filename2 = f'Удостоверение {serializer.instance.pk} для печати.png'
            url = serializer.instance.get_absolute_url()
            TeleBot(os.getenv('TG_TOKEN')).send_document(
                os.getenv('TG_CHAT_ID'),
                document=(filename, image.getvalue()),
            )
            TeleBot(os.getenv('TG_TOKEN')).send_document(
                os.getenv('TG_CHAT_ID'),
                document=(filename2, image2.getvalue()),
                caption=f'{request.build_absolute_uri(url)}',
            )
            return Response(serializer.data(), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CertificateEdit(LoginRequiredMixin, UpdateView):
    model = Certificate
    context_object_name = 'certificate'
    template_name = 'certificates/certificate_edit.html'
    extra_context = {'title': 'Редактирование удостоверения'}
    form_class = CertificateEditForm
    login_url = 'login'

    def form_valid(self, form):
        messages.success(self.request, 'Изменения сохранены')
        return super().form_valid(form)


@login_required(login_url='login')
def certificate_image_view(request: HttpRequest, pk: int, image_type: str):
    try:
        certificate = Certificate.objects.get(pk=pk)
    except:
        return Http404

    image_generator = CertificateImageGenerator()
    if image_type == 'image':
        image = image_generator.generate_rgb_certificate(certificate)
    elif image_type == 'printer':
        image = image_generator.generate_certificate_for_print(certificate)
    else:
        return Http404

    image.seek(0)
    response = HttpResponse(content_type='image/png')
    response.write(image.getvalue())
    return response


def generate_excel_bytes(robots):
    wb = Workbook()
    for robot in robots:
        try:
            ws = wb[robot.get('model')]
        except KeyError:
            ws = wb.create_sheet(robot.get('model'))
            ws.append(tuple(robot.keys()))
        ws.append(tuple(robot.values()))
    if robots:
        wb.remove(wb.worksheets[0])

    excel_bytes = BytesIO()
    wb.save(excel_bytes)
    return excel_bytes.getvalue()


def get_weekly_report() -> bytes:
    start_last_week, end_last_week = get_last_week_range()
    robots = Robot.objects \
        .filter(created__gte=start_last_week, created__lte=end_last_week) \
        .values('model', 'version') \
        .annotate(count=Count('model')) \
        .order_by('model')
    return generate_excel_bytes(robots)


@login_required(login_url='login')
def certificate_download_all_info(request: HttpRequest):
    certificates = Certificate.objects.all().values('id', 'date', 'student_fio', 'course_id', 'course__name', 'course__hours')

    df = pd.DataFrame(certificates)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        df.to_excel(writer, index=False)

    date = datetime.date.today()
    response = HttpResponse(buffer.getvalue(), content_type="application/vnd.ms-excel")
    response['Content-Disposition'] = f'inline; filename=Выгрузка всех удостоверений {date}.xlsx'
    return response


class CourseList(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'certificates/course_list.html'
    context_object_name = 'courses'
    extra_context = {'title': 'Список удостоверений об образовании'}
    login_url = 'login'


class CourseDetail(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'certificates/course_detail.html'
    context_object_name = 'course'
    extra_context = {'title': '📚 Курс'}
    login_url = 'login'


class CourseCreate(LoginRequiredMixin, CreateView):
    model = Course
    template_name = 'certificates/course_create.html'
    context_object_name = 'course'
    form_class = CourseCreateForm
    extra_context = {'title': '📚 Добавление курса'}
    login_url = 'login'

    def form_valid(self, form):
        messages.success(
            self.request,
            'Удостоверение добавлено. Чтобы сгенерировать изображение, нажмите на кнопку ниже',
        )
        return super().form_valid(form)


class CourseEdit(LoginRequiredMixin, UpdateView):
    model = Course
    context_object_name = 'course'
    template_name = 'certificates/course_edit.html'
    extra_context = {'title': '📚 Редактирование курса'}
    form_class = CourseEditForm
    login_url = 'login'

    def form_valid(self, form):
        messages.success(self.request, 'Изменения сохранены')
        return super().form_valid(form)


class CourseDelete(LoginRequiredMixin, DeleteView):
    model = Course
    context_object_name = 'course'
    # template_name = 'certificates/course_delete.html'
    extra_context = {'title': 'Удаление курса'}
    # form_class = CourseEditForm
    login_url = 'login'

    def form_valid(self, form):
        try:
            form = super().form_valid(form)
            messages.success(self.request, 'Курс удалён')
            return form
        except ProtectedError:
            messages.error(self.request, 'Курс не может быть удалён, т.к. есть удостоверения, в которых он указан.')
            return HttpResponseRedirect(reverse('course_detail', kwargs={'pk': self.kwargs.get('pk')}))

    def get_success_url(self):
        return reverse('course_list')


class SettingsView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'certificates/settings.html'
    success_url = reverse_lazy('settings')
    extra_context = {'title': 'Настройки'}
    form_class = UserSettingsForm
    login_url = 'login'

    def form_valid(self, form):
        messages.success(self.request, 'Изменения сохранены')
        return super().form_valid(form)
