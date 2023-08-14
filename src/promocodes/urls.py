from django.urls import path

from .views import *

urlpatterns = [
    path('', PromocodeList.as_view(), name='promocodes_home'),
]
