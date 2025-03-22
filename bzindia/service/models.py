from django.db import models
from django.utils.text import slugify

from company.models import Company
from locations.models import UniqueState

class Category(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_category_company")

    name = models.CharField(max_length=250)
    slug = models.SlugField(blank=True, null=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.company.name}")
            slug = base_slug

            count = 1
            while Category.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name}-{self.company.name}"

    class Meta:
        db_table = "service_category"
        ordering = ["name"]

    @property
    def sub_categories(self):
        return SubCategory.objects.filter(category = self).values("name", "slug")

class SubCategory(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_sub_category_company")

    name = models.CharField(max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True, null=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.category.name}-{self.company.name}")
            slug = base_slug

            count = 1
            while SubCategory.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name}-{self.category.name}-{self.company.name}"

    class Meta:
        db_table = "service_sub_category"
        ordering = ["name"]


class Service(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_company")

    image = models.ImageField(upload_to="services/", null=True, blank=True)
    name = models.CharField(max_length=250)    
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.category.name}-{self.sub_category.name}-{self.company.name}")
            slug = base_slug

            count = 1
            while Service.objects.filter(slug = slug).exists():
                if Service.objects.filter(slug = slug).first().pk == self.pk:
                    break

                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}-{self.company.name}"
    
    class Meta:
        db_table = "services"
        ordering = ["name"]

    @property
    def get_image_name(self):
        if self.image:
            return self.image.name.replace('services/', '')
        
        return None


class Feature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_feature_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    feature = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_features"
        ordering = ["created"]


class VerticalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_vertical_bullet_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_vertical_bullets"
        ordering = ["created"]


class VerticalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_vertical_tab_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(VerticalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_vertical_tabs"
        ordering = ["created"]


class HorizontalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_horizontal_bullet_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_horizontal_bullets"
        ordering = ["created"]


class HorizontalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_horizontal_tab_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(HorizontalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_horizontal_tabs"
        ordering = ["created"]


class TableData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_table_data_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    data = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_table_data"
        ordering = ["created"]


class Table(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_table_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    datas = models.ManyToManyField(TableData)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_table"
        ordering = ["created"]    


class BulletPoints(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_bullet_points_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    bullet_point = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_bullet_points"
        ordering = ["created"]


class Tag(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_tag_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    tag = models.CharField(max_length=250)
    link = models.URLField(max_length=200)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_tags"
        ordering = ["created"]

    
class Timeline(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_timeline_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    summary = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_timelines"
        ordering = ["created"]


class ServiceDetail(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    summary = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

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

    slug = models.SlugField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.service.name}")
            slug = base_slug
            count = 1

            while ServiceDetail.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_details"
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


class Enquiry(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_enquiry_company")

    name = models.CharField(max_length=250)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE)
    message = models.TextField()

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.service.name}-{self.email}")
            slug = base_slug

            count = 1
            while Enquiry.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}-{self.email}"
    
    class Meta:
        db_table = "service_enquiries"
        ordering = ["-created"]


class Faq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_faq_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    question = models.TextField()
    answer = models.TextField()
    dynamic_place_rendering = models.BooleanField(default=False)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.service.name}")
            slug = base_slug

            count = 1
            while Faq.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_faqs"
        ordering = ["-created"]