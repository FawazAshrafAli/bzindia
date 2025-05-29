from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import MetaTagApiViewset

app_name = "meta_tag_api"

router = DefaultRouter()

router.register(r'', MetaTagApiViewset)

urlpatterns = [
    path('', include(router.urls)),
]
