from django.shortcuts import render
from django.views.generic import TemplateView, View, ListView
from django.db.models import Q
import logging

from company.models import Company
from product.models import Product, Category as ProductCategory
from service.models import Service, Category as ServiceCategory
from registration.models import RegistrationSubType
from educational.models import Course

from directory.models import TouristAttraction

from base.views import BaseView

logger = logging.getLogger(__name__)

class HomeView(BaseView, TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["companies"] = Company.objects.all().order_by("name")
            # context["service_categories"] = ServiceCategory.objects.all().order_by("name")
            context["courses"] = Course.objects.all().order_by("name")
            context["registration_sub_types"] = RegistrationSubType.objects.values("name", "slug", "type__name").order_by("name")
            context["services"] = Service.objects.all().order_by("name")
            context["products"] = Product.objects.all().order_by("name")
            
            context["attractions"] = TouristAttraction.objects.filter(
                Q(name__isnull=False) & (
                    Q(historic_type__isnull=False) | 
                    Q(waterway_type__isnull=False) | 
                    Q(waterbody_type__isnull=False)
                )
                ).exclude(
                    Q(historic_type="yes") & 
                    Q(waterway_type="yes") & 
                    Q(waterbody_type="yes")
                ).order_by("?")[:10]
        except Exception as e:
            logger.error(f"Error in fetching the context data of home view: {e}")
        return context
