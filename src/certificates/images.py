
import io
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .models import Certificate
from src.proj.settings import BASE_DIR


def numeral_noun_declension(
    number,
    nominative_singular,
    genetive_singular,
    nominative_plural
):
    """
    Возвращает склонение под нужное число объектов.
    Например:
    >>> numeral_noun_declension(22, 'собака', 'собаки', 'собак')
    >>> "собаки"
"""
    last_digit = number % 10
    return (
        nominative_plural and (number in range(5, 20))
        or
        nominative_singular and (1 in (number, last_digit))
        or
        genetive_singular and ({number, last_digit} & {2, 3, 4})
        or
        nominative_plural
    )


class Drawer:
    font_path = BASE_DIR / 'certificates' / 'media' / 'times_new_roman.ttf'

    def __init__(self, template_path: Path):
        self.image = Image.open(template_path)
        self._draw = ImageDraw.Draw(self.image)
        self._font = ImageFont.truetype(str(self.font_path), size=48)

    def draw_centered_text(self, xy: tuple[float, float], text: str):
        x, y = xy
        text_coordinates = self._draw.textbbox((0, 0), text, font=self._font)
        text_width = text_coordinates[2]
        text_height = text_coordinates[3]

        new_x = x - text_width // 2
        new_y = y - text_height // 2
        self._draw.text((new_x, new_y), text, font=self._font, fill=(0, 0, 0))

    def draw_text(self, xy: tuple[float, float], text: str):
        self._draw.text(xy, text, font=self._font, fill=(0, 0, 0))


class CertificateImageGenerator:
    rgb_template_path = BASE_DIR / 'certificates' / 'media' / 'Шаблон_цвет.png'
    template_for_print_path = BASE_DIR / 'certificates' / 'media' / 'Шаблон_принтер.png'

    def generate_rgb_certificate(self, certificate: Certificate):
        return self._generate_certificate(self.rgb_template_path, certificate, compress=True)

    def generate_certificate_for_print(self, certificate: Certificate):
        return self._generate_certificate(self.template_for_print_path, certificate)

    def _generate_certificate(self, template_path: Path, certificate: Certificate, compress=False) -> io.BytesIO:
        drawer = Drawer(template_path)

        drawer.draw_centered_text((960, 1710), f"{certificate.pk}")
        drawer.draw_centered_text((960, 1900), f"Москва")

        date = certificate.date
        if date:
            date = date.strftime('%d.%m.%Y')
        drawer.draw_centered_text((960, 2080), f"{date}")

        certificate_series = str(certificate.pk)
        while len(certificate_series) < 4:
            certificate_series = '0' + certificate_series
        drawer.draw_centered_text((960, 2240), f"Серия ЭД №{certificate_series}")

        drawer.draw_centered_text((2580, 380), f"{certificate.student_fio}")
        drawer.draw_centered_text((2580, 780), f"ООО «Эдюсон»")

        if certificate.course:
            drawer.draw_centered_text((2580, 1340), f"{certificate.course.name}")
            text_hours = numeral_noun_declension(certificate.course.hours, 'академический час', 'академического часа', 'академических часов')
            drawer.draw_centered_text((2580, 1840), f"{certificate.course.hours} {text_hours}")
        else:
            drawer.draw_centered_text((2580, 1340), f"---------------")
            drawer.draw_centered_text((2580, 1840), f"---------------")

        drawer.draw_text((2580, 2036), f"Масолова Е.В.")
        drawer.draw_text((2506, 2122), f"Сокова С.Н.")

        if compress:
            width, height = drawer.image.size
            drawer.image.thumbnail((width // 2, height // 2), Image.ANTIALIAS)

        buffer = BytesIO()
        drawer.image.save(buffer, format='PNG')
        return buffer
