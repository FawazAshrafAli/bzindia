from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
import logging

from .models import SubCategory, Category, Service, ServiceDetail

logger = logging.getLogger(__name__)

class GetCategoriesView(View):
    model = Category

    def get(self, request, *args, **kwargs):
        try:
            if request.headers.get('x-requested-with') != "XMLHttpRequest":
                return JsonResponse({"status": "failed", "error": "Method not allowed"}, status=405)    
            
            company_slug = request.GET.get("company_slug")

            if not company_slug:
                return JsonResponse({"status": "failed", "error": "Bad Request"}, status=400)
            
            categories = list(self.model.objects.filter(company__slug = company_slug).values("name", "slug"))

            return JsonResponse({"status": "success", "categories": categories}, status=200)

        except Exception as e:
            logger.exception(f"Error in get function of GetCategoriesView in service app: {e}")
            return JsonResponse({"status": "failed", "error": "Some unexpected error occurred."}, status=500)


class GetSubCategoriesView(View):
    model = SubCategory

    def get(self, request, *args, **kwargs):
        try:
            if request.headers.get('x-requested-with') != "XMLHttpRequest":
                return JsonResponse({"status": "failed", "error": "Method not allowed"}, status=405)    
            
            company_slug = request.GET.get("company_slug")
            category_slug = request.GET.get("category_slug")

            if not company_slug or not category_slug:
                return JsonResponse({"status": "failed", "error": "Bad Request"}, status=400)
            
            sub_categories = list(self.model.objects.filter(company__slug = company_slug, category__slug = category_slug).values("name", "slug"))

            return JsonResponse({"status": "success", "sub_categories": sub_categories}, status=200)

        except Exception as e:
            logger.exception(f"Error in get function of GetSubCategoriesView in service app: {e}")
            return JsonResponse({"status": "failed", "error": "Some unexpected error occurred."}, status=500)


class GetServicesView(View):
    model = Service

    def get(self, request, *args, **kwargs):
        try:
            if request.headers.get('x-requested-with') != "XMLHttpRequest":
                return JsonResponse({"status": "failed", "error": "Method not allowed"}, status=405)    
            
            company_slug = request.GET.get("company_slug")
            sub_category_slug = request.GET.get("sub_category_slug")

            if not company_slug or not sub_category_slug:
                return JsonResponse({"status": "failed", "error": "Bad Request"}, status=400)
            
            services = list(self.model.objects.filter(company__slug = company_slug, sub_category__slug = sub_category_slug).values("name", "slug"))

            return JsonResponse({"status": "success", "services": services}, status=200)

        except Exception as e:
            logger.exception(f"Error in get function of GetServicesView in service app: {e}")
            return JsonResponse({"status": "failed", "error": "Some unexpected error occurred."}, status=500)


class GetServiceDetailsView(View):
    model = ServiceDetail

    def get(self, request, *args, **kwargs):
        try:
            if request.headers.get('x-requested-with') != "XMLHttpRequest":
                return JsonResponse({"status": "failed", "error": "Method not allowed"}, status=405)    
            
            company_slug = request.GET.get("company_slug")
            sub_category_slug = request.GET.get("sub_category_slug")

            print(sub_category_slug)

            if not company_slug or not sub_category_slug:
                return JsonResponse({"status": "failed", "error": "Bad Request"}, status=400)
            
            service_details = list(self.model.objects.filter(company__slug = company_slug, service__sub_category__slug = sub_category_slug).values("service__name", "slug"))
            print(service_details)

            return JsonResponse({"status": "success", "service_details"
            "": service_details}, status=200)

        except Exception as e:
            logger.exception(f"Error in get function of GetServicesView in service app: {e}")
            return JsonResponse({"status": "failed", "error": "Some unexpected error occurred."}, status=500)