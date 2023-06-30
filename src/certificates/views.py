from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView

from .forms import CertificateCreateForm, UserLoginForm, CertificateEditForm, CourseCreateForm, CourseEditForm
from .models import Certificate, Course


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


class CertificateDetail(LoginRequiredMixin, DetailView):
    model = Certificate
    template_name = 'certificates/certificate_detail.html'
    context_object_name = 'certificate'
    extra_context = {'title': 'Удостоверение'}


class CertificateCreate(LoginRequiredMixin, CreateView):
    model = Certificate
    template_name = 'certificates/certificate_create.html'
    context_object_name = 'certificate'
    form_class = CertificateCreateForm
    extra_context = {'title': 'Добавление удостоверения'}

    def form_valid(self, form):
        messages.success(
            self.request,
            'Удостоверение добавлено. Чтобы сгенерировать изображение, нажмите на кнопку ниже',
        )
        return super().form_valid(form)


class CertificateEdit(LoginRequiredMixin, UpdateView):
    model = Certificate
    context_object_name = 'certificate'
    template_name = 'certificates/certificate_edit.html'
    extra_context = {'title': 'Редактирование удостоверения'}
    form_class = CertificateEditForm

    def form_valid(self, form):
        messages.success(self.request, 'Изменения сохранены')
        return super().form_valid(form)


class CourseList(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'certificates/course_list.html'
    context_object_name = 'courses'
    extra_context = {'title': 'Список удостоверений об образовании'}


class CourseDetail(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'certificates/course_detail.html'
    context_object_name = 'course'
    extra_context = {'title': '📚 Курс'}


class CourseCreate(LoginRequiredMixin, CreateView):
    model = Course
    template_name = 'certificates/course_create.html'
    context_object_name = 'course'
    form_class = CourseCreateForm
    extra_context = {'title': '📚 Добавление курса'}

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

    def form_valid(self, form):
        messages.success(self.request, 'Изменения сохранены')
        return super().form_valid(form)


class CourseDelete(LoginRequiredMixin, DeleteView):
    model = Course
    context_object_name = 'course'
    template_name = 'certificates/course_delete.html'
    extra_context = {'title': 'Удаление курса'}
    # form_class = CourseEditForm

    def form_valid(self, form):
        messages.success(self.request, 'Курс удалён')
        return super().form_valid(form)
