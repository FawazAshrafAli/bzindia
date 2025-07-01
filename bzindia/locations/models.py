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

    def __str__(self):
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

    def __str__(self):
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

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "places"
        ordering = ["name"]


class TestedCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.latitude}-{self.longitude}"
    

class RetestedCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.latitude}-{self.longitude}"
    

class AndmanAndNicobarTestedCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.latitude}-{self.longitude}"
    

class TestPincode(models.Model):
    pincode = models.PositiveIntegerField()

    def __str__(self):
        return self.pincode


class UniqueState(models.Model):
    name = models.CharField(max_length=150)    
    slug = models.SlugField(blank=True, null=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while UniqueState.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "unique_states"
        ordering = ["name"]


class UniqueDistrict(models.Model):
    name = models.CharField(max_length=150)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, related_name = "districts")
    slug = models.SlugField(blank=True, null=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 2
            while UniqueDistrict.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "unique_districts"
        ordering = ["name"]


class PlaceCoordinate(models.Model):
    place = models.ForeignKey("UniquePlace", on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()


class PlacePincode(models.Model):
    place = models.ForeignKey("UniquePlace", on_delete=models.CASCADE)
    pincode = models.PositiveIntegerField(blank=True, null=True)


class UniquePlace(models.Model):
    name = models.CharField(max_length=150)
    alt_name = models.CharField(max_length=150, blank=True, null=True)

    district = models.ForeignKey(UniqueDistrict, on_delete=models.CASCADE, related_name="places")
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE)

    pincodes = models.ManyToManyField(PlacePincode)

    coordinates = models.ManyToManyField(PlaceCoordinate)    
    
    slug = models.SlugField(blank=True, null=True, max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 2
            while UniquePlace.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "unique_places"
        ordering = ["name"]


class UaeCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"UAE ({self.latitude}-{self.longitude})"
    

class KsaCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"KSA ({self.latitude}-{self.longitude})"
    

class UaeLocationData(models.Model):
    json_data = models.JSONField()

    address = models.CharField(max_length=500)

    requested_latitude = models.FloatField()
    requested_longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "uae_location_data"
        ordering = ["created"]


class KsaLocationData(models.Model):
    json_data = models.JSONField()

    address = models.CharField(max_length=500)

    requested_latitude = models.FloatField()
    requested_longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ksa_location_data"
        ordering = ["created"]


class PincodeAndCoordinate(models.Model):
    place = models.ForeignKey(UniquePlace, on_delete=models.CASCADE, related_name="pincode_and_coordinates")
    post_office_id = models.CharField(max_length=500)

    pincode = models.PositiveIntegerField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    slug = models.SlugField(max_length=500, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pincode} - {self.place.name} of {self.place.district.name}, {self.place.state.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.pincode}-{self.place.name}-{self.place.district.name}-{self.place.state.name}")

            slug = base_slug
            count = 1

            while PincodeAndCoordinate.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)


class IndiaLocationData(models.Model):
    json_data = models.JSONField()

    address = models.CharField(max_length=500)

    place = models.OneToOneField(UniquePlace, on_delete=models.CASCADE)

    # requested_latitude = models.FloatField()
    # requested_longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "india_location_data"
        ordering = ["created"]