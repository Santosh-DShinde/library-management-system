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


from ..models import Books, BorrowRequests

from ..serializers.books_serializer import BooksSerializer

class BorrowRequestsView(MultipleFieldPKModelMixin, CreateRetrieveUpdateViewSet, ApiResponse):
    # authentication_classes = [OAuth2Authentication]
    # permission_classes = [IsAuthenticated]
    model_class = BorrowRequests.objects
    serializer_class = BooksSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            get_id = self.kwargs.get('id')
            instance = self.model_class.filter(id = get_id).first()

            if not instance:
                return ApiResponse.response_bad_request(self, message="Borrow request details not present.")
            
            resp_dict = self.transform_single(instance)
            
            return ApiResponse.response_ok(self, data=resp_dict)
            
        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])

    @transaction.atomic()
    def create(self, request, *args, **kwrgs):
        try:
            sp1 = transaction.savepoint()
            req_data = request.data.copy()
            book_id = req_data.get('book')
            user_id = req_data.get('user')
            start_date = req_data.get('start_date')
            end_date = req_data.get('end_date')
            status = req_data.get('status')

            if not user_id or not book_id:
                return ApiResponse.response_bad_request(self, message="Book Id and User Id are mandetory.")

            if check_is_exists := self.model_class.filter(book_id = book_id, user_id=user_id).first():
                return ApiResponse.response_bad_request(self, message="Borrow request is already exists with Provided User.")
            
            serializer = self.serializer_class(data=req_data)

            if not serializer.is_valid():
                serializer_error = get_serielizer_error(serializer)
                transaction.savepoint_rollback(sp1)
                return ApiResponse.response_bad_request(self, message=serializer_error)
            
            serializer.save()
            return ApiResponse.response_created(self, message="Borrow request stored successfully.")

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
            get_id = self.kwargs.get('id')

            instance = self.model_class.get(id = get_id)

            if not instance:
                return ApiResponse.response_not_found(self, message="Borrow request not found.")

            if check_is_exists := self.model_class.filter(title = title, author=author).exclude().exists():
                return ApiResponse.response_bad_request(self, message="Borrow request is already exists with Author.")

            serializer = self.serializer_class(instance, data=req_data, partial = True)

            if not serializer.is_valid():
                serializer_error = get_serielizer_error(serializer)
                transaction.savepoint_rollback(sp1)
                return ApiResponse.response_bad_request(self, message=serializer_error)
            
            return ApiResponse.response_ok(self, message="Borrow request updated successfully.")

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

            start_date = where_array.get("start_date")
            end_date = where_array.get("end_date")
            if start_date and end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                end_date = datetime.combine(end_date, datetime.max.time())
                obj_list.append(["start_date__range", [start_date, end_date]])

            elif start_date:
                obj_list.append(["start_date__gte", start_date])
    
            elif end_date:
                obj_list.append(["start_date__lte", end_date])
            
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
                return ApiResponse.response_bad_request(self, message="Borrow request not present.")
            
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
