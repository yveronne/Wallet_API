from django.conf.urls import url
from django.urls import path, re_path
from rest_framework.authtoken.views import obtain_auth_token

from wallet_api import views

urlpatterns = [
    path('towns', views.TownsList.as_view()),   #Liste des villes
    re_path('towns/([\w]+)/merchantpoints', views.MerchantPointsList.as_view()),    #Liste des points marchands ouverts de la ville
    path('merchantpoints/<int:pk>', views.OpenOrCloseMerchantPoint.as_view()),      #Ouvrir ou fermer un point marchand
    re_path('merchantpoints/([\d]+)/waitingline', views.WaitingLineView.as_view()),
    re_path('merchantpoints/([\d]+)/transactions', views.TransactionView.as_view()),
    path('comments', views.CommentCreation.as_view()),
    url(r'^merchant/login$', views.LoginUserAPIView.as_view(), name='auth_user_login'),
    url(r'^merchant/logout$', views.LogoutUserAPIView.as_view(), name='auth_user_logout'),
    path('customers', views.CustomerCreation.as_view()),
    path('waitinglines/<int:pk>', views.WaitingLineServe.as_view()),
    path('transactions', views.TransactionInitiation.as_view()),
    path('otp/confirmwithdrawal', views.customerValidation),
    path('transactions/confirm', views.validateTransaction),
    path('transactions/<int:pk>', views.TransactionDetail.as_view())
]

