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



class OpenOrCloseMerchantPoint(generics.UpdateAPIView):
    def get_queryset(self):
        queryset = MerchantPoint.objects.all()
        return queryset

    serializer_class = MerchantPointSerializer
    permission_classes = [IsAuthenticated, IsMerchantOrReadOnly]



class CommentCreation(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            customer = Customer.objects.get(phonenumber=self.request.data.get('customernumber'))
        except Customer.DoesNotExist:
            content = "Ce numéro de téléphone n'existe pas"
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        try:
            merchant_point = MerchantPoint.objects.get(id=self.request.data.get('merchantpointid'))
        except MerchantPoint.DoesNotExist:
            content = "Ce point marchand n'existe pas"
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customernumber=customer, merchantpoint=merchant_point)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class WaitingLineView(generics.ListCreateAPIView):
    serializer_class = WaitingLineSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = WaitingLine.objects.filter(merchantpoint=self.args[0], wasserved=False).order_by('date').reverse()
        return queryset


    # def perform_create(self, serializer): #todo il est déjà dans la file d'attente et pas encore servi
    #todo Cas où un client qui n'a pas de compte Wallet vient faire le dépôt

    def create(self, request, *args, **kwargs):
        try:
            customer = Customer.objects.get(phonenumber=self.request.data.get('customernumber'))
        except Customer.DoesNotExist:
            content = "Ce numéro de téléphone n'existe pas"
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        try:
            merchant_point = MerchantPoint.objects.get(id=self.args[0])
        except MerchantPoint.DoesNotExist:
            content = "Ce point marchand n'existe pas"
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        serializer = WaitingLineSerializer(data=request.data)
        if serializer.is_valid():
            if check_password(self.request.data.get('secret').replace(" ",""), customer.secret):
                serializer.save(customernumber=customer, merchantpoint=merchant_point, wasserved=False)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                content = "Le mot de passe entré est erroné"
                return Response(content, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WaitingLineServe(generics.UpdateAPIView):

    serializer_class = WaitingLineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = WaitingLine.objects.all()
        return queryset



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


class TransactionInitiation(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    permission_classes = [AllowAny]
    serializer_class = TransactionSerializer

    def generateOtp(self):
        from random import randint
        # OTP generation
        otp = ""
        for x in range(7):
            digit = randint(1, 9)
            otp += str(digit)
        return otp



    def create(self, request, *args, **kwargs):
        transaction_type = self.request.data.get('type')
        amount = self.request.data.get('amount')
        merchantPoint = self.request.data.get('merchantPointID')
        expectedDate = self.request.data.get('expectedvalidationdate')

        #Calculating expiration date of the otp (expected validation date + 1 hour)
        from datetime import datetime, timedelta
        expectie = datetime.strptime(expectedDate, "%Y-%m-%d %H:%M:%S")
        expirie = expectie + timedelta(hours=1)

        try:
            merchantPoint = MerchantPoint.objects.get(id=merchantPoint)
        except MerchantPoint.DoesNotExist:
            content = "Ce point marchand n'existe pas"
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        if transaction_type == 'Depot':
            beneficiaryNumber = self.request.data.get('beneficiaryNumber')
            try:
                beneficiary = Customer.objects.get(phonenumber=beneficiaryNumber).replace(" ","")
            except Customer.DoesNotExist:
                content = "Le numéro du bénéficiaire entré est introuvable"
                return Response(content, status=status.HTTP_404_NOT_FOUND)

            serializer = TransactionSerializer(data=request.data)
            if serializer.is_valid():
                #Saving OTP
                while True:
                    # Generating OTP
                    code = self.generateOtp()
                    try:
                        otpie = Otp.objects.get(code=code)
                        if otpie.wasverified == True:
                            otpie.expirationdate = expirie
                            otpie.save()
                            break
                        elif otpie.wasverified == False:
                            continue
                    except Otp.DoesNotExist:
                        otpie = Otp(code=code, expirationdate=expirie)
                        otpie.save()
                        break

                serializer.save(type='Depot', beneficiarynumber=beneficiary, merchantpoint=merchantPoint, amount=amount,
                                expectedvalidationdate=expectedDate, otp=otpie)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif (transaction_type == 'Retrait'):
            secret = self.request.data.get('secret').replace(" ", "")
            number = self.request.data.get('customerNumber').replace(" ","")

            try:
                customer = Customer.objects.get(phonenumber=number)
            except Customer.DoesNotExist:
                content = "Le numéro de client entré est introuvable"
                return Response(content, status=status.HTTP_404_NOT_FOUND)

            serializer = TransactionSerializer(data=request.data)
            if(serializer.is_valid()):
                if check_password(secret, customer.secret):

                    # Saving OTP
                    while True:
                        # Generating OTP
                        code = self.generateOtp()
                        try:
                            otpie = Otp.objects.get(code=code)
                            if otpie.wasverified == True:
                                otpie.expirationdate = expirie
                                otpie.save()
                                break
                            elif otpie.wasverified == False:
                                continue
                        except Otp.DoesNotExist:
                            otpie = Otp(code=code, expirationdate=expirie)
                            otpie.save()
                            break
                    serializer.save(type='Retrait', merchantpoint=merchantPoint,
                                    amount=amount, customernumber=customer.phonenumber,
                                    expectedvalidationdate=expectedDate, otp=otpie)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    content = "Le mot de passe entré est erroné"
                    return Response(content, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



        elif (transaction_type == 'Paiement'):
            secret = self.request.data.get('secret').replace(" ", "")
            number = self.request.data.get('customerNumber').replace(" ","")

            try:
                customer = Customer.objects.get(phonenumber=number)
            except Customer.DoesNotExist:
                content = "Le numéro de client entré est introuvable"
                return Response(content, status=status.HTTP_404_NOT_FOUND)

            serializer = TransactionSerializer(data=request.data)
            if (serializer.is_valid()):
                if check_password(secret, customer.secret):

                    # Saving OTP
                    while True:
                        # Generating OTP
                        code = self.generateOtp()
                        try:
                            otpie = Otp.objects.get(code=code)
                            if otpie.wasverified == True:
                                otpie.expirationdate = expirie
                                otpie.save()
                                break
                            elif otpie.wasverified == False:
                                continue
                        except Otp.DoesNotExist:
                            otpie = Otp(code=code, expirationdate=expirie)
                            otpie.save()
                            break
                    serializer.save(type='Paiement', merchantpoint=merchantPoint,
                                    amount=amount, customernumber=customer.phonenumber,
                                    expectedvalidationdate=expectedDate, otp=otpie)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    content = "Le mot de passe entré est erroné"
                    return Response(content, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
