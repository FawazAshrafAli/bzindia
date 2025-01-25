from django.db import models
from django.utils.text import slugify
import uuid

class PostOffice(models.Model):
    circle_name = models.CharField(max_length=150, null=True, blank=True)
    region_name = models.CharField(max_length=150, null=True, blank=True)
    division_name = models.CharField(max_length=150, null=True, blank=True)
    office_name = models.CharField(max_length=150, null=True, blank=True)
    pincode = models.PositiveIntegerField(null=True, blank=True)
    office_type = models.CharField(max_length=150, null=True, blank=True)
    delivery = models.BooleanField(default=False, null=True, blank=True)
    district = models.CharField(max_length=150, null=True, blank=True)
    state_name = models.CharField(max_length=150, null=True, blank=True)
    latitude = models.CharField(max_length=150, null=True, blank=True)
    longitude = models.CharField(max_length=150, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pincode
    
    class Meta:
        db_table = "post_offices"
        ordering = ["pincode"]


class PoliceStation(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

    name_gujarati = models.CharField(max_length=250, null=True, blank=True)
    name_goan_konkani = models.CharField(max_length=250, null=True, blank=True)
    name_santali = models.CharField(max_length=250, null=True, blank=True)
    name_hindi = models.CharField(max_length=250, null=True, blank=True)
    name_malayalam = models.CharField(max_length=250, null=True, blank=True)
    name_punjabi = models.CharField(max_length=250, null=True, blank=True) #name:pnb
    name_telugu = models.CharField(max_length=250, null=True, blank=True)
    name_kannada = models.CharField(max_length=250, null=True, blank=True)
    name_bengali = models.CharField(max_length=250, null=True, blank=True)
    name_marathi = models.CharField(max_length=250, null=True, blank=True)
    name_tamil = models.CharField(max_length=250, null=True, blank=True)
    name_odiya = models.CharField(max_length=250, null=True, blank=True)
    name_assamese = models.CharField(max_length=250, null=True, blank=True)
    name_kashmiri = models.CharField(max_length=250, null=True, blank=True)
    name_urdu = models.CharField(max_length=250, null=True, blank=True)
    name_maithili = models.CharField(max_length=250, null=True, blank=True)
    name_sanskrit = models.CharField(max_length=250, null=True, blank=True)

    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=20, null=True, blank=True)    
    phone = models.CharField(max_length=120, null=True, blank=True)
    website = models.URLField(max_length=255, null=True, blank=True)
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name or f"Police Station {self.osm_id}"

    class Meta:
        verbose_name = "Police Station"
        verbose_name_plural = "Police Stations"
        db_table = "police_stations"


class Bank(models.Model):
    name = models.CharField(max_length=150)
    ifsc = models.CharField(max_length=20)
    branch = models.CharField(max_length=150)
    center = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    district = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    address = models.TextField()
    contact = models.CharField(max_length=50)
    
    iso3166 = models.CharField(max_length=50)
    micr = models.CharField(max_length=50)
    swift = models.CharField(max_length=50, blank=True, null=True)

    imps = models.BooleanField(default=False)
    rtgs = models.BooleanField(default=False)
    neft = models.BooleanField(default=False)
    upi = models.BooleanField(default=False)

    slug = models.SlugField(blank=True, null=True, max_length=500)

    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.slug:   
            base_slug = slugify(f"{self.name}-{self.ifsc}")
            slug = base_slug
            count = 1
            while Bank.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            
            self.slug = slug

        super().save(*args, **kwargs)


    class Meta:
        verbose_name = "Bank"
        verbose_name_plural = "Banks"
        
        db_table = "banks"
        ordering = ["ifsc"]

    def __str__(self):
        return f"{self.name}-{self.branch}"


class TouristAttraction(models.Model):
    image = models.ImageField(upload_to="attractions/", null=True, blank=True)

    name = models.CharField(max_length=250, null=True, blank=True)
    old_name = models.CharField(max_length=250, null=True, blank=True)
    alternative_name = models.CharField(max_length=250, null=True, blank=True) #alt_name:en        
    short_name = models.CharField(max_length=150, null=True, blank=True)

    # Name in different language
    alternative_name_hindi = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_bengali = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_marathi = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_kannada = models.CharField(max_length=250, null=True, blank=True) #alt_name:kn
    alternative_name_maithili = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_malayalam = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_tamil = models.CharField(max_length=250, null=True, blank=True)

    name_gujarati = models.CharField(max_length=250, null=True, blank=True)
    name_goan_konkani = models.CharField(max_length=250, null=True, blank=True)
    name_santali = models.CharField(max_length=250, null=True, blank=True)
    name_hindi = models.CharField(max_length=250, null=True, blank=True)
    name_malayalam = models.CharField(max_length=250, null=True, blank=True)
    name_punjabi = models.CharField(max_length=250, null=True, blank=True) #name:pnb
    name_telugu = models.CharField(max_length=250, null=True, blank=True)
    name_kannada = models.CharField(max_length=250, null=True, blank=True)
    name_bengali = models.CharField(max_length=250, null=True, blank=True)
    name_marathi = models.CharField(max_length=250, null=True, blank=True)
    name_tamil = models.CharField(max_length=250, null=True, blank=True)
    name_odiya = models.CharField(max_length=250, null=True, blank=True)
    name_assamese = models.CharField(max_length=250, null=True, blank=True)
    name_kashmiri = models.CharField(max_length=250, null=True, blank=True)
    name_urdu = models.CharField(max_length=250, null=True, blank=True)
    name_maithili = models.CharField(max_length=250, null=True, blank=True)
    name_sanskrit = models.CharField(max_length=250, null=True, blank=True)

    historic_type = models.CharField(max_length=150, null=True, blank=True)

    # accessibility
    wheelchair_accessible = models.CharField(max_length=50, null=True, blank=True)

    # sports availability
    sport_type = models.CharField(max_length=50, null=True, blank=True)

    # Leisure Activity
    leisure_activity = models.CharField(max_length=50, null=True, blank=True)

    # Religious
    denomination = models.CharField(max_length=50, null=True, blank=True)
    religion = models.CharField(max_length=50, null=True, blank=True)

    # Geography
    house_number = models.CharField(max_length=150, null=True, blank=True) #addr:housenumber # addr:housename
    pincode = models.CharField(max_length=250, null=True, blank=True) #postcode #addr:postcode
    street = models.CharField(max_length=350, null=True, blank=True) #addr:street
    place = models.CharField(max_length=150, null=True, blank=True) #addr:place
    city = models.CharField(max_length=150, null=True, blank=True) #addr:city 
    district = models.CharField(max_length=150, null=True, blank=True) #addr:district 
    state = models.CharField(max_length=150, null=True, blank=True) #addr:state 
    place_type = models.CharField(max_length=250, null=True, blank=True) #place
    building_type = models.CharField(max_length=150, null=True, blank=True) #amenity
    building_category = models.CharField(max_length=150, null=True, blank=True) #building
    elevation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) #ele
    geography_type = models.CharField(max_length=150, null=True, blank=True) #natural
    man_made_contribution = models.CharField(max_length=150, null=True, blank=True) #man_made
    memmorial_type = models.CharField(max_length=50, null=True, blank=True) #memorial

    building_height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) #height

    waterway_type = models.CharField(max_length=150, null=True, blank=True) #waterway
    waterbody_type = models.CharField(max_length=150, null=True, blank=True) #water
    castle_type = models.CharField(max_length=150, null=True, blank=True) #castle
    attraction = models.CharField(max_length=150, null=True, blank=True)

    # operation data
    operated_by = models.CharField(max_length=250, null=True, blank=True)
    opening_hours = models.CharField(max_length=150, null=True, blank=True)
    access_type = models.CharField(max_length=150, null=True, blank=True) #access

    started_date = models.CharField(max_length=150, null=True, blank=True) #start_date

    # shopping
    shops_available = models.CharField(max_length=150, null=True, blank=True) #shop

    # description
    description = models.TextField(null=True, blank=True)
    note = models.CharField(max_length=150, null=True, blank=True)

    # contact
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)

    #website
    website = models.URLField(max_length=200, null=True, blank=True)    

    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    slug = models.SlugField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    
    class Meta:
        db_table = "attractions"
        ordering = ["created"]

