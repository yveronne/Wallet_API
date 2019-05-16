from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import *

admin.site.register(Town)
admin.site.register(Merchant)

class CustomerAdmin(admin.ModelAdmin):
    exclude = ['secret']
    search_fields = ['lastname', 'phonenumber']
    list_display = ['phonenumber', 'full_name', 'gender', 'cninumber']
admin.site.register(Customer, CustomerAdmin)

class CommentAdmin(admin.ModelAdmin):
    search_fields = ['merchantpoint']
    list_select_related = ('merchantpoint', )
    list_display = ['date', 'title', 'content', 'merchantpoint']
admin.site.register(Comment, CommentAdmin)

class CommentInLine(admin.TabularInline):
    model = Comment


class TransactionAdmin(admin.ModelAdmin):
    search_fields = ['type']
    list_select_related = ('merchantpoint', )
    list_display = ['type', 'amount', 'expectedvalidationdate', 'beneficiarynumber', 'merchantpoint']
admin.site.register(Transaction, TransactionAdmin)


class TransactionInLine(admin.TabularInline):
    model = Transaction

@admin.register(MerchantPoint)
class MerchantPointAdmin(OSMGeoAdmin):
    list_display = ('name', 'area', 'position', 'district')
    list_select_related = ('district', )
    inlines = [
        TransactionInLine, CommentInLine,
    ]

class MerchantPointInline(admin.TabularInline):
    model = MerchantPoint

class DistrictAdmin(admin.ModelAdmin):
    search_fields = ['name', 'townname']
    list_select_related = ('townname', )
    list_display = ['name', 'townname']
    inlines = [
        MerchantPointInline,
    ]
admin.site.register(District, DistrictAdmin)




