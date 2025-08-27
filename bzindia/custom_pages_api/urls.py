from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FaqViewSet, ContactUsViewSet, BzindiaFaqsViewset, BzindiaContactsViewset

app_name = "custom_pages_api"

router = DefaultRouter()
router.register(r'faqs', FaqViewSet)
router.register(r'bzindia_faqs', BzindiaFaqsViewset, basename = "bzindia_faqs")
router.register(r'contact_us', ContactUsViewSet, basename="contact_us")
router.register(r'bzindia_contacts', BzindiaContactsViewset, basename="bzindia_contacts")


urlpatterns = [
    path('', include(router.urls)),
]
