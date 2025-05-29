from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ServiceApiViewset

app_name = "service_api"

router = DefaultRouter()

router.register(r'', ServiceApiViewset)

urlpatterns = [
    path('', include(router.urls)),
]
