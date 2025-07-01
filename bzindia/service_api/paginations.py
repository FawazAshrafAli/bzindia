from rest_framework.pagination import PageNumberPagination

class ServiceDetailPagination(PageNumberPagination):
    page_size = 9

class ServiceMultipagePagination(PageNumberPagination):
    page_size = 3