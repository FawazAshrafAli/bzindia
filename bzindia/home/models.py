from django.db import models
from ckeditor.fields import RichTextField

class HomeContent(models.Model):
    title = models.CharField(max_length=250, default="BZ India")
    description = RichTextField(default="BZ India is a joint venture group that partners with leading companies across diverse sectors to deliver top-tier services in the Indian market")    

    meta_title = models.CharField(max_length=250)
    meta_description = models.TextField()

    footer_text = RichTextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title[:25]}..." if len(self.title) > 25 else self.title
    
    class Meta:
        db_table = "home_main_content"

