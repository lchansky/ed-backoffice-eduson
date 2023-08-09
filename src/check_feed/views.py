import pandas as pd
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render

from .check import FeedChecker
from .forms import CSVUploadForm


def upload_csv(request: WSGIRequest):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            df = pd.read_csv(csv_file.file)
            fc = FeedChecker(df)
            fc.process_values()
            errors_data = fc.check()
            messages.success(request, "CSV файл успешно проверен.")
            return render(
                request,
                'check_feed/show_check_report.html',
                {'title': 'Отчет о проверке', 'errors_data': dict(errors_data)}
            )
    else:
        form = CSVUploadForm()

    return render(
        request,
        'check_feed/upload_csv.html',
        {'form': form, 'title': 'Загрузка файла с фидом (.csv)'}
    )
