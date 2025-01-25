from django.shortcuts import render
from django.views.generic import TemplateView, View, ListView
import logging

from company.models import Company
from product.models import Product, Category as ProductCategory
from service.models import Service, Category as ServiceCategory
from registration.models import RegistrationType
from educational.models import Program

logger = logging.getLogger(__name__)

class BaseHomeView(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            pass
        except Exception as e:
            logger.error(f"Error in fetching context data of base home view: {e}")
        return context
    

class HomeView(BaseHomeView, TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["companies"] = Company.objects.all().order_by("name")
            context["product_categories"] = ProductCategory.objects.all().order_by("name")
            context["service_categories"] = ServiceCategory.objects.all().order_by("name")
            context["course_programs"] = Program.objects.all().order_by("name")
            context["registration_types"] = RegistrationType.objects.all().order_by("name")
            context["services"] = Service.objects.all()
            context["products"] = Product.objects.all()
        except Exception as e:
            logger.error(f"Error in fetching the context data of home view: {e}")
        return context
