"""
URL configuration for bzindia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django_admin/', admin.site.urls),

    path('', include('home.urls', namespace="home")),
    path('company/', include('company.urls', namespace="company")),

    path('admin/', include('superadmin.urls', namespace="superadmin")),
    path('authentication/', include('authentication.urls', namespace="authentication")),
    path('locations/', include('locations.urls', namespace="locations")),
    path('customer/', include('customer.urls', namespace="customer")),
    path('product/', include('product.urls', namespace="product")),
    path('directory/', include('directory.urls', namespace="directory")),
    path('service/', include('service.urls', namespace="service")),
    path('education/', include('educational.urls', namespace="education")),
    path('registration/', include('registration.urls', namespace="registration")),
    path('blog/', include('blog.urls', namespace="blog")),
    path('base/', include('base.urls', namespace="base")),

    # api-urls
    path('company_api/', include('company_api.urls', namespace="company_api")),
    path('registration_api/', include('registration_api.urls', namespace="registration_api")),
    path('course_api/', include('course_api.urls', namespace="course_api")),
    path('service_api/', include('service_api.urls', namespace="service_api")),
    path('product_api/', include('product_api.urls', namespace="product_api")),
    path('meta_tag_api/', include('meta_tag_api.urls', namespace="meta_tag_api")),
    path('destination_api/', include('destination_api.urls', namespace="destination_api")),
    path('blog_api/', include('blog_api.urls', namespace="blog_api")),
    path('location_api/', include('location_api.urls', namespace="location_api")),
    path('home_api/', include('home_api.urls', namespace="home_api")),
    path('contact_api/', include('contact_api.urls', namespace="contact_api")),
    path('custom_pages_api/', include('custom_pages_api.urls', namespace="custom_pages_api")),
    path('meta_api/', include('meta_api.urls', namespace="meta_api")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])