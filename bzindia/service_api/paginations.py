from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

class ServiceDetailPagination(LimitOffsetPagination):
    default_limit = 9
    max_limit = 50 

class ServiceMultipagePagination(PageNumberPagination):
    page_size = 3