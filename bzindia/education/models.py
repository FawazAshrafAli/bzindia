from django.db import models
from django.utils.text import slugify

from company.models import Company

class CourseProgram(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=150)    

    slug = models.SlugField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        db_table = "course_programs"
        ordering = ["name"]

class Course(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=150)
    program = models.CharField(max_length=150)
    specialization = models.CharField(max_length=150)
    image = models.ImageField(upload_to="course_images/", null=True, blank=True)
    mode = models.CharField(max_length=150)
    duration = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    slug = models.SlugField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.program} in {self.specialization}"
    
    class Meta:
        db_table = "courses"
        ordering = ["name"]
