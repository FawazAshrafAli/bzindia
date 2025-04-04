from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.db.models import Avg
from django.utils import timezone
from datetime import datetime, timedelta

from company.models import Company
from locations.models import UniquePlace, UniqueDistrict, UniqueState
from base.models import MetaTag


class Program(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=150)    

    slug = models.SlugField(null=True, blank=True, max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.company.name}")
            slug = base_slug
            count = 1

            while Program.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        db_table = "course_programs"
        ordering = ["name"]

    @property
    def sub_categories(self):
        return Specialization.objects.filter(program = self).values("name", "slug")


class Specialization(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=150)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    slug = models.SlugField(null=True, blank=True, max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.program.name}-{self.company.name}")
            slug = base_slug
            count = 1

            while Specialization.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "specializations"
        ordering = ["name"]


class Course(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    image = models.ImageField(upload_to="course/", null=True, blank=True)
    name = models.CharField(max_length=150)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    mode = models.CharField(max_length=150)
    duration = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    subtitles = models.TextField(null=True, blank=True)
    meta_tags = models.TextField()
    meta_description = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.program.name}-{self.specialization.name}-{self.company.name}")
            slug = base_slug
            count = 1

            while Specialization.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.program} in {self.specialization}"
    
    class Meta:
        db_table = "courses"
        ordering = ["name"]

    @property
    def get_image_name(self):
        if self.image:
            return self.image.name.replace('course/', '')
        return None

    @property
    def description(self):
        try:
            detail_page = CourseDetail.objects.get(course = self)

            return detail_page.summary
        
        except CourseDetail.DoesNotExist:
            return ""
        
    @property
    def rating(self):
        testimonials = Testimonial.objects.filter(course = self).values_list("rating", flat=True)        
        
        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0

    @property
    def rating_count(self):
        return Testimonial.objects.filter(course = self).count()
    
    @property
    def starting_date(self):
        today = timezone.now().date()

        starting_year = today.year
        starting_month = 6
        starting_day = 1

        if today.month >= 6:
            starting_year += 1
            starting_month = 1

        row_starting_date = f"{starting_day}/{starting_month}/{starting_year}"

        starting_date = datetime.strptime(row_starting_date, "%d/%m/%Y")

        return starting_date
    
    @property
    def ending_date(self):
        starting_date = self.starting_date
        duration_in_days = self.duration * 30

        ending_date = starting_date + timedelta(days=duration_in_days)

        return ending_date



         

class Feature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    feature = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "features"
        ordering = ["created"]


class VerticalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "vertical_bullets"
        ordering = ["created"]
    

class VerticalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(VerticalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "vertical_tabs"
        ordering = ["created"]


class HorizontalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "horizontal_bullets"
        ordering = ["created"]


class HorizontalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(HorizontalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "horizontal_tabs"
        ordering = ["created"]

class TableData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    data = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "table_data"
        ordering = ["created"]


class Table(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    datas = models.ManyToManyField(TableData)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "table"
        ordering = ["created"]



class BulletPoints(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    bullet_point = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "bullet_points"
        ordering = ["created"]


class Tag(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    tag = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_tags"
        ordering = ["created"]


class Timeline(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    summary = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "timelines"
        ordering = ["created"]


class CourseDetail(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    summary = models.TextField()
    description = RichTextField()

    meta_title = models.CharField(max_length=100)
    meta_tags = models.ManyToManyField(MetaTag)
    meta_description = models.TextField()

    features = models.ManyToManyField(Feature)

    # Verical Tab
    vertical_title = models.CharField(max_length=250, null=True, blank=True)
    vertical_tabs = models.ManyToManyField(VerticalTab)

    # Horizontal Tab
    horizontal_title = models.CharField(max_length=250, null=True, blank=True)
    horizontal_tabs = models.ManyToManyField(HorizontalTab)

    # Table
    table_title = models.CharField(max_length=250, null=True, blank=True)
    tables = models.ManyToManyField(Table)

    # Bullet Point
    bullet_title = models.CharField(max_length=250, null=True, blank=True)
    bullet_points = models.ManyToManyField(BulletPoints)

    # Tag
    tag_title = models.CharField(max_length=250, null=True, blank=True)
    tags = models.ManyToManyField(Tag)

    # Timeline
    timeline_title = models.CharField(max_length=250, null=True, blank=True)
    timelines = models.ManyToManyField(Timeline)

    hide_features = models.BooleanField(default=False)
    hide_vertical_tab = models.BooleanField(default=False)
    hide_horizontal_tab = models.BooleanField(default=False)
    hide_table = models.BooleanField(default=False)
    hide_bullets = models.BooleanField(default=False)
    hide_tags = models.BooleanField(default=False)
    hide_timeline = models.BooleanField(default=False)

    hide_support_languages = models.BooleanField(default=False)

    slug = models.SlugField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = f"{self.course.name} - {self.company.name}"

        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.course.name}")
            slug = base_slug
            count = 1

            while CourseDetail.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_details"
        ordering = ["created"]

    @property
    def get_data(self):        
        rows = []
        tables = self.tables.all()

        for table in tables:
            data = [data.data for data in table.datas.all()]
            rows.append(data)

        transposed_data = list(map(list, zip(*rows)))

        return transposed_data

    @property
    def get_meta_tags(self):
        if not self.meta_tags:
            return ""

        tag_list = [tag.name for tag in self.meta_tags.all()]

        return ", ".join(tag_list)
    
    @property
    def toc(self):
        options = {
            self.vertical_title: self.hide_vertical_tab,
            self.horizontal_title: self.hide_vertical_tab,
            self.table_title: self.hide_table,
            self.bullet_title: self.hide_bullets,
            self.tag_title: self.hide_tags,
            self.timeline_title: self.hide_timeline
        }

        toc = [title for title, hidden in options.items() if not hidden]

        return toc



class Enquiry(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="course_enquiry_company")

    name = models.CharField(max_length=250)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, related_name="course_state")
    message = models.TextField()

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.course.name}-{self.email}")
            slug = base_slug

            count = 1
            while Enquiry.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}-{self.email}"
    
    class Meta:
        db_table = "course_enquiries"
        ordering = ["-created"]


class Faq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="faq_company")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    dynamic_place_rendering = models.BooleanField(default=False)

    question = models.TextField()
    answer = models.TextField()

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.course.name}")
            slug = base_slug

            count = 1
            while Faq.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_faqs"
        ordering = ["-created"]


class Testimonial(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to="student_testimonials/")

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    place = models.ForeignKey(UniquePlace, on_delete=models.CASCADE)

    text = models.TextField()
    rating = models.PositiveIntegerField(default=5)

    order = models.PositiveIntegerField(default=0)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.name}-{self.course.name}-{self.place.name}")

            slug = base_slug
            count = 1

            while Testimonial.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.name}-{self.course.name}-{self.place.name}"

    class Meta:
        db_table = "student_testimonials"
        ordering = ["created"]

    @property
    def get_image_name(self):
        if self.image:
            return f"{self.image.name}".replace('student_testimonials/', '')
        return None
    
    @property
    def rating_range(self):
        return range(5)
    

