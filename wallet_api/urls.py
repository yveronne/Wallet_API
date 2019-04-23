from django.urls import path, re_path
# from rest_framework.urlpatterns import format_suffix_patterns
from wallet_api import views

urlpatterns = [
    path('towns/', views.TownsList.as_view()),
    re_path('merchantpoints/([\w]+)/$', views.MerchantPointsList.as_view())
]

# urlpatterns = format_suffix_patterns(urlpatterns)
