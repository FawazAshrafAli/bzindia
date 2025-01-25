from django.db import models
from django.utils.text import slugify

from company.models import Company
from locations.models import UniquePlace, UniqueDistrict, UniqueState

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

    place = models.ForeignKey(UniquePlace, on_delete=models.CASCADE, null=True, blank=True)
    district = models.ForeignKey(UniqueDistrict, on_delete=models.CASCADE, null=True, blank=True)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, null=True, blank=True)

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


class Feature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    feature = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "features"
        ordering = ["created"]


class VerticalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "vertical_bullets"
        ordering = ["created"]
    

class VerticalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(VerticalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "vertical_tabs"
        ordering = ["created"]


class HorizontalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "horizontal_bullets"
        ordering = ["created"]


class HorizontalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(HorizontalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "horizontal_tabs"
        ordering = ["created"]

class TableData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    data = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "table_data"
        ordering = ["created"]


class Table(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    datas = models.ManyToManyField(TableData)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "table"
        ordering = ["created"]    


class BulletPoints(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    bullet_point = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "bullet_points"
        ordering = ["created"]


class Tag(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    tag = models.CharField(max_length=250)
    link = models.URLField(max_length=200)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "tags"
        ordering = ["created"]


class Timeline(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    summary = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "timelines"
        ordering = ["created"]


class CourseDetail(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    summary = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    features = models.ManyToManyField(Feature)

    # Verical Tab
    vertical_title = models.CharField(max_length=250, null=True, blank=True)
    vertical_tabs = models.ManyToManyField(VerticalTab)

    # Horizontal Tab
    horizontal_title = models.CharField(max_length=250, null=True, blank=True)
    horizontal_tabs = models.ManyToManyField(HorizontalTab)

    # Table
    table_title = models.CharField(max_length=250, null=True, blank=True)
    tables = models.ManyToManyField(Table)

    # Bullet Point
    bullet_title = models.CharField(max_length=250, null=True, blank=True)
    bullet_points = models.ManyToManyField(BulletPoints)

    # Tag
    tag_title = models.CharField(max_length=250, null=True, blank=True)
    tags = models.ManyToManyField(Tag)

    # Timeline
    timeline_title = models.CharField(max_length=250, null=True, blank=True)
    timelines = models.ManyToManyField(Timeline)

    slug = models.SlugField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.course.name}")
            slug = base_slug
            count = 1

            while CourseDetail.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}"
    
    class Meta:
        db_table = "course_details"
        ordering = ["created"]

    @property
    def get_data(self):        
        rows = []
        tables = self.tables.all()

        for table in tables:
            data = [data.data for data in table.datas.all()]
            rows.append(data)

        transposed_data = list(map(list, zip(*rows)))

        return transposed_data



        



class Enquiry(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="course_enquiry_company")

    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, related_name="course_state")
    message = models.TextField()

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.course.name}-{self.email}")
            slug = base_slug

            count = 1
            while Enquiry.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}-{self.email}"
    
    class Meta:
        db_table = "course_enquiries"
        ordering = ["-created"]