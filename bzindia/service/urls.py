from django.urls import path

from .views import GetSubCategoriesView, GetServicesView

app_name = "service"

urlpatterns = [
    path('get_sub_categories/', GetSubCategoriesView.as_view(), name="get_sub_categories"),
    path('get_services/', GetServicesView.as_view(), name="get_services"),
]
