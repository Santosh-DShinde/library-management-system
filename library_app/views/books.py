import operator
import traceback
from utility.utils import generate_token, get_login_response, get_serielizer_error, get_pagination_resp, transform_list
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.permissions import IsAuthenticated
from ..serializers.login_serializer import LoginSerializer
from utility.utils import MultipleFieldPKModelMixin, CreateRetrieveUpdateViewSet
from utility.response import ApiResponse
from django.db import transaction
from datetime import datetime
from django.db.models import Q
from functools import reduce
from simple_search import search_filter


from ..models import Books

from ..serializers.books_serializer import BooksSerializer

class BooksView(MultipleFieldPKModelMixin, CreateRetrieveUpdateViewSet, ApiResponse):
    # authentication_classes = [OAuth2Authentication]
    # permission_classes = [IsAuthenticated]
    model_class = Books.objects
    serializer_class = BooksSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            get_id = self.kwargs.get('id')
            instance = self.model_class.filter(id = get_id).first()

            if not instance:
                return ApiResponse.response_bad_request(self, message="Books details not present.")
            
            resp_dict = self.transform_single(instance)
            
            return ApiResponse.response_ok(self, data=resp_dict)
            
        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])
            
    @transaction.atomic()
    def create(self, request, *args, **kwrgs):
        try:
            sp1 = transaction.savepoint()
            req_data = request.data.copy()
            title = req_data.get('title')
            author = req_data.get('author')
            isbn = req_data.get('isbn')

            if not title or not author:
                return ApiResponse.response_bad_request(self, message="Book title and Author are mandetory.")

            if check_is_exists := self.model_class.filter(title = title, author=author).first():
                return ApiResponse.response_bad_request(self, message="Book is already exists with Author.")
            
            if check_isbn_exists := self.model_class.filter(isbn = isbn).exists():
                return ApiResponse.response_bad_request(self, message="Book is already exists with given ISBN number.")
            
            serializer = self.serializer_class(data=req_data)

            if not serializer.is_valid():
                serializer_error = get_serielizer_error(serializer)
                transaction.savepoint_rollback(sp1)
                return ApiResponse.response_bad_request(self, message=serializer_error)
            
            serializer.save()
            return ApiResponse.response_created(self, message="Books details stored successfully.")

        except Exception as e:
            print("tracenback", traceback.format_exc())
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])
    
    @transaction.atomic()
    def update(self, request, *args, **kwrgs):
        try:
            sp1 = transaction.savepoint()
            req_data = request.data.copy()
            title = req_data.get('title')
            author = req_data.get('author')
            isbn = req_data.get('isbn')
            get_id = self.kwargs.get('id')

            instance = self.model_class.get(id = get_id)

            if not instance:
                return ApiResponse.response_not_found(self, message="Books details not found.")

            if check_is_exists := self.model_class.filter(title = title, author=author).exclude(id = instance.id).exists():
                return ApiResponse.response_bad_request(self, message="Book is already exists with Author.")
            
            if check_isbn_exists := self.model_class.filter(isbn = isbn).exclude(id = instance.id).exists():
                return ApiResponse.response_bad_request(self, message="Book is already exists with given ISBN number.")

            serializer = self.serializer_class(instance, data=req_data, partial = True)

            if not serializer.is_valid():
                serializer_error = get_serielizer_error(serializer)
                transaction.savepoint_rollback(sp1)
                return ApiResponse.response_bad_request(self, message=serializer_error)
            
            return ApiResponse.response_ok(self, message="Books details updated successfully.")

        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])
    
    def list(self, request, *args, **kwrgs):
        try:
            where_array = request.query_params
            sort_by = where_array.get('sort_by') if where_array.get('sort_by') else "id"
            sort_direction = where_array.get('sort_direction') if where_array.get('sort_direction') else "ascending"
            if sort_direction == "descending":
                sort_by = "-" + sort_by

            obj_list = []

            if where_array.get('title'):
                obj_list.append(('title',where_array.get('title')))
            
            if where_array.get('author'):
                obj_list.append(('author',where_array.get('author')))
            
            if where_array.get('isbn'):
                obj_list.append(('isbn',where_array.get('isbn')))
            
            if where_array.get('copies_available'):
                obj_list.append(('copies_available',where_array.get('copies_available')))

            start_date = where_array.get("start_date")
            end_date = where_array.get("end_date")
            if start_date and end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                end_date = datetime.combine(end_date, datetime.max.time())
                obj_list.append(["created_at__range", [start_date, end_date]])

            elif start_date:
                obj_list.append(["created_at__gte", start_date])
    
            elif end_date:
                obj_list.append(["created_at__lte", end_date])
            
            q_list = [Q(x) for x in obj_list]

            if q_list:
                queryset = self.model_class.filter(reduce(operator.and_, q_list)).order_by(sort_by)
            else:
                queryset = self.model_class.order_by(sort_by)
            
            """Search for keyword"""
            if where_array.get("keyword"):
                queryset = queryset.filter(search_filter(self.search_fields, where_array.get("keyword")))

            resp_data = get_pagination_resp(queryset, request)
            response_data = transform_list(self, resp_data.get('data'))

            return ApiResponse.response_ok(self, data=response_data, paginator=resp_data.get("paginator"))
            
        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])
    
    def delete(self, request, *args, **kwrgs):
        try:
            get_id = self.kwargs.get('id')
            instance = self.model_class.filter(id = get_id).first()

            if not instance:
                return ApiResponse.response_bad_request(self, message="Books details not present.")
            
            instance.delete()

        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])
    
    def transform_single(self, instance):
        resp_dict = dict()
        if instance:
            resp_dict['id'] = instance.id
            resp_dict['title'] = instance.title
            resp_dict['author'] = instance.author
                
        return resp_dict
