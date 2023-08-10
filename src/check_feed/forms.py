from django.forms import FileField, Form, FileInput, ChoiceField, Select


CHECK_FILE_ERRORS = 'check'
GET_FILE_FOR_UPDATE_PRICES = 'update'


class CSVUploadForm(Form):
    OPTIONS = (
        (CHECK_FILE_ERRORS, 'Проверить файл на ошибки'),
        (GET_FILE_FOR_UPDATE_PRICES, 'Получить файл для обновления цен'),
    )

    csv_file = FileField(label='Файл с фидом', widget=FileInput({'class': 'form-control-file', 'type': 'file'}))
    action = ChoiceField(label='Выберите действие', choices=OPTIONS, widget=Select({'class': 'form-select'}))
