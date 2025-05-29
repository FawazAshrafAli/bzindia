from rest_framework import viewsets

from .serializers import ServiceSerializer
from service.models import Service

class ServiceApiViewset(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    queryset = Service.objects.all().order_by("?").order_by("?")[:12]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context