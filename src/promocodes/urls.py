from django.urls import path

from .views import *

urlpatterns = [
    path('', PromocodeList.as_view(), name='promocodes'),
    path('', PromocodeList.as_view(), name='promocode_list'),
    path('create', PromocodeCreate.as_view(), name='promocode_create'),
    path('detail/<str:pk>', PromocodeDetail.as_view(), name='promocode_detail'),
    path('edit/<str:pk>', PromocodeEdit.as_view(), name='promocode_edit'),
    path('import_xlsx', promocode_import_xlsx, name='promocode_import_xlsx'),
]
