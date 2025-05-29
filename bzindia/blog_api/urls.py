from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BlogApiViewset

app_name = "blog_api"

router = DefaultRouter()

router.register(r'', BlogApiViewset)

urlpatterns = [
    path('', include(router.urls)),
]
