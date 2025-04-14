# Django
from django.core.cache import cache

# Django OAuth Toolkit
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.models import AccessToken

# Django REST Framework
from django.conf import settings
from rest_framework.generics import GenericAPIView

# Local
from ..serializers.login_serializer import LoginSerializer
from library_app.swagger.login_logout_swagger import swagger_auto_schema
from utility.response import ApiResponse


class LogoutView(GenericAPIView, ApiResponse):
    serializer_class = LoginSerializer
    authentication_classes = [OAuth2Authentication, ]

    @swagger_auto_schema
    def get(self, request, *args, **kwargs):
        """
        API to logout user.
        """
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                
                cache_key = f"blacklisted_token_{token}"
                cache.set(cache_key, True, timeout=settings.BLACKLIST_TOKEN_TIMEOUT)
                
                # Revoke the token
                try:
                    access_token = AccessToken.objects.get(token=token)
                    access_token.delete()
                except AccessToken.DoesNotExist:
                    return ApiResponse.response_ok(self, message="You have already logged out. Please login again.")

                return ApiResponse.response_ok(self, message="Logout successful")
            else:
                return ApiResponse.response_unauthorized(self, message="Invalid authorization header")
                
        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])
