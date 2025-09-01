from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from datetime import datetime
from django.db.models import Avg

from company.models import Company
from locations.models import UniqueState
from base.models import MetaTag
from company.models import Testimonial

class RegistrationType(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            
            while RegistrationType.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}-{self.company.name}"
    
    class Meta:
        db_table = "registration_type"
        ordering = ["name"]

    @property
    def sub_categories(self):
        return RegistrationSubType.objects.filter(type = self).values("name", "slug")
    
    @property
    def detail_pages(self):
        return RegistrationDetailPage.objects.filter(registration__sub_type__type = self).values("registration__title", "slug")


class RegistrationSubType(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=250)    
    type = models.ForeignKey(RegistrationType, on_delete=models.CASCADE, related_name="registration_sub_types")
    description = models.TextField(null=True, blank=True)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            
            while RegistrationSubType.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}-{self.type.name}-{self.company.name}"
    
    class Meta:
        db_table = "registration_sub_type"
        ordering = ["name"]

    @property
    def price(self):
        registrations = Registration.objects.filter(sub_type = self, price__isnull = False)

        return registrations.first().price if registrations else None
    
    @property
    def get_absolute_url(self):
        return f'/registrations/{self.slug}'


class Registration(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="registrations")
    title = models.CharField(max_length=150, blank=True, null=True)
    image =models.ImageField(upload_to="registrations/", blank=True, null=True)

    registration_type = models.ForeignKey(RegistrationType, on_delete=models.CASCADE, null=True, blank=True, related_name="registrations")
    sub_type = models.ForeignKey(RegistrationSubType, on_delete=models.CASCADE, related_name="registrations")
    price = models.CharField(max_length=20)
    time_required = models.CharField(max_length=100, null=True, blank=True)
    required_documents = models.TextField(null=True, blank=True)
    additional_info = models.TextField(blank=True, null=True)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.sub_type.name)
            slug = base_slug
            count = 1
            
            while Registration.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.sub_type.name}"
    
    class Meta:
        db_table = "registrations"
        ordering = ["-created"]    


class Faq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="registration_faq_company")
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name="faqs")

    question = models.TextField()
    answer = models.TextField()
    dynamic_place_rendering = models.BooleanField(default=False)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.question}")
            slug = base_slug

            count = 1
            while Faq.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.registration.title}"
    
    class Meta:
        db_table = "registration_faqs"
        ordering = ["-created"]


class Enquiry(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="registration_enquiry_company")

    name = models.CharField(max_length=250)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, null=True, blank=True)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, related_name="registration_enquiry_state")

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.registration.title}-{self.email}")
            slug = base_slug

            count = 1
            while Enquiry.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.registration.title}-{self.email}"
    
    class Meta:
        db_table = "registration_enquiries"
        ordering = ["-created"]


class Feature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="registration_feature_company")
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    feature = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.registration.title}"
    
    class Meta:
        db_table = "registration_features"
        ordering = ["created"]


class VerticalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="registration_vertical_bullet_company")
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.registration.title}"
    
    class Meta:
        db_table = "registration_vertical_bullets"
        ordering = ["created"]


class VerticalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="registration_vertical_tab_company")
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    
    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(VerticalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.registration.title}"
    
    class Meta:
        db_table = "registration_vertical_tabs"
        ordering = ["created"]


class HorizontalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="registration_horizontal_bullet_company")
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.registration.title}"
    
    class Meta:
        db_table = "registration_horizontal_bullets"
        ordering = ["created"]


class HorizontalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="registration_horizontal_tab_company")
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(HorizontalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.registration.title}"
    
    class Meta:
        db_table = "registration_horizontal_tabs"
        ordering = ["created"]


class TableData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="registration_table_data_company")
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    data = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.registration.title}"
    
    class Meta:
        db_table = "registration_table_data"
        ordering = ["created"]


class Table(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="registration_table_company")
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    datas = models.ManyToManyField(TableData)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.registration.title}"
    
    class Meta:
        db_table = "registration_table"
        ordering = ["created"]    


class BulletPoint(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="registration_bullet_points_company")
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    bullet_point = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.registration.title}"
    
    class Meta:
        db_table = "registration_bullet_points"
        ordering = ["created"]

    
