from django.db import models
from django.utils.text import slugify

class Category(models.Model):
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


class SubCategory(models.Model):
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
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)    
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    # Additional fields
    colors = models.ManyToManyField(Color)
    sizes = models.ManyToManyField(Size)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    length = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=50, null=True, blank=True)

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