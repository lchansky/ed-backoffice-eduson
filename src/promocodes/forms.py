import datetime

from django.core.exceptions import ValidationError
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
        fields = ['name', 'type', 'discount', 'deadline', 'is_active', 'course_title', ]
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'type': Select(attrs={'class': 'form-select'}),
            'discount': NumberInput(attrs={'class': 'form-control'}),
            'deadline': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': CheckboxInput(attrs={'class': 'form-check-input'}),
            'course_title': TextInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'deadline': 'Чтобы сделать промокод бессрочным, оставьте поле пустым',
            'course_title': 'Название курса, на который действует промокод. '
                            'Должно быть заполнено, если курс бесплатный.',
        }

    def clean_course_title(self):
        if self.cleaned_data['type'] == 'free_course' and not self.cleaned_data['course_title']:
            raise ValidationError(
                "Для промокода с типом 'Бесплатный курс' необходимо указать название курса."
            )
        return self.cleaned_data['course_title']

    def clean_name(self):
        return self.cleaned_data['name'].upper()

    def clean_deadline(self):
        if self.cleaned_data['deadline'] and self.cleaned_data['deadline'] < datetime.date.today():
            raise ValidationError("Дата истечения не может быть в прошлом.")
        return self.cleaned_data['deadline']

    def clean_discount(self):
        discount = self.cleaned_data['discount']
        discount_type = self.cleaned_data['type']
        if discount is not None:
            if discount_type in ('additional_discount', 'fix_discount') and not (0 < discount < 100):
                raise ValidationError("Скидка в процентах должна быть в диапазоне от 0 до 100")
            if discount_type == 'additional_price' and not (0 < discount < 1000000):
                raise ValidationError("Скидка в рублях должна быть в диапазоне от 0 до 1.000.000")
        elif discount is None and discount_type in ('additional_discount', 'fix_discount', 'additional_price'):
            raise ValidationError("Скидка не может быть пустой.")
        return discount


class PromocodeEditForm(PromocodeCreateForm):
    class Meta:
        model = Promocode
        fields = ['type', 'discount', 'deadline', 'is_active', 'course_title', ]
        widgets = {
            'type': Select(attrs={'class': 'form-select'}),
            'discount': NumberInput(attrs={'class': 'form-control'}),
            'deadline': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': CheckboxInput(attrs={'class': 'form-check-input'}),
            'course_title': TextInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'deadline': 'Чтобы сделать промокод бессрочным, оставьте поле пустым',
            'course_title': 'Название курса, на который действует промокод. '
                            'Должно быть заполнено, если курс бесплатный.',
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
