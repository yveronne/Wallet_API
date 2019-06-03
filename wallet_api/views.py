from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import get_user_model
from rest_framework import generics, mixins, status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsMerchantOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from datetime import datetime, timedelta

from .serializers import *
from .messages import sendOtp, sendTransactionSMS

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
            return Response({"error" : "Ce numéro de téléphone n'existe pas"}, status=status.HTTP_404_NOT_FOUND)
        try:
            merchant_point = MerchantPoint.objects.get(id=self.request.data.get('merchantpointid'))
        except MerchantPoint.DoesNotExist:
            return Response({"error" : "Ce point marchand n'existe pas"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customernumber=customer, merchantpoint=merchant_point)
            content = serializer.data
            content["message"] = "Votre commentaire a bien été envoyé. Merci."
            return Response(content, status=status.HTTP_201_CREATED)
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
            return Response({"error" : "Ce numéro de téléphone n'existe pas"}, status=status.HTTP_404_NOT_FOUND)

        try:
            merchant_point = MerchantPoint.objects.get(id=self.args[0])
        except MerchantPoint.DoesNotExist:
            return Response({"error" : "Ce point marchand n'existe pas"}, status=status.HTTP_404_NOT_FOUND)

        serializer = WaitingLineSerializer(data=request.data)
        if serializer.is_valid():
            if check_password(self.request.data.get('secret').replace(" ",""), customer.secret):
                serializer.save(customernumber=customer, merchantpoint=merchant_point, wasserved=False)
                content = serializer.data
                content["message"] = "Vous avez bien été inséré(e) dans la file d'attente."
                return Response(content, status=status.HTTP_201_CREATED)
            else:
                return Response({"error" : "Le mot de passe entré est erroné"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WaitingLineServe(generics.UpdateAPIView):

    serializer_class = WaitingLineUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = WaitingLine.objects.all()
        return queryset



class TransactionView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionListSerializer

    def get_queryset(self):
        queryset = Transaction.objects.filter(merchantpoint=self.args[0], isvalidated=False).order_by('expectedvalidationdate').reverse()
        return queryset


class LoginUserAPIView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        try:
            merchant = Merchant.objects.get(user=user)
        except Merchant.DoesNotExist:
            return Response({"error" : "Ce compte n'est pas celui d'un marchand"}, status=status.HTTP_404_NOT_FOUND)
        try:
            merchantPoint = MerchantPoint.objects.get(merchant=merchant)
            merchantPoint.isopen = True
            merchantPoint.save()
        except MerchantPoint.DoesNotExist:
            return  Response({"error" : "Ce compte n'est associé à aucun point marchant"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"token": token.key, "merchantPointID" : merchantPoint.id})


class LogoutUserAPIView(APIView):
    queryset = get_user_model().objects.all()

    def get(self, request, format=None):
        request.user.auth_token.delete()
        try:
            merchant = Merchant.objects.get(user=request.user)
        except Merchant.DoesNotExist:
            return Response({"error" : "Ce compte n'est pas celui d'un marchand"}, status=status.HTTP_404_NOT_FOUND)
        try:
            merchantPoint = MerchantPoint.objects.get(merchant=merchant)
            merchantPoint.isopen = False
            merchantPoint.save()
        except MerchantPoint.DoesNotExist:
            return Response({"error": "Ce compte n'est associé à aucun point marchant"}, status=status.HTTP_404_NOT_FOUND)
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
        number = self.request.data.get('customerNumber').replace(" ", "")

        #Calculating expiration date of the otp (expected validation date + 1 hour)
        expectie = datetime.strptime(expectedDate, "%Y-%m-%d %H:%M:%S")
        expirie = expectie + timedelta(hours=1)

        try:
            merchantPoint = MerchantPoint.objects.get(id=merchantPoint)
        except MerchantPoint.DoesNotExist:
            return Response({"error" : "Ce point marchand n'existe pas"}, status=status.HTTP_404_NOT_FOUND)

        if transaction_type == 'Depot':
            beneficiaryNumber = self.request.data.get('beneficiaryNumber').replace(" ","")
            try:
                beneficiary = Customer.objects.get(phonenumber=beneficiaryNumber)
            except Customer.DoesNotExist:
                return Response({"error" : "Le numéro du bénéficiaire entré est introuvable"}, status=status.HTTP_404_NOT_FOUND)

            serializer = TransactionSerializer(data=request.data)
            if serializer.is_valid():
                #Saving OTP
                while True:
                    # Generating OTP
                    code = self.generateOtp()
                    try:
                        otpie = Otp.objects.get(code=code)
                        if otpie.wasverified == True or (otpie.wasverified == False and otpie.expirationdate < datetime.now()):
                            otpie.expirationdate = expirie
                            otpie.wasverified = False
                            otpie.save()
                            break
                        elif otpie.wasverified == False and otpie.expirationdate >= datetime.now():
                            continue
                    except Otp.DoesNotExist:
                        otpie = Otp(code=code, expirationdate=expirie)
                        otpie.save()
                        break

                #Sending Otp
                message = sendOtp(otpie.code, number, expirie.strftime("%d-%b-%Y %H:%M:%S"))
                if message != "queued":
                    otpie.delete()
                    return Response({"error" : "Une erreur est survenue. Veuillez réessayer"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    #Saving transaction
                    serializer.save(type='Depot', beneficiarynumber=beneficiary, merchantpoint=merchantPoint, amount=amount,
                                    expectedvalidationdate=expectedDate, otp=otpie, customernumber=number)
                    return Response({"message" : "Transaction initiée avec succès. Le code de confirmation sera envoyé par SMS au " + number}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif (transaction_type == 'Retrait'):
            secret = self.request.data.get('secret').replace(" ", "")

            try:
                customer = Customer.objects.get(phonenumber=number)
            except Customer.DoesNotExist:
                return Response({"error" : "Le numéro de client entré est introuvable"}, status=status.HTTP_404_NOT_FOUND)

            serializer = TransactionSerializer(data=request.data)
            if(serializer.is_valid()):
                if check_password(secret, customer.secret):

                    if customer.balance > float(amount):
                        # Saving OTP
                        while True:
                            # Generating OTP
                            code = self.generateOtp()
                            try:
                                otpie = Otp.objects.get(code=code)
                                if otpie.wasverified == True:
                                    otpie.expirationdate = expirie
                                    otpie.wasverified = False
                                    otpie.save()
                                    break
                                elif otpie.wasverified == False:
                                    continue
                            except Otp.DoesNotExist:
                                otpie = Otp(code=code, expirationdate=expirie)
                                otpie.save()
                                break

                        # Sending Otp
                        message = sendOtp(otpie.code, number, expirie.strftime("%d-%b-%Y %H:%M:%S"))
                        if message != "queued":
                            otpie.delete()
                            return Response({ "error" : "Une erreur est survenue. Veuillez réessayer"},
                                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        else:
                            # Saving transaction
                            serializer.save(type='Retrait', merchantpoint=merchantPoint,
                                            amount=amount, customernumber=customer.phonenumber,
                                            expectedvalidationdate=expectedDate, otp=otpie)

                            return Response({"message" : "Transaction initiée avec succès. Le code de confirmation sera envoyé par SMS au " + number}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"error": "Solde insuffisant. Cette transaction ne peut être initiée"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    return Response({"error" : "Le code secret entré est erroné"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



        elif (transaction_type == 'Paiement'):
            secret = self.request.data.get('secret').replace(" ", "")

            try:
                customer = Customer.objects.get(phonenumber=number)
            except Customer.DoesNotExist:
                return Response({"error" : "Le numéro de client entré est introuvable"}, status=status.HTTP_404_NOT_FOUND)

            serializer = TransactionSerializer(data=request.data)
            if (serializer.is_valid()):
                if check_password(secret, customer.secret):

                    if customer.balance > float(amount):
                        # Saving OTP
                        while True:
                            # Generating OTP
                            code = self.generateOtp()
                            try:
                                otpie = Otp.objects.get(code=code)
                                if otpie.wasverified == True:
                                    otpie.expirationdate = expirie
                                    otpie.wasverified = False
                                    otpie.save()
                                    break
                                elif otpie.wasverified == False:
                                    continue
                            except Otp.DoesNotExist:
                                otpie = Otp(code=code, expirationdate=expirie)
                                otpie.save()
                                break

                        # Sending Otp
                        message = sendOtp(otpie.code, number, expirie.strftime("%d-%b-%Y %H:%M:%S"))
                        if message != "queued":
                            otpie.delete()
                            return Response({"error" : "Une erreur est survenue. Veuillez réessayer"},
                                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        else:
                            # Saving transaction
                            serializer.save(type='Paiement', merchantpoint=merchantPoint,
                                            amount=amount, customernumber=customer.phonenumber,
                                            expectedvalidationdate=expectedDate, otp=otpie)
                            return Response({"message" : "Transaction initiée avec succès. Le code de confirmation sera envoyé par SMS au " + number,
                                              "montant" : amount, "code" : otpie.code}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"error" : "Solde insuffisant. Cette transaction ne peut être initiée"}, status=status.HTTP_406_NOT_ACCEPTABLE)

                else:
                    return Response({"error": "Le code secret entré est erroné"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def validateTransaction(request):
    codie = request.data.get('code')
    try:
        otpie = Otp.objects.get(code=codie)
        if otpie.wasverified == True:
            return Response({"message" : "Ce code a déjà été vérifié"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        elif  otpie.expirationdate < datetime.now():
            return Response({"error": "Ce code a expiré"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        else:
            try:
                transaction = Transaction.objects.get(otp=otpie, isvalidated=False)

                if transaction.type == "Depot":

                    try:
                        beneficiary = Customer.objects.get(phonenumber=transaction.beneficiarynumber.phonenumber)
                        oldBalance = beneficiary.balance
                        beneficiary.balance = oldBalance + transaction.amount
                        beneficiary.save()

                        transaction.isvalidated = True
                        transaction.validationdate = datetime.now()
                        transaction.save()

                        otpie.wasverified = True
                        otpie.save()

                        sendTransactionSMS(beneficiary.phonenumber, "dépôt",
                                           transaction.date.strftime("%d-%b-%Y %H:%M:%S"),
                                           transaction.expectedvalidationdate.strftime("%d-%b-%Y %H:%M:%S"),
                                           transaction.validationdate.strftime("%d-%b-%Y %H:%M:%S"),
                                           str(beneficiary.balance))

                        return Response({"message" : "La transaction a bien été validée."}, status=status.HTTP_200_OK)

                    except Customer.DoesNotExist:
                        return Response({"error": "Le bénéficiaire n'existe pas"}, status=status.HTTP_404_NOT_FOUND)


                elif transaction.type == "Retrait":

                    try:
                        merchantpoint = MerchantPoint.objects.get(id=transaction.merchantpoint_id)

                        try:
                            customer = Customer.objects.get(phonenumber=transaction.customernumber)
                            amount = transaction.amount
                            oldStoreBalance = merchantpoint.balance
                            oldCustomerBalance = customer.balance

                            if oldCustomerBalance < amount:
                                return Response({"error": "Transaction échouée. Solde insuffisant"},
                                                status=status.HTTP_406_NOT_ACCEPTABLE)
                            else:
                                customer.balance = oldCustomerBalance - amount
                                merchantpoint.balance = oldStoreBalance + amount
                                customer.save()
                                merchantpoint.save()

                                transaction.isvalidated = True
                                transaction.validationdate = datetime.now()
                                transaction.save()

                                otpie.wasverified = True
                                otpie.save()

                                sendTransactionSMS(customer.phonenumber, "retrait",
                                                   transaction.date.strftime("%d-%b-%Y %H:%M:%S"),
                                                   transaction.expectedvalidationdate.strftime("%d-%b-%Y %H:%M:%S"),
                                                   transaction.validationdate.strftime("%d-%b-%Y %H:%M:%S"),
                                                   str(customer.balance))

                                return Response({"message" : "La transaction a bien été validée."}, status=status.HTTP_200_OK)

                        except Customer.DoesNotExist:
                            return Response({"error": "Le client n'existe pas"}, status=status.HTTP_404_NOT_FOUND)


                    except MerchantPoint.DoesNotExist:
                        return Response({"error": "Le point marchand n'existe pas"}, status=status.HTTP_404_NOT_FOUND)


                elif transaction.type == "Paiement":

                    try:
                        merchantpoint = MerchantPoint.objects.get(id=transaction.merchantpoint_id)

                        try:
                            customer = Customer.objects.get(phonenumber=transaction.customernumber)
                            amount = transaction.amount
                            oldStoreBalance = merchantpoint.balance
                            oldCustomerBalance = customer.balance

                            if oldCustomerBalance < amount:
                                return Response({"error":"Transaction échouée. Solde insuffisant"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                            else :
                                customer.balance = oldCustomerBalance - amount
                                merchantpoint.balance = oldStoreBalance + amount
                                customer.save()
                                merchantpoint.save()

                                transaction.isvalidated = True
                                transaction.validationdate = datetime.now()
                                transaction.save()

                                otpie.wasverified = True
                                otpie.save()

                                sendTransactionSMS(customer.phonenumber, "paiement",
                                                   transaction.date.strftime("%d-%b-%Y %H:%M:%S"),
                                                   transaction.expectedvalidationdate.strftime("%d-%b-%Y %H:%M:%S"),
                                                   transaction.validationdate.strftime("%d-%b-%Y %H:%M:%S"),
                                                   str(customer.balance))

                                return Response({"message" : "La transaction a bien été validée"}, status=status.HTTP_200_OK)

                        except Customer.DoesNotExist:
                            return Response({"error" : "Le numéro de client entré est introuvable"}, status=status.HTTP_404_NOT_FOUND)

                    except MerchantPoint.DoesNotExist:
                        return Response({"error": "Le point marchand n'existe pas"}, status=status.HTTP_404_NOT_FOUND)

                return Response({"message": "La transaction a bien été validée"}, status=status.HTTP_200_OK)

            except Transaction.DoesNotExist:
                return Response({"error": "La transaction sollicitée n'existe pas"}, status=status.HTTP_404_NOT_FOUND)


    except Otp.DoesNotExist:
        return Response({"error" : "Le code fourni n'existe pas"}, status=status.HTTP_404_NOT_FOUND)


