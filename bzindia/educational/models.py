from django.db import models
from django.utils.text import slugify

from company.models import Company

class Program(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=150)    

    slug = models.SlugField(null=True, blank=True, max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.company.name}")
            slug = base_slug
            count = 1

            while Program.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        db_table = "course_programs"
        ordering = ["name"]


class Specialization(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=150)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    slug = models.SlugField(null=True, blank=True, max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.program.name}-{self.company.name}")
            slug = base_slug
            count = 1

            while Specialization.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "specializations"
        ordering = ["name"]


class Course(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=150)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    mode = models.CharField(max_length=150)
    duration = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    slug = models.SlugField(null=True, blank=True, max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.program.name}-{self.specialization.name}-{self.company.name}")
            slug = base_slug
            count = 1

            while Specialization.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.program} in {self.specialization}"
    
    class Meta:
        db_table = "courses"
        ordering = ["name"]
