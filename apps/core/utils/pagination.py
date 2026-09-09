from collections import OrderedDict
from rest_framework.pagination import LimitOffsetPagination as _LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

class SiswaPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

def get_paginated_response(*, pagination_class, serializer_class, queryset, request, view):
    """
    Helper function untuk menjalankan paginasi Django REST Framework
    dan mengembalikan DRF Response secara konsisten.
    """
    paginator = pagination_class()
    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True)
        return Response(
            OrderedDict(
                [
                    ("count", paginator.count),
                    ("next", paginator.get_next_link()),
                    ("previous", paginator.get_previous_link()),
                    ("results", serializer.data),
                ]
            )
        )

    serializer = serializer_class(queryset, many=True)
    return Response(serializer.data)


# 1. Custom Pagination Class
class LimitOffsetPagination(_LimitOffsetPagination):
    default_limit = 10
    max_limit = 50

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )