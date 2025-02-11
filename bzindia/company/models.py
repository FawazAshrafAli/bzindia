from django.db import models
from django.utils.text import slugify
from locations.models import UniquePlace

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


class Client(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to="clients/")
    order = models.PositiveIntegerField(default=0)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.name}")

            slug = base_slug
            count = 1

            while Client.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.name}"

    class Meta:
        db_table = "clients"
        ordering = ["name"]


class Testimonial(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="testimonial_company")

    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to="testimonials/")

    client_company = models.CharField(max_length=250)
    place = models.ForeignKey(UniquePlace, on_delete=models.CASCADE, related_name="testimonial_place")

    text = models.TextField()
    rating = models.PositiveIntegerField(default=5)

    order = models.PositiveIntegerField(default=0)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.name}-{self.client_company}-{self.place.name}")

            slug = base_slug
            count = 1

            while Testimonial.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.name}-{self.client_company}-{self.place.name}"

    class Meta:
        db_table = "testimonials"
        ordering = ["created"]

    @property
    def get_image_name(self):
        if self.image:
            return f"{self.image.name}".replace('testimonials/', '')
        return None
    

class MultiPage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="multi_page_company")

    text = models.TextField()

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.company.name)

            slug = base_slug
            count = 1

            while MultiPage.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.company.name

    class Meta:
        db_table = "multipages"
        ordering = ["created"]

    @property
    def get_content(self):
        if self.text:
            content = self.text

            replacing_data = {
                'state_name': "Kerala",
                'district_name': "Malappuram",
                "block_name": "Perinthalmanna",                
            }

            for key, value in replacing_data.items():
                content = content.replace(key, value)
            
            return content
        
        return None