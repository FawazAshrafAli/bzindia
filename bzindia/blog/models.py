from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from ckeditor.fields import RichTextField

from educational.models import Course
from product.models import Product
from service.models import Service
from registration.models import RegistrationSubType
from company.models import Company
from base.models import MetaTag

class Blog(models.Model):
    title = models.CharField(max_length=250)
    image = models.ImageField(upload_to="blogs/", null=True, blank=True)

    blog_type = models.CharField(max_length=150)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    registration_sub_type = models.ForeignKey(RegistrationSubType, on_delete=models.CASCADE, null=True, blank=True)

    summary = models.TextField()
    content = RichTextField()
    meta_description = models.TextField()
    
    meta_tags = models.ManyToManyField(MetaTag)

    is_published = models.BooleanField(default=False)

    published_date = models.DateTimeField(blank=True, null=True)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if self.is_published:
            self.published_date = timezone.now()
        else:
            self.published_date = None

        if not self.slug:
            topic = (
                getattr(self.course, "name", None) or
                getattr(self.product, "name", None) or
                getattr(self.service, "name", None) or
                getattr(self.registration_sub_type, "name", "")
            )

            base_slug = slugify(f"{self.title}-{self.blog_type}-{topic}")

            slug = base_slug
            count = 1

            while Blog.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = "blogs"
        ordering = ["-created"]

    @property
    def get_topic(self):
        topic = None
        if self.course:
            topic = self.course.name
        elif self.product:
            topic = self.product.name
        elif self.registration_sub_type:
            topic = self.registration_sub_type.name
        elif self.service:
            topic = self.service.name
            
        return topic
    
    @property
    def get_image_name(self):
        if self.image:
            return self.image.name.replace("blogs/", "")
        
        return None
    
    @property
    def get_object(self):
        if self.blog_type == "Education":
            return self.course.name
        elif self.blog_type == "Product":
            return self.product.name
        elif self.blog_type == "Service":
            return self.service.name
        elif self.blog_type == "Registration":
            return self.registration_sub_type.name
        else:
            return None
        
    @property
    def get_meta_tags(self):
        if not self.meta_tags.exists():
            return ""

        tag_list = [tag.name for tag in self.meta_tags.all()]

        return ", ".join(tag_list)