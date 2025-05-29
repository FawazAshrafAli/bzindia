from rest_framework import viewsets

from .serializers import MetaTagSerializer
from service.models import MetaTag

class MetaTagApiViewset(viewsets.ModelViewSet):
    serializer_class = MetaTagSerializer
    queryset = MetaTag.objects.all().order_by("?")