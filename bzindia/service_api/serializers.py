from rest_framework import serializers
from django.conf import settings

from service.models import Service, Category, ServiceDetail

class ServiceSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only = True)
    duration_count = serializers.CharField(source="duration.days", read_only = True)
    company_social_medias = serializers.SerializerMethodField()
    company_name = serializers.CharField(source="company.name", read_only = True)
    company_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ["name", "image_url", "company_name", "category_name", "duration_count", "price", "company_logo_url", "company_social_medias", "slug"]

        read_only_fields = ["company_name"]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        
        return None
    
    def get_company_logo_url(self, obj):
        request = self.context.get('request')
        if obj.company and hasattr(obj.company, 'logo') and hasattr(obj.company.logo, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.company.logo.url)
            return f"{settings.SITE_URL}{obj.company.logo.url}"
        
        return None    
    
    def get_company_social_medias(self, obj):
        if not hasattr(obj, 'company') or not obj.company:
            return []
        
        try:
            # This will use the @property we defined on the Company model
            return obj.company.social_media_links
        except AttributeError:
            return []
        

class DetailSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    item_name = serializers.CharField(source = "service.name", read_only=True)

    model = ServiceDetail
    fields = ["service", "slug", "item_name"]


class CategorySerializer(serializers.ModelSerializer):
    detail_pages = serializers.SerializerMethodField()

    model = Category
    fields = ["detail_pages"]

    def get_detail_pages(self, obj):
        if not obj:
            return None
        
        details = ServiceDetail.objects.filter(service__category = obj)

        return DetailSerializer(details, many=True).data