from rest_framework import serializers
from django.conf import settings
from django.db.models import Max

from utility.text import clean_string
from datetime import datetime

from product.models import (
    Product, Review, Category, ProductDetailPage, Enquiry, 
    SubCategory, Feature, Timeline,MultiPage,
    Faq, BulletPoint, MultiPageFaq, MultiPageBulletPoint,
    MultiPageFeature, MultiPageTimeline,
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
    image_url = serializers.SerializerMethodField()

    product = serializers.SlugRelatedField(
        queryset=Product.objects.all(),
        slug_field='slug',
        required=True
    )

    email = serializers.EmailField(
        max_length=254,
        required=True
    )
    
    class Meta:
        model = Review
        fields = ['name', 'text', 'rating', 'created', "product_name", "review_by", "created_date", "product", "email", "image_url"]
        extra_kwargs = {
            'company': {'required': False},
            'review_by': {'required': True},
            'text': {'required': True},
            'email': {'required': True},
            'rating': {'required': True}
        }

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.product.image and hasattr(obj.product.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.product.image.url)
            return f"{settings.SITE_URL}/{obj.product.image.url}"
        
        return None

    def get_created_date(self, obj):
        if not obj:
            return None

        return datetime.strftime(obj.created, "%b %d, %Y")
    
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
        string_fields = ['review_by', 'text']
        
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

        rating = data.get('rating', '')
        cleaned_data['rating'] = rating if rating else 0

        
        # Update data with cleaned values
        data.update(cleaned_data)
        
        # Additional business logic validation
        if not self.context.get('request').user.is_authenticated:
            # Example: Spam prevention for anonymous submissions
            if len(data['text']) > 1000:
                raise serializers.ValidationError(
                    {"message": "Message too long (max 1000 characters)"}
                )
        
        return data


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source = "category.name", read_only = True)
    category_slug = serializers.CharField(source = "category.slug", read_only = True)
    sub_category_name = serializers.CharField(source = "sub_category.name", read_only = True)
    sub_category_slug = serializers.CharField(source = "sub_category.slug", read_only = True)
    brand_name = serializers.CharField(source = "brand.name", read_only = True)
    reviews = ReviewSerializer(many=True, read_only=True)
    faqs = serializers.SerializerMethodField()
    blogs = serializers.SerializerMethodField()
    detail_page_slug = serializers.SerializerMethodField()    

    class Meta:
        model = Product
        fields = [
            "name", "image_url", "price", "description", "get_absolute_url", 
            "category_name", "rating", "rating_count", "reviews", "slug", 
            "sku", "stock", "faqs", "blogs", "category_slug", "brand_name",
            "detail_page_slug", "sub_category_slug", "sub_category_name"
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
    
    def get_detail_page_slug(self, obj):
        if not obj:
            return None
        
        try:
            detail_page = ProductDetailPage.objects.get(product = obj)

            return detail_page.slug
        except ProductDetailPage.DoesNotExist:
            return None


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["feature", "id"]


class BulletPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulletPoint
        fields = [
            "id", "bullet_point"
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
    bullet_points = BulletPointSerializer(many=True, read_only=True)    
    timelines = TimelineSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)
    company_slug = serializers.CharField(source="company.slug", read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProductDetailPage
        fields = [
            "meta_title", "meta_description",
            "product", "slug", "summary", "description",
            "features", "bullet_points", "hide_features", "hide_bullets",
            "hide_timeline", "timelines", "meta_tags", 
            "toc", "timeline_title", "hide_support_languages",
            "created", "updated", "company_slug", "url"
            ]
        
    def get_url(self, obj):
        try:
            company_slug = obj.company.slug
            category_slug = obj.product.category.slug
            sub_category_slug = obj.product.sub_category.slug
            slug = obj.slug
        except AttributeError:
            return None

        return f"{company_slug}/{category_slug}/{sub_category_slug}/{slug}"
        

class MultipageFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageFeature
        fields = ["feature", "id"]


class MultipageBulletPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageBulletPoint
        fields = [
            "id", "bullet_point"
            ]
        

class MultipageTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageTimeline
        fields = [
            "id", "heading", "summary"
            ]
        

class MultipageFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageFaq
        fields = [
            "id", "question", "answer", "slug"
            ]


class MultiPageSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    company_slug = serializers.CharField(source="company.slug", read_only=True)

    features = MultipageFeatureSerializer(many=True)    
    bullet_points = MultipageBulletPointSerializer(many=True, read_only=True)    
    timelines = MultipageTimelineSerializer(many=True, read_only=True)
    faqs = MultipageFaqSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    blogs = serializers.SerializerMethodField()
    published = serializers.SerializerMethodField()

    class Meta:
        model = MultiPage
        fields = [
            "title", "products", "slug", "meta_description", "summary", "description",
            "features", "bullet_points", "hide_features", "hide_bullets",
            "hide_timeline", "timelines", "meta_tags", 
            "toc", "timeline_title", "hide_support_languages",
            "faqs", "company_slug", "rating", "rating_count", "reviews",
            "blogs", "meta_title", "created", "updated", "published", "url_type",
            "sub_title", 
            ]
        
    def get_reviews(self, obj):
        if not obj:
            return None
        
        products = obj.products.all()

        reviews_slug = []

        for product in products:
            product_reviews_slug = product.reviews.values_list("slug", flat=True)

            reviews_slug += product_reviews_slug

        reviews = Review.objects.filter(slug__in = reviews_slug)

        serializer = ReviewSerializer(reviews, many=True)

        return serializer.data
        
    def get_rating(self, obj):
        if not obj:
            return None
        
        products = obj.products.all()

        highest_rating = (max(products, key=lambda p: p.rating)).rating        

        return highest_rating if highest_rating else 0
    
    def get_rating_count(self, obj):
        if not obj:
            return None
        
        products = obj.products.all()

        highest_rating_count = (max(products, key=lambda p: p.rating)).rating_count

        return highest_rating_count if highest_rating_count else 0
    
    def get_blogs(self, obj):
        if not obj:
            return None
        
        products = obj.products.all()

        blogs_slug = []

        for product in products:
            product_blogs_slug = product.blogs.values_list("slug", flat=True)

            blogs_slug += product_blogs_slug

        blogs = Blog.objects.filter(slug__in = blogs_slug)

        serializer = BlogSerializer(blogs, many=True)

        return serializer.data
    
    def get_published(self, obj):
        if not obj:
            return None
        
        return datetime.strftime(obj.created, "%d-%b-%Y")
    

class ProductSubCategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    blogs = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = [
            "name", "slug", "updated", "image_url", "category_name", 
            "category_slug", "testimonials", "blogs"
            ]
        
    read_only_fields = "__all__"

    def get_blogs(self, obj):

        blogs = Blog.objects.filter(product__sub_category = obj)
        serializer = BlogSerializer(blogs, many=True)

        return serializer.data
    
    def get_testimonials(self, obj):

        reviews = Review.objects.filter(company = obj.company, product__sub_category = obj)

        serializer = ReviewSerializer(reviews, many=True)

        return serializer.data

    def get_image_url(self, obj):
        request = self.context.get('request')

        product = obj.products.filter(image__isnull = False).first()

        if product and product.image and hasattr(product.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(product.image.url)
            return f"{settings.SITE_URL}{product.image.url}"
        
        return None


class ProductCategorySerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    sub_categories = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()
    blogs = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "details", "name", "slug", "sub_categories", "testimonials", "blogs", 
            "updated", "image_url"
            ]

    read_only_fields = "__all__"

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
    
    def get_blogs(self, obj):

        blogs = Blog.objects.filter(product__category = obj)
        serializer = BlogSerializer(blogs, many=True)

        return serializer.data
    
    def get_testimonials(self, obj):

        reviews = Review.objects.filter(company = obj.company, product__category = obj)

        serializer = ReviewSerializer(reviews, many=True)

        return serializer.data
    
    def get_image_url(self, obj):
        request = self.context.get('request')

        product = obj.products.filter(image__isnull = False).first()

        if product and product.image and hasattr(product.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(product.image.url)
            return f"{settings.SITE_URL}{product.image.url}"
        
        return None
    

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
        fields = ["company", "name", "phone", "email", "product", "state"]
        extra_kwargs = {
            'company': {'required': False},  # Typically set server-side
            'name': {'required': True},
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
        string_fields = ['name']
        
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