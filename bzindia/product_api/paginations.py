from rest_framework.pagination import PageNumberPagination

class ProductDetailPagination(PageNumberPagination):
    page_size = 6

class ProductMultipagePagination(PageNumberPagination):
    page_size = 3