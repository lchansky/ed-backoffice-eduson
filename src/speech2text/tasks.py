from celery import shared_task
from django.utils import timezone

from speech2text import voice_processor
from speech2text.models import TranscribedRecording


@shared_task
def transcribe_mp3_file(filename: str, binary_data: bytes, user_id: int = None):
    recording = TranscribedRecording.objects.create(
        audio_file_name=filename,
        created_by_id=user_id,
    )

    with open(recording.file_path, "wb") as f:
        f.write(binary_data)

    try:
        speeches = voice_processor.transcribe_mp3_file(filename, binary_data)
    except Exception as exc:
        print(exc)
        recording.status = TranscribedRecording.ERROR
    else:
        recording.status = TranscribedRecording.PROCESSED
        recording.speeches = speeches

    recording.processed_at = timezone.now()
    recording.save()
