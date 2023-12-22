from django.urls import path

from courses.views import *

urlpatterns = [
    path('error_log/<int:pk>', ErrorLogView.as_view(), name='courses_error_log'),
    path('table_for_amo_update_prices', table_for_amo_update_prices_view, name='courses_table_for_amo_update_prices'),
]
