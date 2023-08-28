from rest_framework import serializers

from promocodes.models import Promocode


class PromocodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Promocode
        fields = ('name', 'type', 'discount')

    @property
    def data(self):
        data = super().data
        data['status'] = 200
        if isinstance(data['discount'], float) and data['type'] in ('additional_discount', 'fix_discount'):
            data['discount'] = self.instance.discount / 100
        if self.instance.type == 'free_course':
            data['course_title'] = self.instance.course_title
        return data
