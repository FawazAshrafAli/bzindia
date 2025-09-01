from rest_framework import serializers
from django.conf import settings

from utility.text import clean_string

from service.models import (
    Service, Category, ServiceDetail, Feature, VerticalBullet,
    VerticalTab, HorizontalBullet, HorizontalTab, Table,
    Timeline, BulletPoints, Faq, Enquiry, MultiPageVerticalBullet,
    MultiPageVerticalTab, MultiPageHorizontalTab, MultiPageHorizontalBullet,
    MultiPageTimeline, MultiPageTable, MultiPageBulletPoint, 
    MultiPageFaq, MultiPageFeature, MultiPage, SubCategory
    )
from locations.models import UniqueState
from company.models import Testimonial
from blog.models import Blog

from company_api.serializers import CompanySerializer, TestimonialSerializer
from blog_api.serializers import BlogSerializer
from meta_api.serializers import MetaTagSerializer

class FaqSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only = True)

    class Meta:
        model = Faq
        fields = ["id","company", "question", "answer", "slug"]

    def get_company(self, obj):
        if obj.company:
            return {"name": obj.company.name, "slug": obj.company.slug}
        
        return {}
    

class MiniServiceSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only = True)
    sub_category_name = serializers.CharField(source="sub_category.name", read_only = True)

    class Meta:
        model = Service
        fields = ["id",
            "name", "image_url", "category_name", 
            "price", "sub_category_name",            
            ]

        read_only_fields = fields

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        
        return None

class ServiceSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only = True)
    category_slug = serializers.CharField(source="category.slug", read_only = True)
    sub_category_name = serializers.CharField(source="sub_category.name", read_only = True)
    sub_category_slug = serializers.CharField(source="sub_category.slug", read_only = True)
    duration_count = serializers.CharField(source="duration.days", read_only = True)
    company_social_medias = serializers.SerializerMethodField()
    company_name = serializers.CharField(source="company.name", read_only = True)
    company_logo_url = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ["id",
            "name", "image_url", "company_name", "category_name", 
            "duration_count", "price", "company_logo_url", 
            "company_social_medias", "slug", "sub_category_name",
            "faqs", "testimonials", "category_slug", 
            "sub_category_slug"
            ]

        read_only_fields = ["id","company_name"]

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
            return obj.company.social_media_links
        except AttributeError:
            return []
        
    def get_faqs(self, obj):
        if not obj:
            return None
        
        faqs = Faq.objects.filter(service = obj)

        serializers = FaqSerializer(faqs, many=True)

        return serializers.data
    
    def get_testimonials(self, obj):
        if not obj:
            return None
        
        testimonials = Testimonial.objects.filter(company = obj.company)

        serializer = TestimonialSerializer(testimonials, many=True)

        return serializer.data    


