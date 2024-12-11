from utility.utils import generate_token, get_login_response, get_serielizer_error
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.permissions import IsAuthenticated
from ..serializers.login_serializer import LoginSerializer
from utility.utils import MultipleFieldPKModelMixin, CreateRetrieveUpdateViewSet
from utility.response import ApiResponse
from django.db import transaction

from models import Books

from ..serializers.books_serializer import BooksSerializer

class BooksView(MultipleFieldPKModelMixin, CreateRetrieveUpdateViewSet, ApiResponse):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    model_class = Books.objects
    serializer_class = BooksSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            pass
        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])

    @transaction.atomic()
    def create(self, request, *args, **kwrgs):
        try:
            # sp1 = transaction.savepoint()
            req_data = request.data.copy()
            
            title = req_data.get('title')
            author = req_data.get('author')

            if not title or not author:
                return ApiResponse.response_bad_request(self, message="Book title and Author are mandetory.")

            if check_is_exists := self.model_class.filter(title = title, author=author).first():
                return ApiResponse.response_bad_request(self, message="Book is already exists with Author.")
            
            serializer = self.model_class(data=req_data)

            if not serializer.is_valid():
                serializer_error = get_serielizer_error(serializer)
                return ApiResponse.response_bad_request(self, message=serializer_error)
            
            serializer.save()
            return ApiResponse.response_created(self, message="Books details stored successfully.")

        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])
    
    def update(self, request, *args, **kwrgs):
        try:
            pass
        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])
    
    def list(self, request, *args, **kwrgs):
        try:
            pass
        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])
    
    def list(self, request, *args, **kwrgs):
        try:
            pass
        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])