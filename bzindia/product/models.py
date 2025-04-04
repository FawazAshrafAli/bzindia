from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from datetime import datetime
from django.db.models import Avg

from company.models import Company
from locations.models import UniqueState
from base.models import MetaTag

class Category(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Category.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def str(self):
        return self.name

    class Meta:
        db_table = "product_category"
        ordering = ["name"]

    @property
    def sub_categories(self):
        return SubCategory.objects.filter(category = self).values("name", "slug")


class SubCategory(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.category.name}")
            slug = base_slug
            count = 1
            while Category.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def str(self):
        return self.name

    class Meta:
        db_table = "product_sub_category"
        ordering = ["name"]


class Brand(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Brand.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def str(self):
        return self.name

    class Meta:
        db_table = "product_brand"
        ordering = ["name"]


class Size(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    standard = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.category.name}")
            slug = base_slug
            count = 1
            while Brand.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def str(self):
        return self.name

    class Meta:
        db_table = "product_sizes"
        ordering = ["name"]


class Color(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, unique=True)
    hexa = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.hexa}")
            slug = base_slug
            count = 1
            while Brand.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def str(self):
        return self.name

    class Meta:
        db_table = "product_colors"
        ordering = ["name"]
        

class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)    
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    # Additional fields
    colors = models.ManyToManyField(Color)
    sizes = models.ManyToManyField(Size)
    weight = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    length = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=50, null=True, blank=True)

    slug = models.SlugField(blank=True, null=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.category.name}")
            slug = base_slug
            count = 1
            while Brand.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    @property
    def get_colors(self):
        colors = self.colors.all()
        if colors and len(colors) > 0:
            color_list = []
            for color in colors:
                color_list.append(f"<div style='height: 15px; width: 15px; border: 1px solid black; background-color: {color.hexa};'></div>&nbsp;{color.name}")
            return ',&nbsp;'.join(color_list)
        return None
    
    @property
    def get_sizes(self):
        sizes = self.sizes.all()
        if sizes and len(sizes) > 0:
            sizes_list = []
            for size in sizes:
                if size.standard:
                    sizes_list.append(f"{size.name} ({size.standard})")
                else:
                    sizes_list.append(size.name)
            return ',&nbsp;'.join(sizes_list)
        return None
    
    @property
    def get_dimension(self):
        if self.length and self.width and self.height:
            return f"{self.length} {self.unit} x {self.width} {self.unit} x {self.height} {self.unit}"
        
        elif self.length and self.width:
            return f"{self.length} {self.unit} x {self.width} {self.unit}"
        
        return None
    
    @property
    def get_weight(self):
        try:
            if int(self.weight) == 0:
                return None
        except (ValueError, TypeError):
            return self.weight
        
    def str(self):
        return self.name

    class Meta:
        db_table = "products"
        ordering = ["name"]

    @property
    def reviews(self):
        return Review.objects.filter(product__slug = self.slug)

    @property
    def rating(self):
        reviews = Review.objects.filter(product = self).values_list("rating", flat=True)        
        
        return reviews.aggregate(Avg('rating'))['rating__avg'] if reviews else 0

    @property
    def rating_count(self):
        return Review.objects.filter(product = self).count()  


class Faq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_faq_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    question = models.TextField()
    answer = models.TextField()
    dynamic_place_rendering = models.BooleanField(default=False)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.product.name}")
            slug = base_slug

            count = 1
            while Faq.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_faqs"
        ordering = ["-created"]


class Review(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="review_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    review_by = models.TextField(null=True, blank=True)

    text = models.TextField()
    rating = models.PositiveIntegerField(default=5)

    order = models.PositiveIntegerField(default=0)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            user = self.user.username if not self.review_by else self.review_by            

            base_slug = slugify(f"{self.company.name}-{self.product}-{user}")

            slug = base_slug
            count = 1

            while Review.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        user = self.user.username if not self.review_by else self.review_by
        return f"{self.company.name}-{self.product}-{user}"

    class Meta:
        db_table = "reviews"
        ordering = ["created"]    


class Enquiry(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_enquiry_company")

    name = models.CharField(max_length=250)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, related_name="product_enquiry_state")
    message = models.TextField()

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.product.name}-{self.email}")
            slug = base_slug

            count = 1
            while Enquiry.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}-{self.email}"
    
    class Meta:
        db_table = "product_enquiries"
        ordering = ["-created"]


class Feature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_feature_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    feature = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_features"
        ordering = ["created"]


class VerticalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_vertical_bullet_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_vertical_bullets"
        ordering = ["created"]


class VerticalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_vertical_tab_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(VerticalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_vertical_tabs"
        ordering = ["created"]


class HorizontalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_horizontal_bullet_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_horizontal_bullets"
        ordering = ["created"]


class HorizontalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_horizontal_tab_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(HorizontalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_horizontal_tabs"
        ordering = ["created"]


class TableData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_table_data_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    data = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_table_data"
        ordering = ["created"]


class Table(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_table_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    datas = models.ManyToManyField(TableData)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_table"
        ordering = ["created"]    


class BulletPoint(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_bullet_points_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    bullet_point = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_bullet_points"
        ordering = ["created"]


class Tag(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_tag_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    tag = models.CharField(max_length=250)
    link = models.URLField(max_length=200)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_tags"
        ordering = ["created"]

    
class Timeline(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_timeline_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    summary = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_timelines"
        ordering = ["created"]


class ProductDetailPage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    summary = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    meta_title = models.CharField(max_length=100)
    meta_tags = models.ManyToManyField(MetaTag)
    meta_description = models.TextField()

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
    bullet_points = models.ManyToManyField(BulletPoint)

    # Tag
    tag_title = models.CharField(max_length=250, null=True, blank=True)
    tags = models.ManyToManyField(Tag)

    # Timeline
    timeline_title = models.CharField(max_length=250, null=True, blank=True)
    timelines = models.ManyToManyField(Timeline)

    hide_features = models.BooleanField(default=False)
    hide_vertical_tab = models.BooleanField(default=False)
    hide_horizontal_tab = models.BooleanField(default=False)
    hide_table = models.BooleanField(default=False)
    hide_bullets = models.BooleanField(default=False)
    hide_tags = models.BooleanField(default=False)
    hide_timeline = models.BooleanField(default=False)

    buy_now_action = models.CharField(max_length=50, default="whatsapp")
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    external_link = models.URLField(max_length=500, blank=True, null=True)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = f"{self.product.name} - {self.company.name}"

        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.product.name}")
            slug = base_slug
            count = 1

            while ProductDetailPage.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_details"
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
    
    @property
    def get_meta_tags(self):
        if not self.meta_tags:
            return ""

        tag_list = [tag.name for tag in self.meta_tags.all()]

        return ", ".join(tag_list)



class MultiPageFeature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_feature")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    feature = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipage_features"
        ordering = ["created"]


class MultiPageVerticalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_vertical_bullet")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipage_vertical_bullets"
        ordering = ["created"]
    

class MultiPageVerticalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_vertical_tab")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    heading = models.CharField(max_length=250, null=True, blank=True)
    sub_heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(MultiPageVerticalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipage_vertical_tabs"
        ordering = ["created"]


class MultiPageHorizontalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_horizontal_bullet")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)

    bullet = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipage_horizontal_bullets"
        ordering = ["created"]


class MultiPageHorizontalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_horizontal_tab")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(MultiPageHorizontalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipage_horizontal_tabs"
        ordering = ["created"]

class MultiPageTableData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_table_data")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    data = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipage_table_data"
        ordering = ["created"]


class MultiPageTable(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_table")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    datas = models.ManyToManyField(MultiPageTableData)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipage_table"
        ordering = ["created"]    


class MultiPageBulletPoint(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_bullets")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    bullet_point = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipage_bullet_points"
        ordering = ["created"]


class MultiPageTag(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_tag")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    tag = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipage_tags"
        ordering = ["created"]


class MultiPageTimeline(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_timeline")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    heading = models.CharField(max_length=250)
    summary = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipage_timelines"
        ordering = ["created"]


class MultiPageFaq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_faq")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    question = models.CharField(max_length=250)
    answer = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipage_faqs"
        ordering = ["created"]


class MultiPage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    summary = models.TextField(null=True, blank=True)
    description = RichTextField()

    meta_title = models.CharField(max_length=100)
    meta_tags = models.ManyToManyField(MetaTag, related_name="meta_tag_of_multipage")
    meta_description = models.TextField()

    url_type = models.CharField(max_length=50, default="slug_filtered")

    features = models.ManyToManyField(MultiPageFeature)

    # Verical Tab
    vertical_title = models.CharField(max_length=250, null=True, blank=True)
    vertical_tabs = models.ManyToManyField(MultiPageVerticalTab)

    # Horizontal Tab
    horizontal_title = models.CharField(max_length=250, null=True, blank=True)
    horizontal_tabs = models.ManyToManyField(MultiPageHorizontalTab)

    # Table
    table_title = models.CharField(max_length=250, null=True, blank=True)
    tables = models.ManyToManyField(MultiPageTable)

    # Bullet Point
    bullet_title = models.CharField(max_length=250, null=True, blank=True)
    bullet_points = models.ManyToManyField(MultiPageBulletPoint)

    # Tag
    tag_title = models.CharField(max_length=250, null=True, blank=True)
    tags = models.ManyToManyField(MultiPageTag)

    # Timeline
    timeline_title = models.CharField(max_length=250, null=True, blank=True)
    timelines = models.ManyToManyField(MultiPageTimeline)

    # Faqs
    faqs = models.ManyToManyField(MultiPageFaq)

    hide_features = models.BooleanField(default=False)
    hide_vertical_tab = models.BooleanField(default=False)
    hide_horizontal_tab = models.BooleanField(default=False)
    hide_table = models.BooleanField(default=False)
    hide_bullets = models.BooleanField(default=False)
    hide_tags = models.BooleanField(default=False)
    hide_timeline = models.BooleanField(default=False)
    hide_faqs = models.BooleanField(default=False)

    buy_now_action = models.CharField(max_length=50, default="whatsapp")
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    external_link = models.URLField(max_length=500, blank=True, null=True)

    slug = models.SlugField(null=True, blank=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = f"{self.product.name} - {self.company.name}"

        if not self.slug:
            base_slug = slugify(f"{self.company.name}-{self.product.name}")
            slug = base_slug
            count = 1

            while MultiPage.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipages"
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
    
    @property
    def get_meta_tags(self):
        if not self.meta_tags:
            return ""

        tag_list = [tag.name for tag in self.meta_tags.all()]

        return ", ".join(tag_list)