class CategorySerializer(serializers.ModelSerializer):
    detail_pages = serializers.SerializerMethodField()
    blogs = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id","name", "slug", "updated", "detail_pages", "blogs", "testimonials",
                  "image_url"]
        
    def get_image_url(self, obj):
        request = self.context.get('request')

        service = obj.services.filter(image__isnull = False).first()

        if service and service.image and hasattr(service.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(service.image.url)
            return f"{settings.SITE_URL}{service.image.url}"
        
        return None

    def get_detail_pages(self, obj):
        if not obj:
            return None
        
        details = ServiceDetail.objects.filter(service__category = obj)

        return DetailSerializer(details, many=True).data
    
    def get_blogs(self, obj):

        blogs = Blog.objects.filter(service__category = obj)
        serializer = BlogSerializer(blogs, many=True)

        return serializer.data
    
    def get_testimonials(self, obj):

        testimonials = Testimonial.objects.filter(company = obj.company)

        serializer = TestimonialSerializer(testimonials, many=True)

        return serializer.data
    

class SubCategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    blogs = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = ["id",
            "name", "slug", "updated", "image_url", "category_name", 
            "category_slug", "testimonials", "blogs"
            ]

    read_only_fields = "__all__"

    def get_blogs(self, obj):

        blogs = Blog.objects.filter(service__sub_category = obj)
        serializer = BlogSerializer(blogs, many=True)

        return serializer.data
    
    def get_testimonials(self, obj):

        testimonials = Testimonial.objects.filter(company = obj.company)

        serializer = TestimonialSerializer(testimonials, many=True)

        return serializer.data

    def get_image_url(self, obj):
        request = self.context.get('request')

        service = obj.services.filter(image__isnull = False).first()

        if service and service.image and hasattr(service.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(service.image.url)
            return f"{settings.SITE_URL}{service.image.url}"
        
        return None
    
    

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["id","feature", "id"]


class VerticalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerticalBullet
        fields = ["id","id", "bullet"]


class HorizontalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorizontalBullet
        fields = ["id","id", "bullet"]

    
class VerticalTabSerializer(serializers.ModelSerializer):
    bullets = VerticalBulletSerializer(many=True, read_only=True)

    class Meta:
        model = VerticalTab
        fields = ["id",
            "id", "heading", "sub_heading", "summary", "bullets"
            ]
        

class HorizontalTabSerializer(serializers.ModelSerializer):
    bullets = HorizontalBulletSerializer(many=True, read_only=True)

    class Meta:
        model = HorizontalTab
        fields = ["id",
            "id", "heading", "summary", "bullets"
            ]
        
        
class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ["id",
            "id", "heading"
            ]


class BulletPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulletPoints
        fields = ["id",
            "id", "bullet_point"
            ]
        

class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = ["id",
            "id", "heading", "summary"
            ]


class MiniDetailSerializer(serializers.ModelSerializer):
    service = MiniServiceSerializer()
           
    company_slug = serializers.CharField(source="company.slug", read_only=True)
    company_sub_type = serializers.CharField(source="company.sub_type", read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceDetail
        fields = ["id",
            "meta_description", "service", "company_slug",
            "company_sub_type", "url"
            ] 
        
    def get_url(self, obj):
        try:
            company_slug = obj.company.slug
            category_slug = obj.service.category.slug
            sub_category_slug = obj.service.sub_category.slug
            slug = obj.slug
        except AttributeError:
            return None

        return f"{company_slug}/{category_slug}/{sub_category_slug}/{slug}"
        

class DetailSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()
    
    features = FeatureSerializer(many=True)
    vertical_tabs = VerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = HorizontalTabSerializer(many=True, read_only=True)
    tables = TableSerializer(many=True, read_only=True)
    bullet_points = BulletPointSerializer(many=True, read_only=True)    
    timelines = TimelineSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)    
    company_slug = serializers.CharField(source="company.slug", read_only=True)
    company_sub_type = serializers.CharField(source="company.sub_type", read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceDetail
        fields = ["id",
            "meta_title", "meta_description", "company_slug",
            "summary", "description", "features", "service", "slug",
            "vertical_title", "horizontal_title", "vertical_tabs", 
            "horizontal_tabs", "table_title", "tables", "get_data",
            "bullet_title", "bullet_points",
            "timeline_title", "timelines", "toc", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_timeline", "hide_support_languages",
            "meta_tags", "published", "company_sub_type",
            "modified", "updated", "created", "url"
            ] 
        
    def get_url(self, obj):
        try:
            company_slug = obj.company.slug
            category_slug = obj.service.category.slug
            sub_category_slug = obj.service.sub_category.slug
            slug = obj.slug
        except AttributeError:
            return None

        return f"{company_slug}/{category_slug}/{sub_category_slug}/{slug}"
        

class EnquirySerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    service = serializers.SlugRelatedField(
        queryset=Service.objects.all(),
        slug_field='slug',
        required=True
    )
    
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
        model = Enquiry
        fields = ["id","company", "name", "phone", "email", "service", "state"]
        extra_kwargs = {
            'company': {'required': False}, 
            'name': {'required': True},
        }
    
    def get_company(self, obj):
        return obj.company.slug

    def __init__(self, *args, **kwargs):
        company_slug = kwargs.pop('company_slug', None)
        super().__init__(*args, **kwargs)
        
        if company_slug:
            self.fields['service'].queryset = Service.objects.filter(
                company__slug=company_slug,                
            )

    def validate(self, data):
        # Clean string fields
        cleaned_data = {}
        string_fields = ["id",'name']
        
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
        
        return data


class MultipageFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageFeature
        fields = ["id","feature", "id"]


class MultipageVerticalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageVerticalBullet
        fields = ["id","id", "bullet"]


class MultipageHorizontalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageHorizontalBullet
        fields = ["id","id", "bullet"]

    
class MultipageVerticalTabSerializer(serializers.ModelSerializer):
    bullets = VerticalBulletSerializer(many=True, read_only=True)

    class Meta:
        model = MultiPageVerticalTab
        fields = ["id",
            "id", "heading", "sub_heading", "summary", "bullets"
            ]
        

class MultipageHorizontalTabSerializer(serializers.ModelSerializer):
    bullets = HorizontalBulletSerializer(many=True, read_only=True)

    class Meta:
        model = MultiPageHorizontalTab
        fields = ["id",
            "id", "heading", "summary", "bullets"
            ]
        
        
class MultipageTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageTable
        fields = ["id",
            "id", "heading"
            ]


class MultipageBulletPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageBulletPoint
        fields = ["id",
            "id", "bullet_point"
            ]
        

class MultipageTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageTimeline
        fields = ["id",
            "id", "heading", "summary"
            ]
        

class MultipageFaqSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only = True)

    class Meta:
        model = MultiPageFaq
        fields = ["id","company", "question", "answer", "slug"]

    def get_company(self, obj):
        if obj.company:
            return {"name": obj.company.name, "slug": obj.company.slug}
        
        return {}


class MultipageSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()
    company = CompanySerializer()

    features = MultipageFeatureSerializer(many=True)
    vertical_tabs = MultipageVerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = MultipageHorizontalTabSerializer(many=True, read_only=True)
    tables = MultipageTableSerializer(many=True, read_only=True)
    bullet_points = MultipageBulletPointSerializer(many=True, read_only=True)    
    timelines = MultipageTimelineSerializer(many=True, read_only=True)
    faqs = MultipageFaqSerializer(many=True, read_only=True)
    blogs = BlogSerializer(many=True, read_only=True)
    testimonials = serializers.SerializerMethodField()
    meta_tags = MetaTagSerializer(many=True, read_only=True)

    company_slug = serializers.CharField(source = "company.slug", read_only=True)
    company_name = serializers.CharField(source = "company.name", read_only=True)    
    blogs = serializers.SerializerMethodField()

    slider_services = DetailSerializer(many=True)

    class Meta:
        model = MultiPage
        fields = ["id",
            "title", "summary", "description", "slider_services", "features", "slug",
            "vertical_title", "horizontal_title", "vertical_tabs", 
            "horizontal_tabs", "table_title", "tables", "get_data",
            "bullet_title", "bullet_points",
            "timeline_title", "timelines", "toc", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_timeline", "hide_support_languages",
            "blogs", "faqs", "testimonials", "meta_tags", "published",
            "modified", "meta_description", "company_slug", "url_type",
            "rating", "rating_count", "service", "company_name", "company",
            "blogs", "sub_title", "meta_title"
            ]
        
        read_only = fields

    def get_blogs(self, obj):
        if not obj:
            return None
        
        blogs = Blog.objects.filter(company = obj.company, service = obj.service, is_published = True)

        serializer = BlogSerializer(blogs, many=True)

        return serializer.data

    def get_testimonials(self, obj):
        if not obj:
            return None
        
        testimonials = Testimonial.objects.filter(company = obj.company)

        serializer = TestimonialSerializer(testimonials, many=True)

        return serializer.data    
        
