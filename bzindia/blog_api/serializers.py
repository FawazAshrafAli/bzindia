from rest_framework import serializers
from django.conf import settings
from datetime import datetime
from django.db.models import Q

from blog.models import Blog
from meta_api.serializers import MetaTagSerializer

class BlogSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    published_on = serializers.SerializerMethodField()
    meta_tags = MetaTagSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = [
            "title", "image_url", "published_date", "updated", 
            "get_absolute_url", "summary", "meta_tags", "slug", 
            "category", "category_slug", "published_on", "company", "content",
            "category_count", "meta_description"
            ]
        
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}/{obj.image.url}"
        
        return None
    
    def get_published_on(self, obj):
        if obj.published_date:
            return datetime.strftime(obj.published_date, "%b %d, %Y")
        
        return None