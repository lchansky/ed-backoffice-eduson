from django.views.generic import DetailView

from courses.models import ErrorLog


class ErrorLogView(DetailView):
    model = ErrorLog
    context_object_name = 'error_log'
    template_name = 'courses/error_log.html'

