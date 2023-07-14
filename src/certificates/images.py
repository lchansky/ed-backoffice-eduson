
import io
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .models import Certificate
from django.conf import settings

from .utils import numeral_noun_declension

BASE_DIR = settings.BASE_DIR
BASE_MEDIA_DIR = BASE_DIR / 'certificates' / 'media'


class Drawer:
    font_path = BASE_MEDIA_DIR / 'times_new_roman.ttf'

    def __init__(self, template_path: str | Path, rgba: bool = False):
        self.image = Image.open(template_path)
        self.rgba = rgba
        if self.rgba:
            self.image.convert("RGBA")
            self._draw = ImageDraw.Draw(self.image, mode="RGBA")
        else:
            self._draw = ImageDraw.Draw(self.image)
        self._font = ImageFont.truetype(str(self.font_path), size=48)

    def scale_image(self, image: Image, scale: int | float):
        width, height = image.size
        image.thumbnail(
            (round(width * scale / 100), round(height * scale / 100)),
            Image.ANTIALIAS,
        )
        return image

    def draw_picture(self, picture_path: str | Path, xy: tuple[int, int], scale: int | float = 100):
        picture = Image.open(picture_path)
        if self.rgba:
            picture = picture.convert("RGBA")
        if scale != 100:
            picture = self.scale_image(picture, scale)

        if self.rgba:
            width, height = picture.size
            mask = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            mask.paste(picture, (0, 0, width, height))

            self.image.paste(picture, xy, mask=mask)
        else:
            self.image.paste(picture, xy)


    def draw_centered_text(self, xy: tuple[int, int], text: str):
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
    rgb_template_path = BASE_MEDIA_DIR / 'Шаблон_цвет.png'
    template_for_print_path = BASE_MEDIA_DIR / 'Шаблон_принтер.png'
    secretary_sign_path = BASE_MEDIA_DIR / 'Сакина_подпись.png'
    director_sign_path = BASE_MEDIA_DIR / 'Лена_подпись.png'
    stamp_path = BASE_MEDIA_DIR / 'Печать.png'

    def generate_rgb_certificate(self, certificate: Certificate) -> io.BytesIO:
        drawer = Drawer(self.rgb_template_path, rgba=True)

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
            text_hours = numeral_noun_declension(certificate.course.hours, 'час', 'часа', 'часов')
            drawer.draw_centered_text((2580, 1840), f"{certificate.course.hours} {text_hours}")
        else:
            drawer.draw_centered_text((2580, 1340), f"---------------")
            drawer.draw_centered_text((2580, 1840), f"---------------")

        drawer.draw_text((2580, 2036), f"Масолова Е.В.")
        drawer.draw_text((2506, 2122), f"Сокова С.Н.")

        drawer.draw_picture(self.stamp_path, (1560, 1810))
        drawer.draw_picture(self.director_sign_path, (2070, 1980))
        drawer.draw_picture(self.secretary_sign_path, (1970, 1920))

        width, height = drawer.image.size
        drawer.image.thumbnail((width // 2, height // 2), Image.ANTIALIAS)

        buffer = BytesIO()
        drawer.image.save(buffer, format='PNG')
        return buffer

    def generate_certificate_for_print(self, certificate: Certificate) -> io.BytesIO:

        drawer = Drawer(self.template_for_print_path)

        drawer.draw_centered_text((910, 1730), f"{certificate.pk}")
        drawer.draw_centered_text((910, 1910), f"Москва")

        date = certificate.date
        if date:
            date = date.strftime('%d.%m.%Y')
        drawer.draw_centered_text((910, 2095), f"{date}")

        certificate_series = str(certificate.pk)
        while len(certificate_series) < 4:
            certificate_series = '0' + certificate_series
        drawer.draw_centered_text((910, 2240), f"Серия ЭД №{certificate_series}")

        drawer.draw_centered_text((2580, 380), f"{certificate.student_fio}")
        drawer.draw_centered_text((2580, 780), f"ООО «Эдюсон»")

        if certificate.course:
            drawer.draw_centered_text((2580, 1345), f"{certificate.course.name}")
            text_hours = numeral_noun_declension(certificate.course.hours, 'час', 'часа', 'часов')
            drawer.draw_centered_text((2580, 1850), f"{certificate.course.hours} {text_hours}")
        else:
            drawer.draw_centered_text((2580, 1345), f"---------------")
            drawer.draw_centered_text((2580, 1850), f"---------------")

        drawer.draw_text((2580, 2066), f"Масолова Е.В.")
        drawer.draw_text((2506, 2152), f"Сокова С.Н.")

        buffer = BytesIO()
        drawer.image.save(buffer, format='PNG')
        return buffer
