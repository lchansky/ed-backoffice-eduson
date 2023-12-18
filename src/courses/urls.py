from django.urls import path

from courses.views import *

urlpatterns = [
    path('error_log/<int:pk>', ErrorLogView.as_view(), name='courses_error_log'),
]
