from django.forms import Form, CharField
from django.forms.widgets import TextInput


class PromocodeSearchForm(Form):
    name = CharField(
        widget=TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Название',
    )
