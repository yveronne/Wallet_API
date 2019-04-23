from rest_framework import serializers
from .models import *

class TownSerializer(serializers.ModelSerializer):

    class Meta:
        model = Town
        fields = ('name', )



class DistrictSerializer(serializers.ModelSerializer):

    class Meta:
        model = District
        fields = ('name', 'townname')



class MerchantPointSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()

    class Meta:
        model = MerchantPoint
        fields = '__all__'