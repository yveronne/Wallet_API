from rest_framework import permissions

class IsMerchantOrReadOnly(permissions.BasePermission):
    # Est-ce que c'est le marchand du point marchand ?

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.merchant.user == request.user