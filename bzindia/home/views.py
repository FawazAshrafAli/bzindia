from django.shortcuts import render
from django.views.generic import TemplateView, View, ListView
import logging

from company.models import Company
from product.models import Product, Category as ProductCategory
from service.models import Service, Category as ServiceCategory
from registration.models import Registration
from educational.models import Course
from blog.models import Blog
from base.models import MetaTag

from base.views import BaseView

logger = logging.getLogger(__name__)

class HomeView(BaseView, TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["home_page"] = True
            context["companies"] = Company.objects.all().order_by("name")
            context["courses"] = Course.objects.all().order_by("?")[:12]
            context["registration_details"] = Registration.objects.all().order_by("sub_type__name")[:12]
            context["services"] = Service.objects.all().order_by("?")[:12]
            context["products"] = Product.objects.all().order_by("?")[:12]
            context["slider_blogs"] = Blog.objects.filter(is_published = True).order_by("?")[:3]
            context["tags"] = MetaTag.objects.all()
        except Exception as e:
            logger.error(f"Error in fetching the context data of home view: {e}")
        return context
