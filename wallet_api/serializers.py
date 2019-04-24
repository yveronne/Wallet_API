from django.contrib.auth.hashers import make_password
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


class CommentSerializer(serializers.ModelSerializer):
    merchantpoint = MerchantPointSerializer
    class Meta:
        model = Comment
        fields = ('title', 'content', 'customernumber')


class WaitingLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitingLine
        fields = ('date', 'customernumber')

