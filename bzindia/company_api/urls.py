from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyApiViewset

app_name = "company_api"

router = DefaultRouter()

router.register(r'', CompanyApiViewset)


urlpatterns = [
    path('', include(router.urls))    
]
