from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.db.models import Avg, Max, Min

from locations.models import UniquePlace, UniqueState
from base.models import MetaTag

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
    
    @property
    def companies(self):
        return Company.objects.filter(type = self).values("name", "slug").order_by("name")
    
    @property
    def categories(self):
        from educational.models import Program
        from product.models import Category as ProductCategory
        from registration.models import RegistrationType
        from service.models import Category as ServiceCategory

        current_type = self.name
        Category = None

        if current_type == "Education":
            Category = Program

        elif current_type == "Product":
            Category = ProductCategory

        elif current_type == "Registration":
            Category = RegistrationType

        elif current_type == "Service":
            Category = ServiceCategory

        if Category:
            categories = Category.objects.all().order_by("name")

            return [{"name": category.name, "slug": category.slug, "sub_categories": category.sub_categories, "detail_pages": category.detail_pages} for category in categories]

        return None
    
    @property
    def companies(self):
        return Company.objects.filter(type = self).order_by("name")
    

class Company(models.Model):
    name = models.CharField(max_length=150)
    type = models.ForeignKey(CompanyType, on_delete=models.CASCADE)
    sub_type = models.CharField(max_length=250)
    slug = models.SlugField(null=True, blank=True, max_length=175)
    favicon = models.ImageField(upload_to="company_favicon/", null=True, blank=True)
    logo = models.ImageField(upload_to="company_logo/", null=True, blank=True)
    phone1 = models.CharField(max_length=50)
    phone2 = models.CharField(max_length=50)
    whatsapp = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    description = RichTextField(null=True, blank=True)

    facebook = models.URLField(max_length=500, null=True, blank=True)
    twitter = models.URLField(max_length=500, null=True, blank=True)
    linkedin = models.URLField(max_length=500, null=True, blank=True)
    youtube = models.URLField(max_length=500, null=True, blank=True)

    meta_title = models.CharField(max_length=100)
    meta_tags = models.ManyToManyField(MetaTag)
    meta_description = models.TextField()

    footer_content = RichTextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.meta_title:
            self.meta_title = f"Home - {self.name}"

        if not self.slug:
            # base_slug = slugify(self.name)
            base_slug = slugify(self.sub_type)
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

    @property
    def categories(self):
        from educational.models import Program
        from product.models import Category as ProductCategory
        from registration.models import RegistrationType
        from service.models import Category as ServiceCategory

        company_type = self.type.name
        Category = None

        if company_type == "Education":
            Category = Program

        elif company_type == "Product":
            Category = ProductCategory

        elif company_type == "Registration":
            Category = RegistrationType

        elif company_type == "Service":
            Category = ServiceCategory

        if Category:
            return Category.objects.filter(company = self).values("name", "slug").order_by("name")

        return None    

    @property
    def get_meta_tags(self):
        if not self.meta_tags:
            return ""

        tag_list = [tag.name for tag in self.meta_tags.all()]

        return ", ".join(tag_list)
    
    @property
    def social_media_links(self):
        social_media_fields = [self.facebook, self.twitter, self.linkedin, self.youtube]        
        
        return [link for link in social_media_fields if link and link != "None"]

    @property
    def rating(self):
        TestimonialModel = Testimonial
        if self.type == "Education":
            from educational.models import Testimonial as CourseTestimonial

            TestimonialModel = CourseTestimonial

        testimonials = TestimonialModel.objects.filter(company = self).values_list("rating", flat=True)        
        
        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0
    
    @property
    def get_absolute_url(self):
        return f'https://bzindia.in/{self.slug}'

    @property
    def blogs(self):
        from blog.models import Blog

        return Blog.objects.filter(company = self, is_published = True)
    
    @property
    def faqs(self):
        from custom_pages.models import FAQ

        return FAQ.objects.filter(company = self)
    
    @property
    def price_range(self):
        from educational.models import Course
        from product.models import Product
        from registration.models import Registration
        from service.models import Service

        if self.type == "Education":
            prices = Course.objects.filter(company=self.company).aggregate(
                min_price=Min("price"),
                max_price=Max("price")
            )

            if prices["min_price"] is not None:
                if prices["min_price"] == prices["max_price"]:
                    return prices["min_price"]
                return f"{prices['min_price']} - {prices['max_price']}"
            
        return None
    
    @property
    def clients(self):
        if self.type.name != "Education":
            return Client.objects.filter(company = self)
        
        return []


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
    
    
class ContactEnquiry(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="contact_enquiry_company")

    name = models.CharField(max_length=250)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, related_name="contact_state")
    message = models.TextField()

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.email}")
            slug = base_slug

            count = 1
            while ContactEnquiry.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.email}"
    
    class Meta:
        db_table = "contact_enquiries"
        ordering = ["-created"]