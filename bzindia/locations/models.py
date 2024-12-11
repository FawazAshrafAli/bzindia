from django.db import models
from django.utils.text import slugify

class State(models.Model):
    name = models.CharField(max_length=150)    
    slug = models.SlugField(blank=True, null=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while State.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def str(self):
        return self.name
    
    class Meta:
        db_table = "states"
        ordering = ["name"]


class District(models.Model):
    name = models.CharField(max_length=150)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True, null=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.state.name}")
            slug = base_slug
            count = 1
            while District.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def str(self):
        return self.name
    
    class Meta:
        db_table = "districts"
        ordering = ["name"]


class Place(models.Model):
    name = models.CharField(max_length=150)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    pincode = models.PositiveIntegerField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.district.name}-{self.state.name}")
            slug = base_slug
            count = 1
            while Place.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def str(self):
        return self.name
    
    class Meta:
        db_table = "places"
        ordering = ["name"]


class TestedCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    def str(self):
        return f"{self.latitude}-{self.longitude}"
    

class RetestedCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    def str(self):
        return f"{self.latitude}-{self.longitude}"
    

class TestPincode(models.Model):
    pincode = models.PositiveIntegerField()

    def __str__(self):
        return self.pincode