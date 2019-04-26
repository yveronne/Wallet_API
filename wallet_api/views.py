from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import get_user_model
from rest_framework import generics, mixins, status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsMerchantOrReadOnly

from .serializers import *

class TownsList(generics.ListAPIView):
    queryset = Town.objects.order_by('name')
    serializer_class = TownSerializer
    permission_classes = [AllowAny]


class MerchantPointsList(mixins.ListModelMixin, generics.GenericAPIView):
    def get_queryset(self):
        queryset = MerchantPoint.objects.filter(district__townname__name__icontains=self.args[0], isopen=True)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, *kwargs)

    serializer_class = MerchantPointSerializer
    permission_classes = [AllowAny]



class OpenOrCloseMerchantPoint(generics.UpdateAPIView): #todo logs
    def get_queryset(self):
        queryset = MerchantPoint.objects.all()
        return queryset

    serializer_class = MerchantPointSerializer
    permission_classes = [IsAuthenticated, IsMerchantOrReadOnly]



class CommentCreation(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        customer = get_object_or_404(Customer, phonenumber=self.request.data.get('customernumber'))
        merchant_point = get_object_or_404(MerchantPoint, id=self.request.data.get('merchantpointid')) #todo customize error messages
        return serializer.save(customernumber=customer, merchantpoint=merchant_point)



class WaitingLineView(generics.ListCreateAPIView):
    serializer_class = WaitingLineSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = WaitingLine.objects.filter(merchantpoint=self.args[0], wasserved=False)
        return queryset


    # def perform_create(self, serializer): #todo il est déjà dans la file d'attente et pas encore servi
        # merchant_point = get_object_or_404(MerchantPoint, id=self.args[0])
        # customer = get_object_or_404(Customer, phonenumber=self.request.data.get('customernumber'))
        # secret = self.request.data.get('secret')
        # if check_password(secret, customer.secret):
        #     return serializer.save(customernumber=customer, merchantpoint=merchant_point, wasserved=False)
        # else:
        #     content = {'error' : 'Le mot de passe entré est erroné'}
        #     return Response(content, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = WaitingLineSerializer(data=request.data)
        merchant_point = get_object_or_404(MerchantPoint, id=self.args[0])
        customer = get_object_or_404(Customer, phonenumber=self.request.data.get('customernumber'))
        if serializer.is_valid():
            if check_password(self.request.data.get('secret'), customer.secret):
                serializer.save(customernumber=customer, merchantpoint=merchant_point, wasserved=False)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                content = {'error': 'Le mot de passe entré est erroné'}
                return Response(content, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#todo ne pas oublier de retirer les espaces du secret au niveau du mot de passe (le secret)
#todo rôles (le marchand qui peut consulter sa liste doit être authentifié; ce n'est pas le cas pour le client qui crée


class TransactionView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Transaction.objects.filter(merchantpoint=self.args[0], isvalidated=False)
        return queryset


class LogoutUserAPIView(APIView):
    queryset = get_user_model().objects.all()

    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class CustomerCreation(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        hashedSecret = make_password(self.request.data.get('secret'))
        return serializer.save(secret=hashedSecret)
