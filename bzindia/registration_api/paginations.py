from rest_framework.pagination import PageNumberPagination

class RegistrationPagination(PageNumberPagination):
    page_size = 9

class RegistrationMultipagePagination(PageNumberPagination):
    page_size = 3