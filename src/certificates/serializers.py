from rest_framework import serializers
from rest_framework.fields import CharField

from .models import Certificate, Course


class CertificateSerializer(serializers.ModelSerializer):
    course_name = CharField(max_length=200)

    class Meta:
        model = Certificate
        fields = ('date', 'student_fio', 'course_name')

    def create(self, validated_data):
        course = None
        if course_name := validated_data.get('course_name'):
            courses = Course.objects.filter(name=course_name)
            if courses:
                course = courses[0]

        certificate = Certificate(
            date=validated_data['date'],
            student_fio=validated_data['student_fio'],
            course=course,
        )
        certificate.save()
        return certificate

    def data(self):
        data: dict = self.instance.__dict__
        data.pop('_state')
        return data
