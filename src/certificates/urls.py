from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from certificates.views import *

urlpatterns = [
    path('', CertificateList.as_view(), name='certificate_list'),
    path('create', CertificateCreate.as_view(), name='certificate_create'),
    path('<int:pk>', CertificateDetail.as_view(), name='certificate_detail'),
    path('<int:pk>/edit', CertificateEdit.as_view(), name='certificate_edit'),
    path('<int:pk>-<str:image_type>.png', certificate_image_view, name='certificate_image'),
    path('download_all_info', certificate_download_all_info, name='certificate_download_all_info'),

    path('courses', CourseList.as_view(), name='course_list'),
    path('courses/create', CourseCreate.as_view(), name='course_create'),
    path('courses/<int:pk>', CourseDetail.as_view(), name='course_detail'),
    path('courses/<int:pk>/edit', CourseEdit.as_view(), name='course_edit'),
    path('courses/<int:pk>/delete', CourseDelete.as_view(), name='course_delete'),

    path('api/create_and_send_image', csrf_exempt(CertificateAPIView.as_view()))
]
