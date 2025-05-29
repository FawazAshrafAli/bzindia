from rest_framework import serializers
from django.conf import settings

from company.models import Company, CompanyType, Client, ContactEnquiry, Testimonial

from blog_api.serializers import BlogSerializer
from meta_api.serializers import MetaTagSerializer
from custom_pages_api.serializers import FaqSerializer
from locations.models import UniqueState

from utility.text import clean_string

class ClientSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ["name", "image_url", "slug"]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        return None
    

class TestimonialSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    place_name = serializers.CharField(source = "place.name", read_only = True)

    class Meta:
        model = Testimonial
        fields = [
            "name", "image_url", "slug", "client_company", "place_name",
            "text", "rating"
            ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        return None
    

class CompanySerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    favicon_url = serializers.SerializerMethodField()
    company_type = serializers.CharField(source = "type.name", read_only=True)
    blogs = BlogSerializer(many=True, read_only=True)
    faqs = FaqSerializer(many=True, read_only = True)
    meta_tags = MetaTagSerializer(many=True, read_only = True)
    clients = ClientSerializer(many=True, read_only=True)

    class Meta:
        model = Company 
        fields = [
            "name", "logo_url", "description" , "categories", 
            "social_media_links", "get_absolute_url", "slug", 
            "company_type", "footer_content", "meta_title",
            "phone1", "phone2", "blogs", "faqs", "whatsapp", 
            "email", "meta_tags", "meta_description", 
            "favicon_url", "price_range", "twitter", "facebook",
            "created", "updated", "clients", "rating"
        ]

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and hasattr(obj.logo, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.logo.url)
            return f"{settings.SITE_URL}{obj.logo.url}"
        return None
    
    def get_favicon_url(self, obj):
        request = self.context.get('request')
        if obj.favicon and hasattr(obj.favicon, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.favicon.url)
            return f"{settings.SITE_URL}{obj.favicon.url}"
        return None
    
    def get_categories(self, obj):
        categories = obj.categories
        return list(categories) if categories else []   
    

class CompanyTypeSerializer(serializers.ModelSerializer):
    companies = CompanySerializer(many=True, read_only=True)

    class Meta:
        model = CompanyType
        fields = ["name", "slug", "companies", "categories"]
    

class ContactEnquirySerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()
    
    state = serializers.SlugRelatedField(
        queryset=UniqueState.objects.all(),
        slug_field='slug',
        required=True
    )
    
    phone = serializers.RegexField(
        regex=r'^\+?[1-9]\d{1,14}$',  # E.164 international phone format
        error_messages={
            'invalid': 'Enter a valid phone number (e.g. +1234567890) with 9-15 digits.'
        },
        required=True
    )
    
    email = serializers.EmailField(
        max_length=254,
        required=True
    )
    
    class Meta:
        model = ContactEnquiry
        fields = ["company", "name", "phone", "email", "state", "message"]
        extra_kwargs = {
            'company': {'required': False},
            'name': {'required': True},
            'message': {'required': True}
        }
    
    def get_company(self, obj):
        return obj.company.slug

    def validate(self, data):
        # Clean string fields
        cleaned_data = {}
        string_fields = ['name', 'message']
        
        for field in string_fields:
            value = data.get(field, '').strip()
            if not value:
                raise serializers.ValidationError(
                    {field: f"{field.capitalize()} is required and cannot be empty"}
                )
            cleaned_data[field] = clean_string(value)
        
        # Email validation
        email = data.get('email', '').strip().lower()
        if not email:
            raise serializers.ValidationError({"email": "Email is required"})
        cleaned_data['email'] = email
        
        # Phone validation (already handled by RegexField)
        cleaned_data['phone'] = data['phone']
        
        # Update data with cleaned values
        data.update(cleaned_data)
        
        # Additional business logic validation
        if not self.context.get('request').user.is_authenticated:
            # Example: Spam prevention for anonymous submissions
            if len(data['message']) > 1000:
                raise serializers.ValidationError(
                    {"message": "Message too long (max 1000 characters)"}
                )
        
        return data