class Timeline(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="registration_timeline_company")
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    summary = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.registration.title}"
    
    class Meta:
        db_table = "registration_timelines"
        ordering = ["created"]


class RegistrationDetailPage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="registration_details")
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, blank=True, null=True)

    summary = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

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
    bullet_points = models.ManyToManyField(BulletPoint)

    # Timeline
    timeline_title = models.CharField(max_length=250, null=True, blank=True)
    timelines = models.ManyToManyField(Timeline)

    hide_features = models.BooleanField(default=False)
    hide_vertical_tab = models.BooleanField(default=False)
    hide_horizontal_tab = models.BooleanField(default=False)
    hide_table = models.BooleanField(default=False)
    hide_bullets = models.BooleanField(default=False)
    hide_timeline = models.BooleanField(default=False)

    hide_support_languages = models.BooleanField(default=False)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = f"{self.registration.title}"

        if not self.slug:
            base_slug = slugify(f"{self.registration.title}")
            slug = base_slug
            count = 1

            while RegistrationDetailPage.objects.filter(slug = slug).exclude(pk = self.pk).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.registration.title}"
    
    class Meta:
        db_table = "registration_detail_pages"
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
            self.horizontal_title: self.hide_horizontal_tab,
            self.table_title: self.hide_table,
            self.bullet_title: self.hide_bullets,
            self.timeline_title: self.hide_timeline
        }

        toc = [title for title, hidden in options.items() if not hidden]

        return toc
    
    @property
    def published(self):        
        if self.created:
            return datetime.strftime(self.created, "%Y-%m-%d")
        return None
    
    @property
    def modified(self):
        if self.updated:
            return datetime.strftime(self.updated, "%Y-%m-%d")
        return None
    
    @property
    def faqs(self):
        return Faq.objects.filter(company = self.company, registration = self.registration)
    
    @property
    def testimonials(self):
        return Testimonial.objects.filter(company = self.company).order_by("order")
    
    @property
    def blogs(self):
        from blog.models import Blog
        return Blog.objects.filter(company = self.company, registration = self.registration)
    
    @property
    def price(self):
        registrations = Registration.objects.filter(sub_type = self.registration, price__isnull = False)

        if registrations:
            return registrations.first().price
        
        return None
    
    @property
    def image_count(self):        
        return 0



class MultiPageFeature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_registration_multipage_feature")
    title = models.CharField(max_length = 250)

    feature = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "registration_multipage_features"
        ordering = ["created"]


class MultiPageVerticalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_registration_multipage_vertical_bullet")
    title = models.CharField(max_length = 250)

    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "registration_multipage_vertical_bullets"
        ordering = ["created"]
    

class MultiPageVerticalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="multi_vertical_tabs")
    title = models.CharField(max_length = 250)
    
    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(MultiPageVerticalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "registration_multipage_vertical_tabs"
        ordering = ["created"]


class MultiPageHorizontalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="hori_verticle_tabs")
    title = models.CharField(max_length = 250)

    heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "registration_multipage_horizontal_bullets"
        ordering = ["created"]


class MultiPageHorizontalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_registration_multipage_horizontal_tab")
    title = models.CharField(max_length = 250)

    heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(MultiPageHorizontalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "registration_multipage_horizontal_tabs"
        ordering = ["created"]

class MultiPageTableData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_registration_multipage_table_data")
    title = models.CharField(max_length = 250)

    heading = models.CharField(max_length=250)
    data = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "registration_multipage_table_data"
        ordering = ["created"]


class MultiPageTable(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="multi_tables")
    title = models.CharField(max_length = 250)

    heading = models.CharField(max_length=250)
    datas = models.ManyToManyField(MultiPageTableData)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "registration_multipage_table"
        ordering = ["created"]    


class MultiPageBulletPoint(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_registration_multipage_bullets")
    title = models.CharField(max_length = 250)

    bullet_point = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "registration_multipage_bullet_points"
        ordering = ["created"]


class MultiPageTimeline(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_registration_multipage_timeline")
    title = models.CharField(max_length = 250)

    heading = models.CharField(max_length=250)
    summary = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "registration_multipage_timelines"
        ordering = ["created"]


class MultiPageFaq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_registration_multipage_faq")
    title = models.CharField(max_length = 250)

    question = models.CharField(max_length=250)
    answer = models.TextField()

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.title}")
            slug = base_slug

            count = 1
            while MultiPageFaq.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "registration_multipage_faqs"
        ordering = ["created"]


class MultiPage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="registration_multipages")
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name="multipages")

    title = models.CharField(max_length = 250)
    sub_title = models.CharField(max_length = 250, blank=True, null=True)

    summary = models.TextField(null=True, blank=True)
    description = RichTextField()

    meta_title = models.CharField(max_length=100)
    meta_tags = models.ManyToManyField(MetaTag, related_name="registration_multipages")
    meta_description = models.TextField()

    url_type = models.CharField(max_length=50, default="slug_filtered")

    registration_region = models.CharField(max_length=250, default="all")
    available_states = models.ManyToManyField(UniqueState, related_name="registration_multipages")

    slider_registrations = models.ManyToManyField(RegistrationDetailPage)

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
    bullet_points = models.ManyToManyField(MultiPageBulletPoint)

    # Timeline
    timeline_title = models.CharField(max_length=250, null=True, blank=True)
    timelines = models.ManyToManyField(MultiPageTimeline, related_name="registration_multipage_states")

    # Faqs
    faqs = models.ManyToManyField(MultiPageFaq)

    hide_features = models.BooleanField(default=False)
    hide_vertical_tab = models.BooleanField(default=False)
    hide_horizontal_tab = models.BooleanField(default=False)
    hide_table = models.BooleanField(default=False)
    hide_bullets = models.BooleanField(default=False)
    hide_timeline = models.BooleanField(default=False)
    hide_faqs = models.BooleanField(default=False)

    hide_support_languages = models.BooleanField(default=False)
    home_footer_visibility = models.BooleanField(default=False)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = f"{self.title}"

        if not self.home_footer_visibility and not MultiPage.objects.exclude(pk=self.pk).filter(company = self.company, home_footer_visibility=True).exists():
            self.home_footer_visibility = True

        base_slug = slugify(self.title)
        slug = base_slug
        count = 1

        while MultiPage.objects.filter(slug = slug).exclude(pk = self.pk).exists():
            slug = f"{base_slug}-{count}"
            count += 1

        if self.url_type != "slug_filtered":
            slug = slug.replace("-in-place_name", "").replace("-in-district_name", "").replace("-in-state_name", "").replace("-place_name", "").replace("-district_name", "").replace("-state_name", "")

        self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "registration_multipages"
        ordering = ["created"]

    @property
    def slider_registration_type_slug(self):
        if self.slider_registrations.count() > 0:
            first_slider_registration_detail = self.slider_registrations.first()
            return first_slider_registration_detail.registration.registration_type.slug
        
        return None
    
    @property
    def slider_registration_sub_type_slug(self):
        if self.slider_registrations.count() > 0:
            first_slider_registration_detail = self.slider_registrations.first()
            return first_slider_registration_detail.registration.sub_type.slug
        
        return None

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
            self.horizontal_title: self.hide_horizontal_tab,
            self.table_title: self.hide_table,
            self.bullet_title: self.hide_bullets,
            self.timeline_title: self.hide_timeline
        }

        toc = [title for title, hidden in options.items() if not hidden]

        return toc
    
    @property
    def published(self):
        if self.created:
            return datetime.strftime(self.created, "%Y-%m-%d")
        return None
    
    @property
    def modified(self):
        if self.updated:
            return datetime.strftime(self.updated, "%Y-%m-%d")
        return None
    
    @property
    def blogs(self):
        from blog.models import Blog
        return Blog.objects.filter(company = self.company, registration = self.registration)
    
    @property
    def testimonials(self):
        return Testimonial.objects.filter(company = self.company).order_by("order")
    
    @property
    def rating(self):
        testimonials = Testimonial.objects.filter(company = self.company).values_list("rating", flat=True)        
        
        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0

    @property
    def rating_count(self):
        return Testimonial.objects.filter(company = self.company).count()
    
    @property
    def image_count(self):        
        return 0