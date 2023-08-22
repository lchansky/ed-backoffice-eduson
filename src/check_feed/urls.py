from django.urls import path

from check_feed.views import *

urlpatterns = [
    path('', upload_csv, name='upload_feed_csv'),
]
