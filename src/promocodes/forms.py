from django.forms import Form, CharField, ModelForm, FileField
from django.forms.widgets import TextInput, Select, DateInput, NumberInput, CheckboxInput, FileInput

from promocodes.models import Promocode


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
        help_texts = {
            'deadline': 'Чтобы сделать промокод бессрочным, оставьте поле пустым',
        }


class PromocodeEditForm(ModelForm):
    class Meta:
        model = Promocode
        fields = ['type', 'discount', 'deadline', 'is_active', ]
        widgets = {
            'type': Select(attrs={'class': 'form-select'}),
            'discount': NumberInput(attrs={'class': 'form-control'}),
            'deadline': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'deadline': 'Чтобы сделать промокод бессрочным, оставьте поле пустым',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.deadline:
            self.initial['deadline'] = self.instance.deadline.isoformat()


class PromocodesUploadForm(Form):
    file = FileField(
        label='Файл с промокодами. Доступные форматы: .csv, .xlsx.',
        widget=FileInput({'class': 'form-control-file', 'type': 'file', "style": "display: inline-block; padding: 10px;"}),
    )
