from copy import deepcopy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from rest_framework.response import Response
from rest_framework.views import APIView


from permissions.permission_required import PermissionRequiredMixin, permission_required
from speech2text.models import TranscribedRecording
from speech2text.tasks import transcribe_mp3_file


def upload_recording(request):
    return render(
        request,
        'speech2text/upload_recording.html',
        {'title': 'Загрузка файла', 'user_id': request.user.id if request.user.is_authenticated else ''}
    )


class TranscribeRecordingAPI(APIView):
    def post(self, request):
        uploaded_file: TemporaryUploadedFile = request.FILES['audio_file']
        user_id = request.POST.get('user_id', None)

        if not uploaded_file.name.endswith('.mp3'):
            return Response({'message': 'Неверный формат файла'}, status=400)

        with open(uploaded_file.file.name, 'rb') as f:
            transcribe_mp3_file.delay(filename=uploaded_file.name, binary_data=f.read(), user_id=user_id)

        return Response({'message': 'Обработка файла начата'}, status=200)


class RecordingsList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = TranscribedRecording
    template_name = 'speech2text/recordings_list.html'
    context_object_name = 'recordings'
    extra_context = {'title': 'Аудиозаписи'}
    login_url = 'login'
    paginate_by = 10
    permission_required = 'speech2text.view_transcribedrecording'
    permission_denied_redirect = 'home'
    permission_denied_message = 'У вас нет прав для просмотра аудиозаписей'


class RecordingDetail(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = TranscribedRecording
    template_name = 'speech2text/recording_detail.html'
    context_object_name = 'recording'
    extra_context = {'title': 'Аудиозапись'}
    login_url = 'login'
    permission_required = 'speech2text.view_transcribedrecording'
    permission_denied_redirect = 'home'
    permission_denied_message = 'У вас нет прав для просмотра аудиозаписей'




