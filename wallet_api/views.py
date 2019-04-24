from django.contrib.auth import authenticate
from rest_framework import generics, mixins
from django.shortcuts import get_object_or_404

from .models import *
from .serializers import *

class TownsList(generics.ListAPIView):
    queryset = Town.objects.order_by('name')
    serializer_class = TownSerializer


class MerchantPointsList(mixins.ListModelMixin, generics.GenericAPIView):
    def get_queryset(self):
        queryset = MerchantPoint.objects.filter(district__townname__name__icontains=self.args[0])
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, *kwargs)

    serializer_class = MerchantPointSerializer


class OpenOrCloseMerchantPoint(generics.UpdateAPIView):
    def get_queryset(self):
        queryset = MerchantPoint.objects.all()
        return queryset

    serializer_class = MerchantPointSerializer


class CommentCreation(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        customer = get_object_or_404(Customer, phonenumber=self.request.data.get('customernumber'))
        merchant_point = get_object_or_404(MerchantPoint, id=self.request.data.get('merchantpointid')) #todo customize error messages
        return serializer.save(customernumber=customer, merchantpoint=merchant_point)


class WaitingLineCreation(generics.ListCreateAPIView):
    def get_queryset(self):
        queryset = WaitingLine.objects.filter(merchantpoint=self.args[0], wasserved=False)
        return queryset
    serializer_class = WaitingLineSerializer

    def perform_create(self, serializer): #todo il est déjà dans la file d'attente et pas encore servi
        customer = get_object_or_404(Customer, phonenumber=self.request.data.get('customernumber'), secret=self.request.data.get('secret'))
        merchant_point = get_object_or_404(MerchantPoint, id=self.request.data.get('merchantpointid'))
        return serializer.save(customernumber=customer, merchantpoint=merchant_point, wasserved=False)

def login_view(request):
    login = request.POST['login']
    password = request.POST['password']
    user = authenticate(request, username=login, password=password)
    if user is not None:
        login(request, user)
        return "heyyyy"
    else:
        return "haaaa"
