from django.shortcuts import render, redirect
from django.views.generic import View
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
import requests, os, logging

from service.models import Service
from company.models import Company, CompanyType
from directory.models import TouristAttraction
from locations.models import Place

logger = logging.getLogger(__name__)

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
    

class GetLocalPlacesView(View):
    def get(self, request, *args, **kwargs):
        pincode = self.kwargs.get("pincode")

        places = Place.objects.filter(pincode = pincode).distinct().order_by("name")
        list_places = list(places.values("name", "slug"))

        data = {
            "success": True, "places": list_places, "pincode": pincode
        }

        first_location = places.first() if places else None

        if first_location:
            place = first_location.name
            district = first_location.district.name
            state = first_location.state.name
            latitude = first_location.latitude
            longitude = first_location.longitude

            data.update({
                "place": place,
                "district": district,
                "state": state
            })

            services = Service.objects.all().order_by("?")

            service_schema = {
                "@context": "http://schema.org",
                "@type": "ItemList",
                "itemListElement": [
                    {
                    "@type": "ListItem",
                    "position": f"{index + 1}",
                    "item": {
                        "@type": "Service",
                        "provider": {
                        "@type": "Organization",
                        "name": f"{service.company.name}",
                        "url": f"https://www.bzindia.in/company/{service.company.slug}",
                        "logo": f"https://www.bzindia.in{service.company.logo.url if service.company.logo else '/#'}",
                        "address": {
                            "@type": "PostalAddress",
                            "streetAddress": f"{place}",
                            "addressLocality": f"{district}",
                            "addressRegion": f"{state}",
                            "postalCode": f"{pincode}",
                            "addressCountry": "IN"
                        },
                        "location": {
                            "@type": "Place",
                            "geo": {
                            "@type": "GeoCoordinates",
                            "latitude": f"{latitude}",
                            "longitude": f"{longitude}"
                            }
                        }
                        },
                        "name": f"{service.name}",
                        "description": f"{service.description}",
                        "image": f"https://www.bzindia.in/{service.image.url if service.image else '#'}",
                        "url": f"https://www.bzindia.in/service/{service.slug}"
                    }
                    } for index, service in enumerate(services)
                ]
            }

            data["service_schema"] = service_schema

        return JsonResponse(data)


class GetPincodeView(View):
    def get(self, request, *args, **kwargs):
        try:
            if request.headers.get("x-requested-with") != "XMLHttpRequest":
                return JsonResponse({"failed": True, "message": "Method Not Allowed"}, status=403)

            latitude = self.kwargs.get("latitude")
            longitude = self.kwargs.get("longitude")

            opencage_api = os.getenv('OPENCAGE_API_KEY_1') 

            if not latitude or not longitude or not opencage_api:
                return JsonResponse({"failed": True, "message": "Bad Request"}, status=400)

            url = f'https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={opencage_api}'

            response = requests.get(url)
            data = response.json()

            if not data['results'] or not data['results'][0]['components']['postcode']:
                return JsonResponse({"failed": True, "message": "Not Found"}, status=404)

            pincode = data['results'][0]['components']['postcode']

            return redirect(reverse_lazy('base:get_places', kwargs = {'pincode': pincode}))
        
        except Exception as e:
            logger.exception(f"Error in get function of GetPincodeView of base app: {e}")
            return JsonResponse({"failed": True, "message": "An unexpected error occured"}, status=500)
