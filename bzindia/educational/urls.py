from django.urls import path

from .views import GetSpecializationsView

app_name = "education"

urlpatterns = [
    path('get_specializations/', GetSpecializationsView.as_view(), name="get_specializations"),
]
