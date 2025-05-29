from rest_framework import serializers
from django.conf import settings

from utility.text import clean_string

from educational.models import  (
    Course, Testimonial, Faq, Enquiry, Program, CourseDetail,
    Feature, VerticalTab, HorizontalTab, Table, BulletPoints, 
    Tag, Timeline, VerticalBullet, HorizontalBullet,

    MultiPage, MultiPageFaq, MultiPageFeature, MultiPageBulletPoints,
    MultiPageHorizontalBullet, MultiPageHorizontalTab, MultiPageTag,
    MultiPageTable, MultiPageTimeline, MultiPageTableData, MultiPageVerticalTab,
    MultiPageVerticalBullet
    )
from locations.models import UniqueState
from company.models import Company
from company_api.serializers import CompanySerializer
from blog_api.serializers import BlogSerializer
from custom_pages_api.serializers import FaqSerializer
from meta_api.serializers import MetaTagSerializer

from .paginations import CoursePagination

class CourseSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    program_name = serializers.CharField(source='program.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_sub_type = serializers.CharField(source='company.sub_type', read_only=True)
    company_slug = serializers.CharField(source='company.slug', read_only=True)

    class Meta:
        model = Course
        fields = [
            "name", "program_name", "image_url", "company_sub_type",
            "description", "company_name", "company_slug", "mode", 
            "starting_date", "ending_date", "duration", 
            "price", "rating", "rating_count", "slug"]
        
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
        model = BulletPoints
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


class StudentTestimonialSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    course_name = serializers.CharField(source = "course.name", read_only=True)
    place_name = serializers.CharField(source = "place.name", read_only=True)

    class Meta:
        model = Testimonial
        fields = ["name", "image_url", "course_name", "place_name", "text", "rating", "slug"]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        return


class DetailSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    features = FeatureSerializer(many=True)
    vertical_tabs = VerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = HorizontalTabSerializer(many=True, read_only=True)
    tables = TableSerializer(many=True, read_only=True)
    bullet_points = BulletPointSerializer(many=True, read_only=True)    
    tags = TagSerializer(many=True, read_only=True)
    timelines = TimelineSerializer(many=True, read_only=True)
    blogs = BlogSerializer(many=True, read_only=True)
    faqs = FaqSerializer(many=True, read_only=True)
    testimonials = StudentTestimonialSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)
    item_name = serializers.CharField(source="course.name", read_only = True)

    class Meta:
        model = CourseDetail
        fields = [
            "summary", "description", "features", "course", "slug",
            "vertical_title", "horizontal_title", "vertical_tabs", 
            "horizontal_tabs", "table_title", "tables", "get_data",
            "bullet_title", "bullet_points", "tag_title", "tags",
            "timeline_title", "timelines", "toc", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_tags", "hide_timeline", "hide_support_languages",
            "blogs", "faqs", "testimonials", "meta_tags", "published",
            "modified", "item_name"
            ]


class CourseFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ["question", "answer", "slug"]


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
        fields = ["company", "name", "phone", "email", "course", "state", "message"]
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
            self.fields['course'].queryset = Course.objects.filter(
                company__slug=company_slug,
                is_active=True  # Example of additional filtering
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
    

class ProgramSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()
    blogs = BlogSerializer(many=True, read_only=True)
    detail_pages = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = ["name", "slug", "courses", "blogs", "detail_pages"]

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
        model = MultiPageBulletPoints
        fields = [
            "id", "bullet_point"
            ]
        

class MultipageTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageTag
        fields = [
            "id", "tag"
            ]
        

class MultiPageFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageFaq
        fields = [
            "question", "answer", "slug"
        ]
        

class MultipageTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageTimeline
        fields = [
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
    tags = MultipageTagSerializer(many=True, read_only=True)
    timelines = MultipageTimelineSerializer(many=True, read_only=True)
    blogs = BlogSerializer(many=True, read_only=True)
    faqs = MultiPageFaqSerializer(many=True, read_only=True)
    testimonials = StudentTestimonialSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)

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
            "blogs", "faqs", "testimonials", "url_type", "meta_tags", 
            "published", "modified", "meta_description", "company_name",
            "company_slug", "course"
            ]