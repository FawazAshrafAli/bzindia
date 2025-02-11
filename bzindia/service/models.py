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