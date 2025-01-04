from django.db import models
from django.utils.text import slugify

from company.models import Company

class RegistrationType(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.company.name}")
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


class RegistrationSubType(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=250)
    type = models.ForeignKey(RegistrationType, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.type.name}-{self.company.name}")
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


class RegistrationDetail(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    sub_type = models.ForeignKey(RegistrationSubType, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    time_required = models.CharField(max_length=100, null=True, blank=True)
    required_documents = models.TextField(null=True, blank=True)
    additional_info = models.TextField(blank=True, null=True)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.sub_type.name}-{self.company.name}")
            slug = base_slug
            count = 1
            
            while RegistrationDetail.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.sub_type.name}"
    
    class Meta:
        db_table = "registration_detail"
        ordering = ["-created"]