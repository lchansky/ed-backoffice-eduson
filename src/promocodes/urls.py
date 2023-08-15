from django.urls import path

from .views import *

urlpatterns = [
    path('', PromocodeList.as_view(), name='promocodes'),
    path('', PromocodeList.as_view(), name='promocode_list'),
    path('create', PromocodeCreate.as_view(), name='promocode_create'),
    path('<str:pk>', PromocodeDetail.as_view(), name='promocode_detail'),
    path('<str:pk>/edit', PromocodeEdit.as_view(), name='promocode_edit'),
]
