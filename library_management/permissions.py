from rest_framework.permissions import BasePermission
from django.conf import settings

def is_model_permission(request, code_name):
    try:
        if not request.user.group:
            return False
        permissions = request.user.group.permissions.filter(codename=code_name)
        if permissions:
            return True
        else:
            return False
    except:
        return False

class is_super_admin(BasePermission):
    """
    check for super admin login or not
    """
    def has_permission(self, request, view):
        try:
            return request.user.group_id == settings.GRP_SUPER_ADMIN
        except:
            return False


class is_access(BasePermission):
    def has_permission(self, request, view):
        headers = settings.HEADERS
        # return request.META.get('HTTP_ACCESS_KEY') == headers
        return True