from rest_framework import viewsets

from .serializers import BlogSerializer
from blog.models import Blog

class BlogApiViewset(viewsets.ModelViewSet):
    serializer_class = BlogSerializer
    queryset = Blog.objects.filter(is_published = True).order_by("?")
    lookup_field = "slug"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context