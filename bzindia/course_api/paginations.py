from rest_framework.pagination import PageNumberPagination

class CoursePagination(PageNumberPagination):
    page_size = 9

class CourseMultipagePagination(PageNumberPagination):
    page_size = 3