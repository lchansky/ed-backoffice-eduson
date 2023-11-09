from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Model, DateTimeField, CharField, JSONField, ForeignKey, DO_NOTHING
from django.urls import reverse

User = get_user_model()


class TranscribedRecording(Model):
    class Meta:
        verbose_name = 'Транскрибированная запись'
        verbose_name_plural = 'Транскрибированные записи'
        ordering = ['-created_at']

    PROCESSING = 'Processing'
    PROCESSED = 'Processed'
    ERROR = 'Error'
    STATUS_CHOICES = [
        (PROCESSING, 'Обработка⏳'),
        (PROCESSED, 'Обработано✅'),
        (ERROR, 'Ошибка обработки❌'),
    ]

    created_by = ForeignKey(User, on_delete=DO_NOTHING, blank=True, null=True, verbose_name='Кем создана')
    created_at = DateTimeField(auto_now_add=True)

    audio_file_name = CharField(max_length=100)

    status = CharField(max_length=20, choices=STATUS_CHOICES, default=PROCESSING, blank=True, null=True)
    processed_at = DateTimeField(blank=True, null=True)
    speeches = JSONField(blank=True, null=True)

    def __repr__(self):
        return (f'<TranscribedRecording '
                f'(id={self.pk}; status={self.status}; '
                f'audio_file_name={self.audio_file_name}; '
                f'created_at={self.created_at};)>')

    def get_absolute_url(self):
        return reverse('recording_detail', kwargs={'pk': self.pk})
    
    @property
    def file_path(self):
        return settings.SPEECH2TEXT_MEDIA_DIR / self.audio_file_name

    @property
    def text(self):
        return ' '.join([speech['text'] for speech in self.speeches]) if self.speeches else ''
