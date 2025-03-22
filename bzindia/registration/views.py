from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from django.views.generic import View
import logging

from superadmin.views import BaseRegistrationCompanyView

from company.models import Company
from registration.models import RegistrationType, RegistrationSubType

logger = logging.getLogger(__name__)

class GetRegistrationTypeView(BaseRegistrationCompanyView, View):
    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({
                "status": "failed",
                "error": "Method Not Allowed"
            }, status=403)

        company_slug = request.GET.get("company_slug")

        if not company_slug:
            return JsonResponse({
                "status": "failed",
                "error": "Missing required parameters"
            }, status=400)

        try:
            current_company = get_object_or_404(Company, slug=company_slug)

            types = RegistrationType.objects.filter(company=current_company).values("name", "slug")

            return JsonResponse({
                "status": "success",
                "types": list(types)
            }, status=200)

        except Http404:
            return JsonResponse({
                "status": "failed",
                "error": "Company not found"
            }, status=404)
        except Exception as e:
            logger.exception(f"Error in get function of GetRegistrationTypeView: {e}")
            return JsonResponse({
                "status": "failed",
                "error": "An unexpected error occurred"
            }, status=500)
        

class GetRegistrationSubTypeView(BaseRegistrationCompanyView, View):
    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({
                "status": "failed",
                "error": "Method Not Allowed"
            }, status=403)

        company_slug = request.GET.get("company_slug")
        type_slug = request.GET.get("type_slug")

        if not company_slug or not type_slug:
            return JsonResponse({
                "status": "failed",
                "error": "Missing required parameters"
            }, status=400)

        try:
            current_company = get_object_or_404(Company, slug=company_slug)
            type = get_object_or_404(RegistrationType, slug=type_slug, company=current_company)

            sub_types = RegistrationSubType.objects.filter(
                company=current_company, type=type
            ).values("name", "slug")

            return JsonResponse({
                "status": "success",
                "sub_types": list(sub_types)
            }, status=200)

        except Http404:
            return JsonResponse({
                "status": "failed",
                "error": "Company or registration type not found"
            }, status=404)
        except Exception as e:
            logger.exception(f"Unexpected error in GetSubTypeView of registration app: {e}")
            return JsonResponse({
                "status": "failed",
                "error": "An unexpected error occurred"
            }, status=500)