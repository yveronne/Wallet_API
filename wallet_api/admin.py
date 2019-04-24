from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import *

admin.site.register(Town)
admin.site.register(District)
admin.site.register(Merchant)
admin.site.register(Customer)
admin.site.register(Comment)

@admin.register(MerchantPoint)
class MerchantPoint(OSMGeoAdmin):
    list_display = ('name', 'area', 'position', 'district')
