from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import DestinationApiViewset

app_name = "destination_api"

router = DefaultRouter()

router.register(r'destinations', DestinationApiViewset, basename="destination"), 

urlpatterns = [
    path('', include(router.urls)),
]
