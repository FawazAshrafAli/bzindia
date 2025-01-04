from django.urls import path

from .views import get_sub_categories

app_name = "service"

urlpatterns = [
    path('get_sub_categories/', get_sub_categories, name="get_sub_categories"),
]
