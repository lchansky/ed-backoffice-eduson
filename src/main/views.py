from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from main.forms import UserSettingsForm, UserLoginForm, UserRegisterForm
from mix_panel import mp


class MainPage(LoginRequiredMixin, TemplateView):
    template_name = 'main/main_page.html'
    extra_context = {'title': 'Главная страница'}
    login_url = 'login'


def user_register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserRegisterForm(data=request.POST)
        if form.is_valid():
            form.save()
            mp.set_user_properties(
                form.cleaned_data['username'],
                {
                    '$first_name': form.cleaned_data['first_name'],
                    '$last_name': form.cleaned_data['last_name'],
                }
            )
            messages.success(request, 'Вы успешно зарегистрированы')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


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


class SettingsView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/settings.html'
    success_url = reverse_lazy('settings')
    extra_context = {'title': 'Настройки'}
    form_class = UserSettingsForm
    login_url = 'login'

    def form_valid(self, form):
        messages.success(self.request, 'Изменения сохранены')
        return super().form_valid(form)
