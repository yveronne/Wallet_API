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


class WaitingLineSerializer(serializers.ModelSerializer):

    class Meta:
        model = WaitingLine
        fields = ('date', 'customernumber')



class MerchantPointSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()
    waitingListSize = serializers.SerializerMethodField('get_waitinglist_size')

    class Meta:
        model = MerchantPoint
        fields = ('id', 'name', 'area', 'district', 'position', 'waitingListSize' )

    def get_waitinglist_size(self, merchantPoint):
        waitingListSize = merchantPoint.waitingline_set.filter(wasserved=False).count()
        return waitingListSize



class CommentSerializer(serializers.ModelSerializer):
    merchantpoint = MerchantPointSerializer()

    class Meta:
        model = Comment
        fields = ('title', 'content', 'customernumber', 'merchantpoint')



class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('expectedvalidationdate', 'type', 'customernumber')