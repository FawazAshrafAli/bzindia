from django.urls import path

from .views import get_company, CompanyHomePageView

app_name = "company"

urlpatterns = [
    path("<str:slug>", CompanyHomePageView.as_view(), name="company_home"),
    path("get_company/<str:slug>", get_company, name="get_company"),
]
