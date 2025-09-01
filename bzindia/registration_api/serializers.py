from rest_framework import serializers
from utility.text import clean_string
from django.conf import settings
from django.db.models import Avg

from registration.models import (
    RegistrationSubType, RegistrationDetailPage, Feature, VerticalBullet, 
    HorizontalBullet, VerticalTab, HorizontalTab, Table, BulletPoint, 
    Timeline, RegistrationType, Faq, Enquiry, Registration,

    MultiPageFeature, MultiPageFaq, MultiPage, MultiPageBulletPoint,
    MultiPageHorizontalBullet, MultiPageHorizontalTab, MultiPageTable,
    MultiPageTimeline,
    MultiPageVerticalBullet, MultiPageVerticalTab
    )
from locations.models import UniqueState

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


class SubTypeSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type.name', read_only=True)
    type_slug = serializers.CharField(source='type.slug', read_only=True)
    company_slug = serializers.CharField(source="company.slug", read_only=True)  
    price = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()      
    rating = serializers.SerializerMethodField() 
    image_url = serializers.SerializerMethodField()


    class Meta:
        model = RegistrationSubType
        fields = ["id",
            "name", "type_name", "company_slug", "description", "slug",
            "price", "type_slug", "testimonials",
            "rating", "updated", "image_url"
            ]
        
        read_only_fields = fields    

    def get_rating(self, obj):
        if not obj.company:
            return 0
        
        testimonials = obj.company.testimonials.values_list("rating", flat=True)

        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0    

    def get_price(self, obj):
        if obj.registrations:
        
            # registration_obj = Registration.objects.filter(sub_type = obj).first()
            registration_obj = obj.registrations.first()

            if registration_obj and registration_obj.price:
                return registration_obj.price

        return None

    def get_testimonials(self, obj):
        from company.models import Testimonial

        if not obj.company: 
            return None
        
        testimonials = Testimonial.objects.filter(company = obj.company)

        serializer = TestimonialSerializer(testimonials, many=True)

        return serializer.data
    
    def get_image_url(self, obj):
        first_registration_with_image = obj.registrations.filter(image__isnull = False).first()

        if first_registration_with_image:
            request = self.context.get('request')
            if first_registration_with_image.image and hasattr(first_registration_with_image.image, 'url'):
                if request is not None:
                    return request.build_absolute_uri(first_registration_with_image.image.url)
                return f"{settings.SITE_URL}{first_registration_with_image.image.url}"
        
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
        model = BulletPoint
        fields = ["id",
            "id", "bullet_point"
            ]
        

class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = ["id",
            "id", "heading", "summary"
            ]


class MiniRegistrationSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField() 

    class Meta:
        model = Registration
        fields = ["id",
            "title", "image_url", "sub_type", "price"        
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        
        return None


class RegistrationSerializer(serializers.ModelSerializer):
    sub_type  = SubTypeSerializer()
    image_url = serializers.SerializerMethodField() 
    blogs = serializers.SerializerMethodField()  
    rating = serializers.SerializerMethodField()  

    class Meta:
        model = Registration
        fields = ["id",
            "title", "image_url", "sub_type", "price",
            "time_required", "required_documents", "additional_info",
            "slug", "updated", "blogs", "rating"
        ]

    def get_rating(self, obj):
        if not obj.company:
            return 0
        
        testimonials = obj.company.testimonials.values_list("rating", flat=True)

        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0

    def get_blogs(self, obj):
        blogs = obj.blogs.all()

        serializer = BlogSerializer(blogs, many=True)
        
        return serializer.data

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        
        return None


class MiniDetailSerializer(serializers.ModelSerializer):
    registration = MiniRegistrationSerializer()
    company_slug = serializers.CharField(source="company.slug", read_only=True)
    company_sub_type = serializers.CharField(source="company.sub_type", read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = RegistrationDetailPage
        fields = ["id",
            "registration", "meta_description", "company_slug",
            "company_sub_type", "url"
            ]
        
    def get_url(self, obj):
        try:
            company_slug = obj.company.slug
            type_slug = obj.registration.registration_type.slug
            sub_type_slug = obj.registration.sub_type.slug
            slug = obj.slug
        except AttributeError:
            return None

        return f"{company_slug}/{type_slug}/{sub_type_slug}/{slug}"


class DetailSerializer(serializers.ModelSerializer):
    registration = RegistrationSerializer()
    company_slug = serializers.CharField(source="company.slug", read_only=True)
    
    features = FeatureSerializer(many=True)
    vertical_tabs = VerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = HorizontalTabSerializer(many=True, read_only=True)
    tables = TableSerializer(many=True, read_only=True)
    bullet_points = BulletPointSerializer(many=True, read_only=True)    
    timelines = TimelineSerializer(many=True, read_only=True)
    faqs = serializers.SerializerMethodField()
    testimonials = TestimonialSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)
    item_name = serializers.CharField(source="registration.title", read_only=True)
    company_sub_type = serializers.CharField(source="company.sub_type", read_only=True)
    company_meta_title = serializers.CharField(source="company.meta_title", read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = RegistrationDetailPage
        fields = ["id",
            "registration", "meta_title", "meta_description",
            "summary", "description", "features", "slug",
            "vertical_title", "horizontal_title", "vertical_tabs", 
            "horizontal_tabs", "table_title", "tables", "get_data",
            "bullet_title", "bullet_points",
            "timeline_title", "timelines", "toc", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_timeline", "hide_support_languages",
            "faqs", "testimonials", "meta_tags", "published",
            "modified", "item_name", "created", "updated",
            "company_slug", "company_sub_type", "url", "company_meta_title"
            ]
        
    def get_url(self, obj):
        try:
            company_slug = obj.company.slug
            type_slug = obj.registration.registration_type.slug
            sub_type_slug = obj.registration.sub_type.slug
            slug = obj.slug
        except AttributeError:
            return None

        return f"{company_slug}/{type_slug}/{sub_type_slug}/{slug}"
    
    def get_faqs(self, obj):
        if obj.registration:
            faqs = obj.registration.faqs.all()

            if faqs:
                serializer = FaqSerializer(faqs, many=True)
                return serializer.data
            
        return None
            


class EnquirySerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    registration = serializers.SlugRelatedField(
        queryset=Registration.objects.all(),
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
        fields = ["id","company", "name", "phone", "email", "registration", "state"]
        extra_kwargs = {
            'company': {'required': False},  # Typically set server-side
            'name': {'required': True}
        }
    
    def get_company(self, obj):
        return obj.company.slug

    def __init__(self, *args, **kwargs):
        company_slug = kwargs.pop('company_slug', None)
        super().__init__(*args, **kwargs)
        
        if company_slug:
            self.fields['registration'].queryset = Registration.objects.filter(
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

class MultipageFaqSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only = True)

    class Meta:
        model = MultiPageFaq
        fields = ["id","company", "question", "answer", "slug"]

    def get_company(self, obj):
        if obj.company:
            return {"name": obj.company.name, "slug": obj.company.slug}
        
        return {}

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


class MultipageSerializer(serializers.ModelSerializer):
    registration = RegistrationSerializer()

    features = MultipageFeatureSerializer(many=True)
    vertical_tabs = MultipageVerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = MultipageHorizontalTabSerializer(many=True, read_only=True)
    tables = MultipageTableSerializer(many=True, read_only=True)
    bullet_points = MultipageBulletPointSerializer(many=True, read_only=True)    
    timelines = MultipageTimelineSerializer(many=True, read_only=True)
    faqs = MultipageFaqSerializer(many=True, read_only=True)
    testimonials = TestimonialSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)

    company_slug = serializers.CharField(source = "company.slug", read_only=True)
    company_name = serializers.CharField(source = "company.name", read_only=True)

    slider_registrations = DetailSerializer(many = True)

    class Meta:
        model = MultiPage
        fields = ["id",
            "title", "slug", "summary", "description", "slider_registrations", "features", "slug",
            "vertical_title", "horizontal_title", "vertical_tabs", 
            "horizontal_tabs", "table_title", "tables", "get_data",
            "bullet_title", "bullet_points",
            "timeline_title", "timelines", "toc", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_timeline", "hide_support_languages",
            "faqs", "testimonials", "meta_tags", "published",
            "modified", "meta_description", "company_slug", "url_type",
            "rating", "rating_count", "registration", "company_name",
            "sub_title", "meta_title"
            ]
        
        read_only = fields


class TypeSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    detail_pages = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()
    blogs = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField() 

    class Meta:
        model = RegistrationType
        fields = ["id",
            "name", "company", "description", "slug", "detail_pages",
            "testimonials", "blogs", "updated", "rating"
            ]
        
        read_only_fields = fields

    def get_rating(self, obj):
        if not obj.company:
            return 0
        
        testimonials = obj.company.testimonials.values_list("rating", flat=True)

        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0

    def get_blogs(self, obj):
        from blog.models import  Blog        

        registration_slugs = obj.registrations.values_list("slug", flat=True)
        blogs = Blog.objects.filter(registration__slug__in = registration_slugs)

        serializer = BlogSerializer(blogs, many=True)
        
        return serializer.data

    def get_testimonials(self, obj):
        from company.models import Testimonial

        if not obj.company: 
            return None
        
        testimonials = Testimonial.objects.filter(company = obj.company)

        serializer = TestimonialSerializer(testimonials, many=True)

        return serializer.data

    def get_detail_pages(self, obj):
        if not obj:
            return None
        
        details = RegistrationDetailPage.objects.filter(registration__registration_type = obj)

        return DetailSerializer(details, many=True).data
        