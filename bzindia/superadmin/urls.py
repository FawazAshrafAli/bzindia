from django.urls import path
from .views import HomeView, CompanyListView, AddCompanyView, UpdateCompanyView, DeleteCompanyView

app_name = "superadmin"

urlpatterns = [
    path('', HomeView.as_view(), name="home"),

    # Company
    path('add_company/', AddCompanyView.as_view(), name="add_company"),
    path('update_company/<str:slug>', UpdateCompanyView.as_view(), name="update_company"),
    path('delete_company/<str:slug>', DeleteCompanyView.as_view(), name="delete_company"),
    path('companies/', CompanyListView.as_view(), name="companies"),
]
