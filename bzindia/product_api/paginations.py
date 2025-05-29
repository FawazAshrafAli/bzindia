from rest_framework.pagination import PageNumberPagination

class ProductDetailPagination(PageNumberPagination):
    page_size = 6   