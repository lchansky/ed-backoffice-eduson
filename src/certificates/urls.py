from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    path('', CertificateList.as_view(), name='home'),
    path('', CertificateList.as_view(), name='certificate_list'),
    path('certificates/create', CertificateCreate.as_view(), name='certificate_create'),
    path('certificates/<int:pk>', CertificateDetail.as_view(), name='certificate_detail'),
    path('certificates/<int:pk>/edit', CertificateEdit.as_view(), name='certificate_edit'),
    path('certificates/<int:pk>-<str:image_type>.png', certificate_image_view, name='certificate_image'),

    path('courses', CourseList.as_view(), name='course_list'),
    path('courses/create', CourseCreate.as_view(), name='course_create'),
    path('courses/<int:pk>', CourseDetail.as_view(), name='course_detail'),
    path('courses/<int:pk>/edit', CourseEdit.as_view(), name='course_edit'),
    path('courses/<int:pk>/delete', CourseDelete.as_view(), name='course_delete'),

    path("login/", user_login, name="login"),
    path('logout/', user_logout, name='logout'),
    path('settings/', SettingsView.as_view(), name='settings'),

    path('api/certificates/create_and_send_image', csrf_exempt(CertificateAPIView.as_view()))
]
