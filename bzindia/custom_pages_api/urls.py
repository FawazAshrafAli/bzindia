from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FaqViewSet, ContactUsViewSet

app_name = "custom_pages_api"

router = DefaultRouter()
router.register(r'faq', FaqViewSet)
router.register(r'contact_us', ContactUsViewSet, basename="contact_us")


urlpatterns = [
    path('', include(router.urls)),
]
