from django.db import models
from django.utils.text import slugify

class CompanyType(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(null=True, blank=True, max_length=175)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            count = 1
            while CompanyType.objects.filter(slug = self.slug).exists():
                self.slug = f"{base_slug}-{count}"
                count += 1

        super().save(*args, **kwargs)

    class Meta:
        db_table = "company_type"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=150)
    type = models.ForeignKey(CompanyType, on_delete=models.CASCADE)
    slug = models.SlugField(null=True, blank=True, max_length=175)
    favicon = models.ImageField(upload_to="company_favicon/", null=True, blank=True)
    logo = models.ImageField(upload_to="company_logo/", null=True, blank=True)
    phone1 = models.CharField(max_length=50)
    phone2 = models.CharField(max_length=50)
    whatsapp = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            count = 1
            while CompanyType.objects.filter(slug = self.slug).exists():
                self.slug = f"{base_slug}-{count}"
                count += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "company"
        ordering = ["name"]

