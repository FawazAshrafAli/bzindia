from rest_framework import serializers
from django.conf import settings

from utility.text import clean_string
from datetime import datetime

from product.models import (
    Product, Review, Category, ProductDetailPage, Enquiry, 
    SubCategory, Feature, Timeline, Tag, 
    Faq, BulletPoint
    )
from blog_api.serializers import BlogSerializer
from blog.models import Blog
from locations.models import UniqueState
from meta_api.serializers import MetaTagSerializer

class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ["question", "answer", "slug"]

class ReviewSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    created_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['name', 'text', 'rating', 'created', "product_name", "review_by", "created_date"]
        read_only_fields = fields

    def get_created_date(self, obj):
        if not obj:
            return None

        return datetime.strftime(obj.created, "%b %d, %Y")


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source = "category.name", read_only = True)
    reviews = ReviewSerializer(many=True, read_only=True)
    faqs = serializers.SerializerMethodField()
    blogs = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "name", "image_url", "price", "description", "get_absolute_url", 
            "category_name", "rating", "rating_count", "reviews", "slug", 
            "sku", "stock", "faqs", "blogs"
            ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}/{obj.image.url}"
        
        return None
    
    def get_faqs(self, obj):
        if not obj:
            return None
        
        faqs = Faq.objects.filter(product = obj)

        serializer = FaqSerializer(faqs, many = True)

        return serializer.data
    
    def get_blogs(self, obj):
        if not obj:
            return None
        
        blogs = Blog.objects.filter(product = obj)

        serializer = BlogSerializer(blogs, many = True)

        return serializer.data
    

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["feature", "id"]


# class VerticalBulletSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VerticalBullet
#         fields = ["id", "bullet"]


# class HorizontalBulletSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = HorizontalBullet
#         fields = ["id", "bullet"]

    
# class VerticalTabSerializer(serializers.ModelSerializer):
#     bullets = VerticalBulletSerializer(many=True, read_only=True)

#     class Meta:
#         model = VerticalTab
#         fields = [
#             "id", "heading", "sub_heading", "summary", "bullets"
#             ]
        

# class HorizontalTabSerializer(serializers.ModelSerializer):
#     bullets = HorizontalBulletSerializer(many=True, read_only=True)

#     class Meta:
#         model = HorizontalTab
#         fields = [
#             "id", "heading", "summary", "bullets"
#             ]
        
        
# class TableSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Table
#         fields = [
#             "id", "heading"
#             ]


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
    product = ProductSerializer()

    features = FeatureSerializer(many=True)
    # vertical_tabs = VerticalTabSerializer(many=True, read_only=True)
    # horizontal_tabs = HorizontalTabSerializer(many=True, read_only=True)
    # tables = TableSerializer(many=True, read_only=True)
    bullet_points = BulletPointSerializer(many=True, read_only=True)    
    tags = TagSerializer(many=True, read_only=True)
    timelines = TimelineSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)

    class Meta:
        model = ProductDetailPage
        fields = [
            "product", "slug", "meta_description", "summary", "description",
            "features", "bullet_points", "hide_features", "hide_bullets",
            "hide_tags", "hide_timeline", "tags", "timelines", "meta_tags", 
            "toc", "timeline_title", "tag_title", "hide_support_languages"
            ]
    

class ProductSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ["name", "slug"]


class ProductCategorySerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    sub_categories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["details", "name", "slug", "sub_categories"]

    def get_details(self, obj):
        if not obj:
            return None
        
        details = ProductDetailPage.objects.filter(product__category = obj)

        return DetailSerializer(details, many=True).data
    
    def get_sub_categories(self, obj):
        if not obj:
            return None
        
        sub_categories = SubCategory.objects.filter(category = obj)

        return ProductSubCategorySerializer(sub_categories, many=True).data
    

class EnquirySerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    product = serializers.SlugRelatedField(
        queryset=Product.objects.all(),
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
        fields = ["company", "name", "phone", "email", "product", "state", "message"]
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
            self.fields['product'].queryset = Product.objects.filter(
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