# languages_in_india = [
#     "hi",      # Hindi
#     "en",      # English
#     "bn",      # Bengali
#     "te",      # Telugu
#     "mr",      # Marathi
#     "ta",      # Tamil
#     "ur",      # Urdu
#     "gu",      # Gujarati
#     "ml",      # Malayalam
#     "kn",      # Kannada
#     "or",      # Odia (Oriya)
#     "pa",      # Punjabi
#     "as",      # Assamese
#     "mai",     # Maithili
#     "sa",      # Sanskrit
#     "kok",     # Konkani
#     "sd",      # Sindhi
#     "dgo",     # Dogri
#     "mni",     # Manipuri
#     "brx",     # Bodo
#     "sat",     # Santali
#     "ks",      # Kashmiri
#     "ne",      # Nepali
#     "lus",     # Mizo
#     "ar",      # Arabic (spoken by some communities)
# ]


class Court(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)

    old_name = models.CharField(max_length=250, blank=True, null=True)

    name_gujarati = models.CharField(max_length=250, null=True, blank=True)
    name_goan_konkani = models.CharField(max_length=250, null=True, blank=True)
    name_santali = models.CharField(max_length=250, null=True, blank=True)
    name_hindi = models.CharField(max_length=250, null=True, blank=True)
    name_malayalam = models.CharField(max_length=250, null=True, blank=True)
    name_punjabi = models.CharField(max_length=250, null=True, blank=True) #name:pnb
    name_telugu = models.CharField(max_length=250, null=True, blank=True)
    name_kannada = models.CharField(max_length=250, null=True, blank=True)
    name_bengali = models.CharField(max_length=250, null=True, blank=True)
    name_marathi = models.CharField(max_length=250, null=True, blank=True)
    name_tamil = models.CharField(max_length=250, null=True, blank=True)
    name_odiya = models.CharField(max_length=250, null=True, blank=True)
    name_assamese = models.CharField(max_length=250, null=True, blank=True)
    name_kashmiri = models.CharField(max_length=250, null=True, blank=True)
    name_urdu = models.CharField(max_length=250, null=True, blank=True)
    name_maithili = models.CharField(max_length=250, null=True, blank=True)
    name_sanskrit = models.CharField(max_length=250, null=True, blank=True)

    designation = models.CharField(max_length=250, null=True, blank=True)

    street = models.CharField(max_length=250, blank=True, null=True)
    city = models.CharField(max_length=250, blank=True, null=True)
    district = models.CharField(max_length=250, blank=True, null=True)
    state = models.CharField(max_length=250, blank=True, null=True)
    pincode = models.PositiveIntegerField(null=True, blank=True)
    
    phone = models.CharField(max_length=50, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)

    opening_hours = models.CharField(max_length=250, blank=True, null=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    class Meta:
        db_table="courts"