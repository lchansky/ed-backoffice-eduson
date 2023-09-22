from django.contrib import admin

from certificates.models import Certificate, Course


class CertificateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Certificate._meta.fields]
    list_filter = ("date", "student_fio", "course")
    search_fields = ("student_fio", "course__name")


class CourseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Course._meta.fields]
    list_filter = ("name", "hours")
    search_fields = ("name", "hours")


admin.site.register(Certificate, CertificateAdmin)
admin.site.register(Course, CourseAdmin)


