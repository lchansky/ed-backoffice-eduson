from django.contrib import admin

from courses.models import ErrorLog, CoursesVersion, PricesHistory

admin.site.register(ErrorLog)
admin.site.register(CoursesVersion)
admin.site.register(PricesHistory)

