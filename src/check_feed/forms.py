from django.forms import FileField, Form, FileInput


class CSVUploadForm(Form):
    csv_file = FileField(label='Файл с фидом', widget=FileInput({'class': 'form-control-file', 'type': 'file'}))
