from django.contrib.sitemaps import Sitemap

from company.models import Company
from product.models import ProductDetailPage, MultiPage as ProductMultiPage
from service.models import ServiceDetail, MultiPage as ServiceMultiPage
from registration.models import RegistrationDetailPage
from educational.models import CourseDetail, MultiPage as CourseMultiPage
from directory.models import CscCenter
from blog.models import Blog
from base.models import MetaTag
from django.conf import settings
from datetime import datetime, timezone


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "monthly"

    def items(self):
        return [
            '/',
            '/contact_us',
            '/services',
            '/products',
            '/courses',
            '/registrations',
            '/csc_centers',
            '/tag',
            '/blog'
        ]

    def location(self, item):
        return item
    
    def lastmod(self, obj):
        return datetime.now(timezone.utc).replace(microsecond=0)    
    
    def get_urls(self, page=1, site=None, protocol=None):
        urls = super().get_urls(page=page, site=site, protocol=protocol)
        items = self.items()

        for i, item in enumerate(items):
            if item == '/products':
                multipages = ProductMultiPage.objects.prefetch_related('products').all()
                image_list = []

                for multipage in multipages:
                    product_images = multipage.products.values_list("image", flat=True)
                    image_list.extend([img for img in product_images if img])  # Exclude empty/null images

                total = len(image_list)
                urls[i]["image_count"] = total
            elif item == '/services':
                multipages = ServiceMultiPage.objects.all()
                total = len([multipage.service.image.url for multipage in multipages if multipage.service.image])
                urls[i]["image_count"] = total
            elif item == '/courses':
                multipages = CourseMultiPage.objects.all()
                total = len([multipage.course.image.url for multipage in multipages if multipage.course.image])
                urls[i]["image_count"] = total
            elif item == '/csc_centers':
                centers = CscCenter.objects.all()
                total = len([center.logo.url for center in centers if center.logo])
                urls[i]["image_count"] = total
            elif item == '/blog':
                blogs = Blog.objects.all()
                total = len([blog.image.url for blog in blogs if blog.image])
                urls[i]["image_count"] = total
        return urls
    

class CompanySitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return Company.objects.all()

    def location(self, obj):
        return f"/{obj.slug}/"
    
    def lastmod(self, obj):        
        return obj.updated or obj.created or datetime.now(timezone.utc).replace(microsecond=0)


class CompanySubPagesSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Company.objects.all()

    def get_urls(self, page=1, site=None, protocol=None):
        base_url = settings.SITE_URL.rstrip("/")
        urls = []
        subpaths = [
            "faqs", "about_us", "contact_us", "blog",
            "products", "services", "registrations", "courses"
        ]

        now = datetime.now(timezone.utc).replace(microsecond=0)

        for company in self.items():

            for path in subpaths:
                image_count = 0            
                full_url = f"{base_url}/{company.slug}/{path}"

                if path == "products":
                    details = ProductDetailPage.objects.filter(company = company)
                    total = len([detail.product.image.url for detail in details if detail.product.image])
                    image_count = total
                elif path == "services":
                    details = ServiceDetail.objects.filter(company = company)
                    total = len([detail.service.image.url for detail in details if detail.service.image])
                    image_count = total
                elif path == "courses":
                    details = CourseDetail.objects.filter(company = company)
                    total = len([detail.course.image.url for detail in details if detail.course.image])
                    image_count = total
                elif path == "blog":
                    blogs = Blog.objects.filter(company = company)
                    total = len([blog.image.url for blog in blogs if blog.image])
                    image_count = total
                urls.append({
                    'location': full_url,
                    'priority': self.priority,
                    'changefreq': self.changefreq,
                    'lastmod': now,
                    'image_count': image_count
                })
        return urls
    

class BlogSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Blog.objects.select_related("company")

    def location(self, obj):
        if obj.company:
            return f"/{obj.company.slug}/blog/{obj.slug}"
        return f"/blog/{obj.slug}"
    
    def lastmod(self, obj):        
        return obj.updated or obj.created or datetime.now(timezone.utc).replace(microsecond=0)
    
    def get_urls(self, page=1, site=None, protocol=None):
        urls = super().get_urls(page=page, site=site, protocol=protocol)
        items = self.items()

        for i, item in enumerate(items):            
            urls[i]["image_count"] = 1 if item.image else 0
        return urls
    

class MetaTagSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"
    
    def items(self):
        return MetaTag.objects.all()

    def location(self, obj):
        return f"/tag/{obj.slug}"
    
    def lastmod(self, obj):        
        return obj.updated or obj.created or datetime.now(timezone.utc).replace(microsecond=0)
    

class CompanyDetailSitemap(Sitemap):
    def items(self):
        services = ServiceDetail.objects.select_related("company").all()
        products = ProductDetailPage.objects.select_related("company").all()
        courses = CourseDetail.objects.select_related("company").all()
        registrations = RegistrationDetailPage.objects.select_related("company").all()
        return [
            *[(s, "service") for s in services],
            *[(p, "product") for p in products],
            *[(c, "course") for c in courses],
            *[(r, "registration") for r in registrations],
        ]

    def location(self, obj):
        instance, type_slug = obj
        return f"/{type_slug}/{instance.company.slug}/{instance.slug}"
    
    def lastmod(self, obj):
        instance, type_slug = obj
        return instance.updated or instance.created or datetime.now(timezone.utc).replace(microsecond=0)
    
    def image_count(self, obj):
        instance, _ = obj

        return instance.image_count or 0
    
    def get_urls(self, page=1, site=None, protocol=None):
        urls = super().get_urls(page=page, site=site, protocol=protocol)
        items = self.items()

        for i, item in enumerate(items):
            urls[i]["image_count"] = self.image_count(item)
        return urls


class IndiaSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return ["state-list"]

    def location(self, item):
        return "/state-list-in-india/"

    def lastmod(self, item):        
        return datetime.now(timezone.utc).replace(microsecond=0)
    
    def get_urls(self, page=1, site=None, protocol=None):
        urls = super().get_urls(page=page, site=site, protocol=protocol)
        items = self.items()

        for i, item in enumerate(items):
            urls[i]["image_count"] = 6
        return urls