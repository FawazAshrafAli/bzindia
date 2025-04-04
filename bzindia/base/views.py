from django.shortcuts import render
from django.views.generic import View
from django.db.models import Q


from company.models import Company, CompanyType
from directory.models import TouristAttraction


class BaseView(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["company_types"] = CompanyType.objects.all().order_by("name")

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
                ).order_by("?")[:12]     

        return context
