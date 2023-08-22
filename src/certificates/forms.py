from django.forms import ModelForm, TextInput, DateInput, NumberInput, Select

from certificates.models import Certificate, Course


class CertificateCreateForm(ModelForm):
    class Meta:
        model = Certificate
        fields = '__all__'
        widgets = {
            'date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'student_fio': TextInput(attrs={'class': 'form-control'}),
            'course': Select(attrs={'class': 'form-select'}),
        }


class CertificateEditForm(ModelForm):
    class Meta:
        model = Certificate
        fields = '__all__'
        widgets = {
            'date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'student_fio': TextInput(attrs={'class': 'form-control'}),
            'course': Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['date'] = self.instance.date.isoformat()


class CourseCreateForm(ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'hours': NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        }


class CourseEditForm(ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'hours': NumberInput(attrs={'class': 'form-control'}),
        }
