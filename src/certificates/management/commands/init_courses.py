from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '''Загружает курсы из файла courses.csv, который должен лежать рядом с manage.py. 
    Если в базе есть хотя бы один курс, то команда не выполнится.'''

    def handle(self, *args, **options):
        import pandas as pd
        from ...models import Course
        courses = Course.objects.all()
        if not courses:
            df = pd.read_csv('courses.csv')
            for idx, row in df.iterrows():
                Course.objects.create(name=row["Курс"], hours=row["Часы"])
            self.stdout.write('Курсы успешно проинициализированы!')
        else:
            self.stdout.write('Таблица с курсами не пустая, пропускаю инициализацию курсов...')
