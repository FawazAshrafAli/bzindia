from django.db import models
from django.utils.text import slugify

from company.models import Company

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

    name = models.CharField(max_length=250)    
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    description = models.TextField(null=True, blank=True)

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
    
