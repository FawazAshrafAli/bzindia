from django.db import models
from company.models import Company
from django.utils.timezone import now

from django.utils.text import slugify

from locations.models import UniquePlace, UniqueDistrict, UniqueState

class AboutUs(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    content = models.TextField(verbose_name="Content")

    # intro = models.TextField()
    # mission = models.TextField(blank=True, null=True)
    # vision = models.TextField(blank=True, null=True)
    # history = models.TextField(blank=True, null=True)
    # team_info = models.TextField(blank=True, null=True)

    slug = models.SlugField(max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.company.name)
            slug = base_slug

            count = 1
            while AboutUs.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "about_us"
        ordering = ["company__name"]


class ContactUs(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=20)

    provide_query = models.BooleanField(default=False)

    place = models.ForeignKey(UniquePlace, on_delete=models.CASCADE, null=True, blank=True)
    district = models.ForeignKey(UniqueDistrict, on_delete=models.CASCADE, null=True, blank=True)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, null=True, blank=True)
    pincode = models.PositiveIntegerField(blank=True, null=True)

    facebook = models.URLField(max_length=250, blank=True, null=True)
    x = models.URLField(max_length=250, blank=True, null=True)
    youtube = models.URLField(max_length=250, blank=True, null=True)
    instagram = models.URLField(max_length=250, blank=True, null=True)

    lat = models.DecimalField(max_digits=10, decimal_places=7)
    lon = models.DecimalField(max_digits=10, decimal_places=7)

    slug = models.SlugField(max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.company.name)
            slug = base_slug

            count = 1
            while ContactUs.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "contact_us"
        ordering = ["company__name"]


class FAQ(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    question = models.CharField(max_length=250)
    answer = models.TextField()

    slug = models.SlugField(max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.company.name)
            slug = base_slug

            count = 1
            while FAQ.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "faq"
        ordering = ["company__name"]


class PrivacyPolicy(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    content = models.TextField(verbose_name="Content")

    # information_collection = models.TextField(verbose_name="Information Collection", blank=True, null=True)
    # use_of_information = models.TextField(verbose_name="Use of Information", blank=True, null=True)
    # information_sharing = models.TextField(verbose_name="Information Sharing", blank=True, null=True)
    # user_rights = models.TextField(verbose_name="User Rights", blank=True, null=True)
    # cookies_tracking = models.TextField(verbose_name="Cookies and Tracking", blank=True, null=True)
    effective_date = models.DateField(verbose_name="Effective Date")
    last_updated = models.DateField(verbose_name="Last Updated", null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    support_email = models.EmailField(max_length=254, null=True, blank=True)

    slug = models.SlugField(max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.company.name)
            slug = base_slug

            count = 1
            while FAQ.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "privacy_policies"
        ordering = ["company__name"]


class TermsAndConditions(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    content = models.TextField(help_text="Full text of the Terms and Conditions.")
    
    version = models.CharField(max_length=20, help_text="Version number of the Terms and Conditions.")
    effective_date = models.DateField(default=now, help_text="The date when these terms became effective.")
    is_active = models.BooleanField(default=False, help_text="Indicates if this version is currently active.")
    
    slug = models.SlugField(blank=True, null=True, help_text="The slug of the record")

    created_at = models.DateTimeField(auto_now_add=True, help_text="The date and time when the record was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="The date and time when the record was last updated.")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.company.name)
            slug = base_slug

            count = 1
            while TermsAndConditions.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)


    class Meta:
        verbose_name = "Terms and Conditions"
        verbose_name_plural = "Terms and Conditions"
        ordering = ['-effective_date']

    def __str__(self):
        return self.company.name    
    

class ShippingAndDeliveryPolicy(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    content = models.TextField(verbose_name="Content")    

    slug = models.SlugField(max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.company.name)
            slug = base_slug

            count = 1
            while ShippingAndDeliveryPolicy.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "shipping_and_delivery_policy"
        ordering = ["company__name"]


class CancellationAndRefundPolicy(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    content = models.TextField(verbose_name="Content")    

    slug = models.SlugField(max_length=500)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.company.name)
            slug = base_slug

            count = 1
            while CancellationAndRefundPolicy.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "cancellation_and_refund_policy"
        ordering = ["company__name"]