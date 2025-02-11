from django.urls import path

from .views import GetSpecializationsView, GetCourseView

app_name = "education"

urlpatterns = [
    path('get_specializations/', GetSpecializationsView.as_view(), name="get_specializations"),
    path('get_courses/', GetCourseView.as_view(), name="get_courses"),
]
