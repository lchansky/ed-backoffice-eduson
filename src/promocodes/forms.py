from django.forms import Form, CharField, ModelForm
from django.forms.widgets import TextInput, Select, DateInput, NumberInput, CheckboxInput

from .models import Promocode


class PromocodeSearchForm(Form):
    name = CharField(
        widget=TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Название',
    )


class PromocodeCreateForm(ModelForm):
    class Meta:
        model = Promocode
        fields = ['name', 'type', 'discount', 'deadline', 'is_active', ]
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'type': Select(attrs={'class': 'form-select'}),
            'discount': NumberInput(attrs={'class': 'form-control'}),
            'deadline': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PromocodeEditForm(PromocodeCreateForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.deadline:
            self.initial['deadline'] = self.instance.deadline.isoformat()
