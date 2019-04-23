from rest_framework import generics
from .models import *
from .serializers import *

class TownsList(generics.ListAPIView):
    queryset = Town.objects.order_by('name')
    serializer_class = TownSerializer


class MerchantPointsList(generics.ListAPIView):
    def get_queryset(self):
        queryset = MerchantPoint.objects.filter(district__townname__name__icontains=self.args[0])
        return queryset
    serializer_class = MerchantPointSerializer