class MultiPageFeature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    feature = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_multipage_features"
        ordering = ["created"]


class MultiPageVerticalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_multipage_vertical_bullets"
        ordering = ["created"]
    

class MultiPageVerticalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(MultiPageVerticalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_multipage_vertical_tabs"
        ordering = ["created"]


class MultiPageHorizontalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_multipage_horizontal_bullets"
        ordering = ["created"]


class MultiPageHorizontalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(MultiPageHorizontalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_multipage_horizontal_tabs"
        ordering = ["created"]

class MultiPageTableData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    data = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_multipage_table_data"
        ordering = ["created"]


class MultiPageTable(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    datas = models.ManyToManyField(MultiPageTableData)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_multipage_table"
        ordering = ["created"]    


class MultiPageBulletPoints(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    bullet_point = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_multipage_bullet_points"
        ordering = ["created"]


class MultiPageTag(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    tag = models.CharField(max_length=250)
    # link = models.URLField(max_length=200)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_multipage_tags"
        ordering = ["created"]


class MultiPageTimeline(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    summary = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_multipage_timelines"
        ordering = ["created"]


class MultiPageFaq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    question = models.CharField(max_length=250)
    answer = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_multipage_faqs"
        ordering = ["created"]


class MultiPage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    summary = models.TextField(null=True, blank=True)
    description = RichTextField()

    meta_title = models.CharField(max_length=100)
    meta_tags = models.ManyToManyField(MetaTag)
    meta_description = models.TextField()

    url_type = models.CharField(max_length=50, default="slug_filtered")

    features = models.ManyToManyField(MultiPageFeature)

    # Verical Tab
    vertical_title = models.CharField(max_length=250, null=True, blank=True)
    vertical_tabs = models.ManyToManyField(MultiPageVerticalTab)

    # Horizontal Tab
    horizontal_title = models.CharField(max_length=250, null=True, blank=True)
    horizontal_tabs = models.ManyToManyField(MultiPageHorizontalTab)

    # Table
    table_title = models.CharField(max_length=250, null=True, blank=True)
    tables = models.ManyToManyField(MultiPageTable)

    # Bullet Point
    bullet_title = models.CharField(max_length=250, null=True, blank=True)
    bullet_points = models.ManyToManyField(MultiPageBulletPoints)

    # Tag
    tag_title = models.CharField(max_length=250, null=True, blank=True)
    tags = models.ManyToManyField(MultiPageTag)

    # Timeline
    timeline_title = models.CharField(max_length=250, null=True, blank=True)
    timelines = models.ManyToManyField(MultiPageTimeline)

    # Faqs
    faqs = models.ManyToManyField(MultiPageFaq)

    hide_features = models.BooleanField(default=False)
    hide_vertical_tab = models.BooleanField(default=False)
    hide_horizontal_tab = models.BooleanField(default=False)
    hide_table = models.BooleanField(default=False)
    hide_bullets = models.BooleanField(default=False)
    hide_tags = models.BooleanField(default=False)
    hide_timeline = models.BooleanField(default=False)
    hide_faqs = models.BooleanField(default=False)

    slug = models.SlugField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = f"{self.course.name} - {self.company.name}"

        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.course.name}")
            slug = base_slug
            count = 1

            while MultiPage.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_multipages"
        ordering = ["created"]

    @property
    def get_data(self):        
        rows = []
        tables = self.tables.all()

        for table in tables:
            data = [data.data for data in table.datas.all()]
            rows.append(data)

        transposed_data = list(map(list, zip(*rows)))

        return transposed_data
    
    @property
    def get_meta_tags(self):
        if not self.meta_tags:
            return ""

        tag_list = [tag.name for tag in self.meta_tags.all()]

        return ", ".join(tag_list)
