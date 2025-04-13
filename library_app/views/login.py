from rest_framework.generics import GenericAPIView
from django.db.models import Q
from django.core.cache import cache
from utility.utils import generate_token, get_login_response
from utility.response import ApiResponse
from utility.constants import MESSAGES, STATUS_ACTIVE, STATUS_INACTIVE  
from django.conf import settings

"""serializer"""
from ..serializers.login_serializer import LoginSerializer

"""Model"""
from ..models import User

"""swagger"""
from ..swagger.login_logout_swagger import swagger_auto_schema


class LoginViewSet(GenericAPIView, ApiResponse):
    serializer_class = LoginSerializer

    @swagger_auto_schema
    def post(self, request, *args, **kwargs):
        """
        API to get logged In.
        """
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            if not username or not password:
                return ApiResponse.response_bad_request(self, message=MESSAGES['username_password_required'])

            # Check cache first for failed attempts
            cache_key = f"login_attempts_{username}"
            failed_attempts = cache.get(cache_key, 0)
            
            if failed_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                return ApiResponse.response_unauthorized(self, message="Too many failed attempts. Please try again later.")

            try:
                user = User.objects.only('id', 'username', 'email', 'status', 'password').get(
                    Q(username=username) | Q(email=username)
                )
                
                if not user.check_password(password):
                    cache.set(cache_key, failed_attempts + 1, timeout=settings.LOGIN_ATTEMPT_TIMEOUT)
                    return ApiResponse.response_unauthorized(self, message=MESSAGES['invalid_username_and_password'])

            except User.DoesNotExist:
                return ApiResponse.response_unauthorized(self, message=MESSAGES['username_not_exist'])

            if user.status == STATUS_INACTIVE:
                return ApiResponse.response_bad_request(self, message=MESSAGES['user_inactive'])
            elif user.status != STATUS_ACTIVE:
                return ApiResponse.response_bad_request(self, message=MESSAGES['user_deleted'])

            cache.delete(cache_key)
            
            token = generate_token(request, user)
            resp_dict = get_login_response(user, token)
            resp_dict["token"] = token
            
            return ApiResponse.response_ok(self, data=resp_dict, message="Login successful")
        
        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=str(e))
