from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from django.views.generic import View
import logging

from superadmin.views import BaseEducationCompanyView

from .models import Program, Specialization, Course
from company.models import Company

logger = logging.getLogger(__name__)

class GetSpecializationsView(BaseEducationCompanyView, View):
    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({
                "status": "failed",
                "error": "Method Not Allowed"
            }, status=403)

        company_slug = request.GET.get("company")
        program_slug = request.GET.get("program")

        if not company_slug or not program_slug:
            return JsonResponse({
                "status": "failed",
                "error": "Missing required parameters"
            }, status=400)

        try:
            current_company = get_object_or_404(Company, slug=company_slug)
            program = get_object_or_404(Program, slug=program_slug, company=current_company)

            specializations = Specialization.objects.filter(
                company=current_company, program=program
            ).values("name", "slug")

            return JsonResponse({
                "status": "success",
                "specializations": list(specializations)
            }, status=200)

        except Http404:
            return JsonResponse({
                "status": "failed",
                "error": "Company or program not found"
            }, status=404)
        except Exception as e:
            logger.exception(f"Unexpected error in GetSpecializationsView: {e}")
            return JsonResponse({
                "status": "failed",
                "error": "An unexpected error occurred"
            }, status=500)


class GetCourseView(BaseEducationCompanyView, View):
    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({
                "status": "failed",
                "error": "Method Not Allowed"
            }, status=403)

        company_slug = request.GET.get("company")
        program_slug = request.GET.get("program")

        if not company_slug or not program_slug:
            return JsonResponse({
                "status": "failed",
                "error": "Missing required parameters"
            }, status=400)

        try:
            courses = Course.objects.filter(
                company__slug = company_slug, program__slug = program_slug
            ).values("name", "slug")

            return JsonResponse({
                "status": "success",
                "courses": list(courses)
            }, status=200)

        except Http404:
            return JsonResponse({
                "status": "failed",
                "error": "Company or program not found"
            }, status=404)
        except Exception as e:
            logger.exception(f"Unexpected error in GetCourseView: {e}")
            return JsonResponse({
                "status": "failed",
                "error": "An unexpected error occurred"
            }, status=500)