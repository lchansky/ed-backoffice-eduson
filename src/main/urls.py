from django.urls import path
from .views import *

urlpatterns = [
    path('', MainPage.as_view(), name='main_page'),
    path('', MainPage.as_view(), name='home'),
    path('login/', user_login, name="login"),
    path('logout/', user_logout, name='logout'),
    path('settings/', SettingsView.as_view(), name='settings'),
]
