import os
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime, timezone
from service.models import MultiPage as ServiceMultiPage
from product.models import MultiPage as ProductMultiPage
from registration.models import MultiPage as RegistrationMultiPage
from educational.models import MultiPage as CourseMultiPage
from locations.models import UniquePlace, UniqueState, UniqueDistrict

SITEMAP_DIR = os.path.join(settings.BASE_DIR, "static", "sitemaps")
BASE_URL = settings.SITE_URL.rstrip("/")

CHUNK_SIZE = 25000

def write_sitemap_file(filename, urls):
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    path = os.path.join(SITEMAP_DIR, filename)

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<?xml-stylesheet type="text/xsl" href="/static/sitemaps/sitemap1.xsl"?>')
    lines.append('''<urlset
    xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:bz="https://bzindia.in/schemas"
    xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 
    http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">''')

    for url in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{url['loc']}</loc>")
        lines.append(f"    <lastmod>{now}</lastmod>")
        lines.append(f"    <changefreq>weekly</changefreq>")
        lines.append(f"    <priority>0.8</priority>")
        lines.append(f"    <bz:imageCount>{url['image_count']}</bz:imageCount>")
        lines.append("  </url>")

    lines.append("</urlset>")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


class Command(BaseCommand):
    help = "Generate sitemap index and chunked sitemap XML files"

    def handle(self, *args, **kwargs):
        os.makedirs(SITEMAP_DIR, exist_ok=True)

        services = ServiceMultiPage.objects.select_related("company")
        products = ProductMultiPage.objects.select_related("company")
        courses = CourseMultiPage.objects.select_related("company")
        registrations = RegistrationMultiPage.objects.select_related("company")

        place_slugs = list(UniquePlace.objects.values_list("slug", flat=True))
        district_slugs = list(UniqueDistrict.objects.values_list("slug", flat=True))
        state_slugs = list(UniqueState.objects.values_list("slug", flat=True))

        location_slugs = list(set(place_slugs + district_slugs + state_slugs))

        place_data = list(
            UniquePlace.objects.values("slug", "district__slug", "state__slug")
        )

        all_pages = [
            *[(s, "service") for s in services],
            *[(p, "product") for p in products],
            *[(c, "course") for c in courses],
            *[(r, "registration") for r in registrations],
        ]

        all_urls = []

        for instance, _type in all_pages:
            base_slug = getattr(instance, "slug", "") or getattr(instance, "item_slug", "")
            company_slug = instance.company.slug



            image_count = 0

            if instance.image_count:
                image_count += instance.image_count       

            if instance.url_type == "slug_filtered":
                for location_slug in location_slugs:                    
                    url = f"{BASE_URL}/{company_slug}/{base_slug.replace('place_name', location_slug)}/"                    
                    all_urls.append({"loc": url, "image_count": image_count})

            elif instance.url_type == "location_filtered":
                for place in place_data:
                    state_slug = place["state__slug"]
                    for region_slug in (place["district__slug"], place["slug"]):
                        full_url = f"{settings.SITE_URL}/{company_slug}/{base_slug}/{state_slug}/{region_slug}/"
                        all_urls.append({"loc": full_url, "image_count": image_count})

        # Split into chunks
        sitemap_files = []
        for i in range(0, len(all_urls), CHUNK_SIZE):
            chunk = all_urls[i:i + CHUNK_SIZE]
            filename = f"sitemap-multipage-{i//CHUNK_SIZE + 1}.xml"
            write_sitemap_file(filename, chunk)
            sitemap_files.append(filename)

        # Write sitemap index
        now = datetime.utcnow().isoformat() + "Z"
        index_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<?xml-stylesheet type="text/xsl" href="/static/sitemaps/sitemap.xsl"?>',
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        ]

        for fname in sitemap_files:
            index_lines.append("  <sitemap>")
            index_lines.append(f"    <loc>{BASE_URL}/{fname}</loc>")
            index_lines.append(f"    <lastmod>{now}</lastmod>")
            index_lines.append("  </sitemap>")
            
        index_lines.append("  <sitemap>")
        index_lines.append(f"    <loc>{BASE_URL}/sitemap-django.xml</loc>")
        index_lines.append(f"    <lastmod>{now}</lastmod>")
        index_lines.append("  </sitemap>")

        index_lines.append("</sitemapindex>")

        with open(os.path.join(SITEMAP_DIR, "sitemap_index.xml"), "w", encoding="utf-8") as f:
            f.write("\n".join(index_lines))

        self.stdout.write(self.style.SUCCESS(
            f"✅ Generated {len(sitemap_files)} sitemaps and index at: /static/sitemaps/sitemap_index.xml"
        ))