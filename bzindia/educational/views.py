from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from django.views.generic import View, DetailView
import logging

from superadmin.views import BaseEducationCompanyView

from .models import Program, Specialization, Course, Testimonial
from company.models import Company, Client

from company.views import CompanyBaseView
    
logger = logging.getLogger(__name__)

class GetProgramsView(BaseEducationCompanyView, View):
    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({
                "status": "failed",
                "error": "Method Not Allowed"
            }, status=403)

        company_slug = request.GET.get("company")        

        if not company_slug:
            return JsonResponse({
                "status": "failed",
                "error": "Missing required parameters"
            }, status=400)

        try:
            education_company = get_object_or_404(Company, slug=company_slug, type__name = "Education")

            programs = Program.objects.filter(company=education_company).values("name", "slug")

            return JsonResponse({
                "status": "success",
                "programs": list(programs)
            }, status=200)

        except Http404:
            return JsonResponse({
                "status": "failed",
                "error": "Company not found"
            }, status=404)
        except Exception as e:
            logger.exception(f"Unexpected error in GetProgramsView: {e}")
            return JsonResponse({
                "status": "failed",
                "error": "An unexpected error occurred"
            }, status=500)
        

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
        

class HomeView(CompanyBaseView, DetailView):
    model = Company
    template_name = "education/home.html"
    context_object_name = "company"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object()

        context["courses"] = Course.objects.filter(company = self.object).order_by("?")
        context["clients"] = Client.objects.filter(company = self.object).order_by("?")
        context["testimonials"] = Testimonial.objects.filter(company = self.object).order_by("order")
        context["nearby_courses"] = Course.objects.all().order_by("?")

        return context