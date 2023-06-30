from django.db.models import Model, DateField, CharField, BigIntegerField, ForeignKey, PROTECT
from django.urls import reverse


class Certificate(Model):
    date = DateField(verbose_name='Дата окончания')
    student_fio = CharField(max_length=100, verbose_name='ФИО студента')
    course = ForeignKey("Course", blank=True, null=True, on_delete=PROTECT, verbose_name='Курс')

    class Meta:
        verbose_name = 'Удостоверение'
        verbose_name_plural = 'Удостоверения'

    def __str__(self):
        return f'{self.pk}'

    def get_absolute_url(self):
        return reverse('certificate_detail', kwargs={'pk': self.pk})


class Course(Model):
    name = CharField(max_length=200, verbose_name='Название')
    hours = BigIntegerField(verbose_name='Длительность (часы)')

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.hours} ч)'

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'pk': self.pk})

    def get_success_url(self):
        return reverse('course_list')
