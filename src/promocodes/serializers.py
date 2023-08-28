from rest_framework import serializers

from promocodes.models import Promocode


class PromocodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Promocode
        fields = ('name', 'type', 'discount', 'deadline')

    @property
    def data(self):
        data = super().data
        data['status'] = 200
        if self.instance.type == 'free_course':
            data['course_title'] = self.instance.course_title
        return data
