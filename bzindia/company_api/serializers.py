from rest_framework import serializers
from django.conf import settings

from company.models import Company, CompanyType, Client, ContactEnquiry, Testimonial, Banner

from blog_api.serializers import BlogSerializer
from meta_api.serializers import MetaTagSerializer
from custom_pages_api.serializers import FaqSerializer
from locations.models import UniqueState

from utility.text import clean_string

class ClientSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ["id","name", "image_url", "slug"]

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
    company_rating = serializers.SerializerMethodField()

    class Meta:
        model = Testimonial
        fields = ["id",
            "name", "image_url", "slug", "client_company", "place_name",
            "text", "rating", "company_rating"
            ]
        
    
    def get_company_rating(self, obj):
        from django.db.models import Avg

        if not obj.company:
            return 0
        
        testimonials = obj.company.testimonials.values_list("rating", flat=True)

        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0
        
    

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        return None
    

class MiniCompanySerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    type_slug = serializers.CharField(source = "type.slug", read_only=True)    
    company_type = serializers.CharField(source = "type.name", read_only=True)    

    class Meta:
        model = Company 
        fields = ["id",
            "name", "logo_url", "description", 
            "slug", "summary", "get_absolute_url",  
            "company_type", "meta_title",
            "meta_description", "type_slug",
            "slug"
        ]

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and hasattr(obj.logo, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.logo.url)
            return f"{settings.SITE_URL}{obj.logo.url}"
        return None
    

class NavbarCompanySerializer(serializers.ModelSerializer):
    detail_pages = serializers.SerializerMethodField()

    class Meta:
        model = Company 
        fields = ["id", "name", "slug", "detail_pages"]

    
    def get_detail_pages(self, obj):        

        if not obj.type:
            return None
        
        if obj.type.name == "Education":
            detail_pages = obj.course_details.order_by("?")[:32]

            return [{
                "title": page.course.name,
                "slug": page.slug,
                "url": f'/{page.company.slug}/{page.course.program.slug}/{page.course.specialization.slug}/{page.slug}'
            } for page in detail_pages]
        
        elif obj.type.name == "Service":
            detail_pages = obj.service_details.order_by("?")[:32]

            return [{
                "title": page.service.name,
                "slug": page.slug,
                "url": f'/{page.company.slug}/{page.service.category.slug}/{page.service.sub_category.slug}/{page.slug}'
            } for page in detail_pages]
        
        elif obj.type.name == "Product":
            detail_pages = obj.product_details.order_by("?")[:32]

            return [{
                "title": page.product.name,
                "slug": page.slug,
                "url": f'/{page.company.slug}/{page.product.category.slug}/{page.product.sub_category.slug}/{page.slug}'
            } for page in detail_pages]
        
        elif obj.type.name == "Registration" and obj.registration_details:
            detail_pages = obj.registration_details.order_by("?")[:32]

            return [{
                "title": page.registration.title,
                "slug": page.slug,
                "url": f'/{page.company.slug}/{page.registration.registration_type.slug}/{page.registration.sub_type.slug}/{page.slug}'
            } for page in detail_pages]
        
        else: return None


class CompanySerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    favicon_url = serializers.SerializerMethodField()
    company_type = serializers.CharField(source = "type.name", read_only=True)    
    blogs = BlogSerializer(many=True, read_only=True)
    faqs = FaqSerializer(many=True, read_only = True)
    meta_tags = MetaTagSerializer(many=True, read_only = True)
    clients = ClientSerializer(many=True, read_only=True)
    type_slug = serializers.CharField(source = "type.slug", read_only=True)    
    detail_pages = serializers.SerializerMethodField()
    # multipages = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    items_url = serializers.SerializerMethodField()

    class Meta:
        model = Company 
        fields = ["id",
            "name", "logo_url", "description" , "categories", 
            "get_absolute_url", "slug", "summary",  
            "company_type", "footer_content", "meta_title",
            "phone1", "phone2", "blogs", "faqs", "whatsapp", 
            "email", "meta_tags", "meta_description", 
            "favicon_url", "price_range", "phone",
            "created", "updated", "clients", "rating",
            "sub_type", "type_slug", "detail_pages", 
            # "multipages",
            "items_url"
        ]

    read_only_fields = "__all__"

    def get_phone(self, obj):
        first_contact_obj_of_company = obj.contacts.first()

        if first_contact_obj_of_company:
            return first_contact_obj_of_company.mobile or first_contact_obj_of_company.tel or None
        
        return None

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
    
    def get_detail_pages(self, obj):
        from educational.models import CourseDetail
        from service.models import ServiceDetail
        from product.models import ProductDetailPage
        from registration.models import RegistrationDetailPage

        if not obj.type:
            return None
        
        if obj.type.name == "Education":
            detail_pages = CourseDetail.objects.filter(company = obj).order_by("course__name")

            return [{
                "title": page.course.name,
                "slug": page.slug,
                "url": f'/{page.company.slug}/{page.course.program.slug}/{page.course.specialization.slug}/{page.slug}'
            } for page in detail_pages]
        
        elif obj.type.name == "Service":
            detail_pages = ServiceDetail.objects.filter(company = obj).order_by("service__name")

            return [{
                "title": page.service.name,
                "slug": page.slug,
                "url": f'/{page.company.slug}/{page.service.category.slug}/{page.service.sub_category.slug}/{page.slug}'
            } for page in detail_pages]
        
        elif obj.type.name == "Product":
            detail_pages = ProductDetailPage.objects.filter(company = obj).order_by("product__name")

            return [{
                "title": page.product.name,
                "slug": page.slug,
                "url": f'/{page.company.slug}/{page.product.category.slug}/{page.product.sub_category.slug}/{page.slug}'
            } for page in detail_pages]
        
        elif obj.type.name == "Registration":
            detail_pages = RegistrationDetailPage.objects.filter(company = obj).order_by("registration__title")

            return [{
                "title": page.registration.title,
                "slug": page.slug,
                "url": f'/{page.company.slug}/{page.registration.registration_type.slug}/{page.registration.sub_type.slug}/{page.slug}'
            } for page in detail_pages]
        
        else: return None        

    def get_items_url(self, obj):        
        if not obj.type:
            return None
        
        if obj.type.name == "Education":
            return "courses"            
        
        elif obj.type.name == "Service":
            return "services"
        
        elif obj.type.name == "Product":
            return "products"
        
        elif obj.type.name == "Registration":
            return "registrations"
        
        else: return None
    

class CompanyTypeSerializer(serializers.ModelSerializer):
    companies = CompanySerializer(many=True, read_only=True)    

    class Meta:
        model = CompanyType
        fields = ["id","name", "slug", "companies", "categories"]


class NavbarCompanyTypeSerializer(serializers.ModelSerializer):
    companies = NavbarCompanySerializer(many=True, read_only=True)    

    class Meta:
        model = CompanyType
        fields = ["id","name", "slug", "companies"]

    
class MiniCompanyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyType
        fields = ["id","name"]


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
        fields = ["id","company", "name", "phone", "email", "state", "message"]
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
        string_fields = ["id",'name', 'message']
        
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
    

class BannerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ["id","title", "description", "link", "image_url", "slug"]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        return None