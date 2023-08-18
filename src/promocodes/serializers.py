from rest_framework import serializers

from .models import Promocode


class PromocodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Promocode
        fields = ('name', 'type', 'discount', 'deadline')

    @property
    def data(self):
        data = super().data
        data['status'] = '200'
        return data
