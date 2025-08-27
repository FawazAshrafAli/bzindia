from rest_framework import viewsets
from django.shortcuts import get_list_or_404

from .serializers import FaqSerializer, ContactUsSerializer
from custom_pages.models import FAQ, ContactUs

class FaqViewSet(viewsets.ModelViewSet):
    serializer_class = FaqSerializer
    queryset = FAQ.objects.all().order_by("?")
    lookup_field = "slug"


class ContactUsViewSet(viewsets.ModelViewSet):
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.all().order_by("?")
    lookup_field = "company__slug"


class BzindiaFaqsViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = FaqSerializer
    queryset = FAQ.objects.filter(company__isnull = True)
    

class BzindiaContactsViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.filter(company__isnull = True)
