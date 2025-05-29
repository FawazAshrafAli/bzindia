from rest_framework import serializers
from utility.text import clean_string

from registration.models import (
    RegistrationSubType, RegistrationDetailPage, Feature, VerticalBullet, 
    HorizontalBullet, VerticalTab, HorizontalTab, Table, BulletPoint, 
    Tag, Timeline, RegistrationType, Faq, Enquiry, Registration,

    MultiPageFeature, MultiPageFaq, MultiPage, MultiPageBulletPoint,
    MultiPageHorizontalBullet, MultiPageHorizontalTab, MultiPageTable,
    MultiPageTableData, MultiPageTag, MultiPageTimeline,
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
        fields = ["company", "question", "answer", "slug"]

    def get_company(self, obj):
        if obj.company:
            return {"name": obj.company.name, "slug": obj.company.slug}
        
        return {}


class SubTypeSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type.name', read_only=True)
    company_slug = serializers.CharField(source="company.slug", read_only=True)  
    price = serializers.SerializerMethodField()

    class Meta:
        model = RegistrationSubType
        fields = [
            "name", "type_name", "company_slug", "description", "slug",
            "price"
            ]
        
        read_only_fields = fields

    def get_price(self, obj):
        if not obj:
            return
        
        registration_obj = Registration.objects.filter(sub_type = obj).first()

        if registration_obj and registration_obj.price:
            return registration_obj.price

        return None

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["feature", "id"]


class VerticalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerticalBullet
        fields = ["id", "bullet"]


class HorizontalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorizontalBullet
        fields = ["id", "bullet"]

    
class VerticalTabSerializer(serializers.ModelSerializer):
    bullets = VerticalBulletSerializer(many=True, read_only=True)

    class Meta:
        model = VerticalTab
        fields = [
            "id", "heading", "sub_heading", "summary", "bullets"
            ]
        

class HorizontalTabSerializer(serializers.ModelSerializer):
    bullets = HorizontalBulletSerializer(many=True, read_only=True)

    class Meta:
        model = HorizontalTab
        fields = [
            "id", "heading", "summary", "bullets"
            ]
        
        
class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = [
            "id", "heading"
            ]


class BulletPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulletPoint
        fields = [
            "id", "bullet_point"
            ]
        

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            "id", "tag"
            ]
        

class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = [
            "id", "heading", "summary"
            ]


class DetailSerializer(serializers.ModelSerializer):
    registration_sub_type = SubTypeSerializer()
    
    features = FeatureSerializer(many=True)
    vertical_tabs = VerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = HorizontalTabSerializer(many=True, read_only=True)
    tables = TableSerializer(many=True, read_only=True)
    bullet_points = BulletPointSerializer(many=True, read_only=True)    
    tags = TagSerializer(many=True, read_only=True)
    timelines = TimelineSerializer(many=True, read_only=True)
    blogs = BlogSerializer(many=True, read_only=True)
    faqs = FaqSerializer(many=True, read_only=True)
    testimonials = TestimonialSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)
    item_name = serializers.CharField(source="registration_sub_type.name", read_only=True)

    class Meta:
        model = RegistrationDetailPage
        fields = [
            "summary", "description", "features", "registration_sub_type", "slug",
            "vertical_title", "horizontal_title", "vertical_tabs", 
            "horizontal_tabs", "table_title", "tables", "get_data",
            "bullet_title", "bullet_points", "tag_title", "tags",
            "timeline_title", "timelines", "toc", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_tags", "hide_timeline", "hide_support_languages",
            "blogs", "faqs", "testimonials", "meta_tags", "published",
            "modified", "meta_description", "item_name"
            ]


class EnquirySerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    registration_sub_type = serializers.SlugRelatedField(
        queryset=RegistrationSubType.objects.all(),
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
        fields = ["company", "name", "phone", "email", "registration_sub_type", "state", "message"]
        extra_kwargs = {
            'company': {'required': False},  # Typically set server-side
            'name': {'required': True},
            'message': {'required': True}
        }
    
    def get_company(self, obj):
        return obj.company.slug

    def __init__(self, *args, **kwargs):
        company_slug = kwargs.pop('company_slug', None)
        super().__init__(*args, **kwargs)
        
        if company_slug:
            self.fields['registration_sub_type'].queryset = RegistrationSubType.objects.filter(
                company__slug=company_slug,                
            )

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

class MultipageFaqSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only = True)

    class Meta:
        model = MultiPageFaq
        fields = ["company", "question", "answer", "slug"]

    def get_company(self, obj):
        if obj.company:
            return {"name": obj.company.name, "slug": obj.company.slug}
        
        return {}

class MultipageFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageFeature
        fields = ["feature", "id"]


class MultipageVerticalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageVerticalBullet
        fields = ["id", "bullet"]


class MultipageHorizontalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageHorizontalBullet
        fields = ["id", "bullet"]

    
class MultipageVerticalTabSerializer(serializers.ModelSerializer):
    bullets = VerticalBulletSerializer(many=True, read_only=True)

    class Meta:
        model = MultiPageVerticalTab
        fields = [
            "id", "heading", "sub_heading", "summary", "bullets"
            ]
        

class MultipageHorizontalTabSerializer(serializers.ModelSerializer):
    bullets = HorizontalBulletSerializer(many=True, read_only=True)

    class Meta:
        model = MultiPageHorizontalTab
        fields = [
            "id", "heading", "summary", "bullets"
            ]
        
        
class MultipageTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageTable
        fields = [
            "id", "heading"
            ]


class MultipageBulletPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageBulletPoint
        fields = [
            "id", "bullet_point"
            ]
        

class MultipageTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageTag
        fields = [
            "id", "tag"
            ]
        

class MultipageTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageTimeline
        fields = [
            "id", "heading", "summary"
            ]


class MultipageSerializer(serializers.ModelSerializer):
    registration = SubTypeSerializer()

    features = MultipageFeatureSerializer(many=True)
    vertical_tabs = MultipageVerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = MultipageHorizontalTabSerializer(many=True, read_only=True)
    tables = MultipageTableSerializer(many=True, read_only=True)
    bullet_points = MultipageBulletPointSerializer(many=True, read_only=True)    
    tags = MultipageTagSerializer(many=True, read_only=True)
    timelines = MultipageTimelineSerializer(many=True, read_only=True)
    faqs = MultipageFaqSerializer(many=True, read_only=True)
    blogs = BlogSerializer(many=True, read_only=True)
    testimonials = TestimonialSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)

    company_slug = serializers.CharField(source = "company.slug", read_only=True)
    company_name = serializers.CharField(source = "company.name", read_only=True)

    class Meta:
        model = MultiPage
        fields = [
            "title", "summary", "description", "features", "slug",
            "vertical_title", "horizontal_title", "vertical_tabs", 
            "horizontal_tabs", "table_title", "tables", "get_data",
            "bullet_title", "bullet_points", "tag_title", "tags",
            "timeline_title", "timelines", "toc", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_tags", "hide_timeline", "hide_support_languages",
            "blogs", "faqs", "testimonials", "meta_tags", "published",
            "modified", "meta_description", "company_slug", "url_type",
            "rating", "rating_count", "registration", "company_name"
            ]
        
        read_only = fields


class TypeSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    detail_pages = serializers.SerializerMethodField()

    class Meta:
        model = RegistrationType
        fields = [
            "name", "company", "description", "slug", "detail_pages",
            ]
        
        read_only_fields = fields

    def get_detail_pages(self, obj):
        if not obj:
            return None
        
        details = RegistrationDetailPage.objects.filter(registration_sub_type__type = obj)

        return DetailSerializer(details, many=True).data
        