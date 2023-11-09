from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from speech2text.views import *

urlpatterns = [
    path('upload_recording', upload_recording, name='upload_recording'),
    path('transcribe_recording', TranscribeRecordingAPI.as_view(), name='transcribe_recording'),
    path('recordings', RecordingsList.as_view(), name='recordings_list'),
    path('recordings/<int:pk>', RecordingDetail.as_view(), name='recording_detail'),
]
