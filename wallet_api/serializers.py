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
        fields = ('id', 'date', 'customernumber')

class WaitingLineUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitingLine
        fields = ('wasserved','servicedate')



class MerchantPointSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()
    waitingListSize = serializers.SerializerMethodField('get_waitinglist_size')

    class Meta:
        model = MerchantPoint
        fields = ('id', 'name', 'area', 'district', 'isopen', 'position', 'waitingListSize' )

    def get_waitinglist_size(self, merchantPoint):
        waitingListSize = merchantPoint.waitingline_set.filter(wasserved=False).count()
        return waitingListSize



class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('title', 'content', 'customernumber')



class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('type', 'amount', 'expectedvalidationdate')

class TransactionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'date', 'expectedvalidationdate', 'type', 'amount', 'customernumber',
                  'beneficiarynumber', 'otp', 'wasvalidatedbymerchant', 'wasvalidatedbycustomer')
