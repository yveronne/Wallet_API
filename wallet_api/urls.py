from django.urls import path, re_path
from wallet_api import views

urlpatterns = [
    path('towns', views.TownsList.as_view()),
    re_path('towns/([\w]+)/merchantpoints', views.MerchantPointsList.as_view()),
    path('merchantpoints/<int:pk>', views.OpenOrCloseMerchantPoint.as_view()),
    path('comments', views.CommentCreation.as_view()),
    re_path('waitinglines/([\d]*)', views.WaitingLineCreation.as_view()),
    path('login', views.login_view)
]

