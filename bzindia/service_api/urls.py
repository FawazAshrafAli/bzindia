from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from django.urls import path, include
from .views import (
    ServiceViewset, CompanyViewSet, DetailViewSet, EnquiryViewSet,
    )

app_name = "service_api"

router = DefaultRouter()

router.register(r'companies', CompanyViewSet, basename="company")

companies_router = NestedDefaultRouter(router, r'companies', lookup = "company")

companies_router.register(r'services', ServiceViewset, basename="company-service")
companies_router.register(r'details', DetailViewSet, basename="company-detail")
companies_router.register(r'enquiries', EnquiryViewSet, basename="company-enquiry")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(companies_router.urls)),
]
