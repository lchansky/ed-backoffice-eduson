import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render

from check_feed.check import FeedChecker
from check_feed.forms import CSVUploadForm, CHECK_FILE_ERRORS, GET_FILE_FOR_UPDATE_PRICES


@login_required(login_url='login')
def upload_csv(request: WSGIRequest):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            df = pd.read_csv(csv_file.file)
            fc = FeedChecker(df)
            fc.process_values()
            selected_action = form.cleaned_data['action']
            if selected_action == CHECK_FILE_ERRORS:
                errors_data = fc.check()
                messages.success(request, "CSV файл успешно проверен.")
                return render(
                    request,
                    'check_feed/show_check_report.html',
                    {'title': 'Отчет о проверке', 'errors_data': dict(errors_data)}
                )
            elif selected_action == GET_FILE_FOR_UPDATE_PRICES:
                df = fc.get_df_with_amocrm_friendly_columns()
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="amocrm_update_prices.csv"'
                df.to_csv(path_or_buf=response, index=False)
                messages.success(request, "CSV файл для обновления цен успешно сформирован.")
                return response

    else:
        form = CSVUploadForm()

    return render(
        request,
        'check_feed/upload_csv.html',
        {'form': form, 'title': 'Загрузка файла с фидом (.csv)'}
    )
