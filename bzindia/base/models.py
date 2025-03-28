from django.db import models
from django.utils.text import slugify

class MetaTag(models.Model):
    name = models.CharField(max_length=150)

    slug = models.SlugField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)

            slug = base_slug
            count = 1

            while MetaTag.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"

                count += 1

            self.slug = slug     

        super().save(*args, **kwargs)

    class Meta:
        db_table = "meta_tags"
        ordering = ["name"]