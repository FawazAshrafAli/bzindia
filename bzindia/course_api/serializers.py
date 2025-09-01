from rest_framework import serializers
from django.conf import settings
from datetime import datetime

from utility.text import clean_string

from educational.models import  (
    Course, Testimonial, Faq, Enquiry, Program, CourseDetail,
    Feature, VerticalTab, HorizontalTab, Table, BulletPoints, 
    Timeline, VerticalBullet, HorizontalBullet,

    MultiPage, MultiPageFaq, MultiPageFeature, MultiPageBulletPoints,
    MultiPageHorizontalBullet, MultiPageHorizontalTab,
    MultiPageTable, MultiPageTimeline, MultiPageVerticalTab,
    MultiPageVerticalBullet,

    Specialization
    )
from locations.models import UniqueState
from company.models import Company
from company_api.serializers import CompanySerializer
from blog_api.serializers import BlogSerializer
from custom_pages_api.serializers import FaqSerializer
from meta_api.serializers import MetaTagSerializer

from .paginations import CoursePagination

class MiniCourseSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    program_name = serializers.CharField(source='program.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)     

    class Meta:
        model = Course
        fields = ["id",
            "name", "program_name", "image_url",
            "company_name", "mode", 
            "starting_date", "ending_date", "duration",
            "price", "rating", "rating_count"          
            ]
        
        read_only_fields = fields

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        return None
    

class CourseSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    program_name = serializers.CharField(source='program.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_sub_type = serializers.CharField(source='company.sub_type', read_only=True)
    company_slug = serializers.CharField(source='company.slug', read_only=True)
    program_slug = serializers.CharField(source='program.slug', read_only=True)
    specialization_slug = serializers.CharField(source='specialization.slug', read_only=True)
    specialization_name = serializers.CharField(source='specialization.name', read_only=True)

    class Meta:
        model = Course
        fields = ["id",
            "name", "program_name", "image_url", "company_sub_type",
            "description", "company_name", "company_slug", "mode", 
            "starting_date", "ending_date", "duration", "program_slug",
            "price", "rating", "rating_count", "slug", "specialization_slug",
            "specialization_name"
            ]
        
        read_only_fields = fields

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
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


class StudentTestimonialSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    course_name = serializers.CharField(source = "course.name", read_only=True)
    place_name = serializers.CharField(source = "place.name", read_only=True)

    class Meta:
        model = Testimonial
        fields = ["id","name", "image_url", "course_name", "place_name", "text", "rating", "slug"]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        return


class CourseFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ["id","question", "answer", "slug"]

    
class MiniCourseDetailSerializer(serializers.ModelSerializer):    
    course = MiniCourseSerializer()        
    url = serializers.SerializerMethodField()

    class Meta:
        model = CourseDetail
        fields = ["id",
            "meta_description","course","url"
            ]
        
    def get_url(self, obj):
        try:
            company_slug = obj.company.slug
            program_slug = obj.course.program.slug
            specialization_slug = obj.course.specialization.slug
            slug = obj.slug
        except AttributeError:
            return None

        return f"{company_slug}/{program_slug}/{specialization_slug}/{slug}"
        

class DetailSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    features = FeatureSerializer(many=True)
    vertical_tabs = VerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = HorizontalTabSerializer(many=True, read_only=True)
    tables = TableSerializer(many=True, read_only=True)
    bullet_points = BulletPointSerializer(many=True, read_only=True)    
    timelines = TimelineSerializer(many=True, read_only=True)
    faqs = CourseFaqSerializer(many=True, read_only=True)
    testimonials = StudentTestimonialSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)
    item_name = serializers.CharField(source="course.name", read_only = True)
    company_slug = serializers.CharField(source="company.slug", read_only = True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = CourseDetail
        fields = ["id",
            "meta_title", "meta_description", "company_slug",
            "summary", "description", "features", "course", "slug",
            "vertical_title", "horizontal_title", "vertical_tabs", 
            "horizontal_tabs", "table_title", "tables", "get_data",
            "bullet_title", "bullet_points",
            "timeline_title", "timelines", "toc", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_timeline", "hide_support_languages",
            "faqs", "testimonials", "meta_tags", "published",
            "modified", "item_name", "created", "updated", "url"
            ]
        
    def get_url(self, obj):
        try:
            company_slug = obj.company.slug
            program_slug = obj.course.program.slug
            specialization_slug = obj.course.specialization.slug
            slug = obj.slug
        except AttributeError:
            return None

        return f"{company_slug}/{program_slug}/{specialization_slug}/{slug}"


class EnquirySerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    course = serializers.SlugRelatedField(
        queryset=Course.objects.all(),
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
        fields = ["id","company", "name", "phone", "email", "course", "state"]
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
            self.fields['course'].queryset = Course.objects.filter(
                company__slug=company_slug,
                is_active=True  # Example of additional filtering
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
    

class ProgramSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()
    blogs = BlogSerializer(many=True, read_only=True)
    detail_pages = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = ["id","name", "slug", "courses", "blogs", "detail_pages", "testimonials", "updated"]

    def get_testimonials(self, obj):

        courses = obj.courses.all()

        testimonials = Testimonial.objects.filter(course__in = courses)
        serializer = StudentTestimonialSerializer(testimonials, many=True)

        return serializer.data

    def get_courses(self, obj):
        request = self.context.get("request")
        courses_qs = obj.courses.all()

        paginator = CoursePagination()
        paginated_qs = paginator.paginate_queryset(courses_qs, request)

        serializer = CourseSerializer(paginated_qs, many=True, context={"request": request})
        return {
            "count": courses_qs.count(),
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": serializer.data,
        }
    
    def get_detail_pages(self, obj):
        if not obj:
            return None
        
        details = CourseDetail.objects.filter(course__program = obj)

        return DetailSerializer(details, many=True).data
    

class SpecializationSerializer(serializers.ModelSerializer):
    program = ProgramSerializer(many=False)
    image_url = serializers.SerializerMethodField()
    blogs = serializers.SerializerMethodField()

    class Meta:
        model = Specialization
        fields = ["id","name", "slug", "program", "updated", "image_url", "blogs", "updated"]

    read_only_fields = "__all__"

    def get_image_url(self, obj):
        request = self.context.get('request')

        course = Course.objects.filter(specialization = obj, image__isnull = False).first()

        if course and course.image and hasattr(course.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(course.image.url)
            return f"{settings.SITE_URL}{course.image.url}"
        return None

    def get_blogs(self, obj):
        from blog.models import Blog

        blogs = Blog.objects.filter(course__specialization = obj)
        serializer = BlogSerializer(blogs, many=True)

        return serializer.data
    

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
        model = MultiPageBulletPoints
        fields = ["id",
            "id", "bullet_point"
            ]
        

class MultiPageFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageFaq
        fields = ["id",
            "question", "answer", "slug"
        ]
        

class MultipageTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageTimeline
        fields = ["id",
            "id", "heading", "summary"
            ]

class MultiPageSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    company_name = serializers.CharField(source="company.name", read_only=True)
    company_slug = serializers.CharField(source="company.slug", read_only=True)
    features = MultipageFeatureSerializer(many=True)
    vertical_tabs = MultipageVerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = MultipageHorizontalTabSerializer(many=True, read_only=True)
    tables = MultipageTableSerializer(many=True, read_only=True)
    bullet_points = MultipageBulletPointSerializer(many=True, read_only=True)    
    tags = serializers.SerializerMethodField()
    timelines = MultipageTimelineSerializer(many=True, read_only=True)
    blogs = BlogSerializer(many=True, read_only=True)
    faqs = MultiPageFaqSerializer(many=True, read_only=True)
    testimonials = StudentTestimonialSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)

    slider_courses = DetailSerializer(many=True)

    class Meta:
        model = MultiPage
        fields = ["id",
            "title", "summary", "description", "slider_courses", "features", "slug",
            "vertical_title", "horizontal_title", "vertical_tabs", 
            "horizontal_tabs", "table_title", "tables", "get_data",
            "bullet_title", "bullet_points", "tags",
            "timeline_title", "timelines", "toc", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_timeline", "hide_support_languages",
            "blogs", "faqs", "testimonials", "url_type", "meta_tags", 
            "published", "modified", "meta_description", "company_name",
            "company_slug", "course", "sub_title", "meta_title",
            "updated", "created"
            ]
        
    read_only_fields = "__all___"
        
    def get_tags(self, obj):
        if not obj.meta_tags:
            return None
        
        meta_tags = obj.meta_tags.all()

        serializer = MetaTagSerializer(meta_tags)

        return serializer.data