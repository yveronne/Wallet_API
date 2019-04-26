from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import *

admin.site.register(Town)
admin.site.register(Merchant)
admin.site.register(Comment)

@admin.register(MerchantPoint)
class MerchantPoint(OSMGeoAdmin):
    list_display = ('name', 'area', 'position', 'district')

class DistrictAdmin(admin.ModelAdmin):
    search_fields = ['name', 'townname']
    list_select_related = True
    list_display = ['name', 'townname']
admin.site.register(District, DistrictAdmin)



class CustomerAdmin(admin.ModelAdmin):
    exclude = ['secret']
    search_fields = ['lastname', 'phonenumber']
    list_select_related = True
    list_display = ['phonenumber', 'full_name', 'gender', 'cninumber']
admin.site.register(Customer, CustomerAdmin)

