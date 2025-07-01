from rest_framework.pagination import PageNumberPagination

class ItemPagination(PageNumberPagination):
    page_size = 12

class MetaTagPagination(PageNumberPagination):
    page_size = 12