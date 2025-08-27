# Rest Framework Libraries
from rest_framework.response import Response
from rest_framework import viewsets, status, serializers
from rest_framework.permissions import AllowAny

# Django Libraries
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import Http404
import logging

# Model Imports
from educational.models import (
    Course, Testimonial, Faq, Enquiry, Program, CourseDetail, Specialization
    )

from company.models import Company, Client

from .serializers import (
    CourseSerializer, StudentTestimonialSerializer, 
    CourseFaqSerializer, EnquirySerializer, ProgramSerializer, 
    DetailSerializer, SpecializationSerializer
    )

from company_api.serializers import CompanySerializer, ClientSerializer

from .paginations import CoursePagination

logger = logging.getLogger(__name__)

class CourseApiViewset(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    lookup_field = "slug"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class InstituteCourseDetailViewSet(viewsets.ModelViewSet):
    serializer_class = DetailSerializer

    def get_queryset(self):
        slug = self.kwargs.get("company_slug")

        if slug:
            return CourseDetail.objects.filter(company__slug = slug)

        return CourseDetail.objects.none()
        

class ProgramViewset(viewsets.ModelViewSet):
    serializer_class = ProgramSerializer
    lookup_field = "slug"

    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")
    
        if company_slug:
            return Program.objects.filter(company__slug = company_slug).order_by("?")
        
        return Program.objects.none()
    

class SpecializationViewset(viewsets.ModelViewSet):
    serializer_class = SpecializationSerializer
    pagination_class = CoursePagination
    lookup_field = "slug"

    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")
        program_slug = self.request.query_params.get("program")
    
        if company_slug:
            filters = {"company__slug": company_slug}

            if program_slug:
                filters["program__slug"] = program_slug

            return Specialization.objects.filter(**filters).order_by("?")
        
        return Specialization.objects.none()
        
    

class EducationCompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.filter(type__name = "Education")
    lookup_field = "slug"


class CorporatePartnersViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer

    def get_queryset(self):
        queryset = Client.objects.filter(company__type__name = "Education")
        
        company_slug = self.request.query_params.get('company_slug')
        if company_slug:
            queryset = queryset.filter(company__slug=company_slug)
            
        return queryset.order_by("?")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class StudentTestimonialViewSet(viewsets.ModelViewSet):
    serializer_class = StudentTestimonialSerializer

    def get_queryset(self):
        queryset = Testimonial.objects.all()
        
        company_slug = self.request.query_params.get('company_slug')
        if company_slug:
            queryset = queryset.filter(company__slug=company_slug)
            
        return queryset.order_by("?")


class CourseFaqViewSet(viewsets.ModelViewSet):
    serializer_class = CourseFaqSerializer
    queryset = Faq.objects.all().order_by("?")[:5]


class CompanyCoursesViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.filter(company__slug=self.kwargs.get("company_slug")) if self.kwargs.get("company_slug") else Course.objects.none()


class EnquiryViewSet(viewsets.ModelViewSet):
    serializer_class = EnquirySerializer
    http_method_names = ["post", "get"]
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Enquiry.objects.filter(company__slug=self.kwargs.get("company_slug")) if self.kwargs.get("company_slug") else Enquiry.objects.none()

    def create(self, request, *args, **kwargs):
        response_data = {
            "success": False,
            "message": "Validation Failed",
            "errors": None
        }

        try:
            company_slug = self.kwargs.get("company_slug")
            if not company_slug:
                response_data["message"] = "Company identifier missing"
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            company = get_object_or_404(Company, slug = company_slug)
            
            enquiry_data = request.data.copy()
            enquiry_data["company"] = company
            serializer = self.get_serializer(data=enquiry_data)
            serializer.is_valid(raise_exception=True)
            
            serializer.save(company = company)

            response_data.update({
                "success": True,
                "message": "Enquiry submitted successfully",
                "data": serializer.data
            })
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Http404:
            response_data.update({
                "message": "Invalid company specified",
                "error": "Company not found"
            })
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except serializers.ValidationError as e:
            response_data.update({
                "message": "Validation error",
                "errors": e.detail
            })
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception(
                f"Enquiry submission error - Company: {company_slug}, "
            )
            response_data.update({
                "message": "Server error processing your enquiry",
                "error": "Internal server error"
            })
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DetailViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DetailSerializer
    lookup_field = "slug"
    pagination_class = CoursePagination

    def get_queryset(self):
        slug = self.kwargs.get("company_slug")
        program = self.request.query_params.get("program")
        specialization_slug = self.request.query_params.get("specialization")

        if slug:
            if slug == "all":
                return CourseDetail.objects.all()

            filters = {"company__slug": slug}

            if program:
                filters["course__program__name"] = program

            if specialization_slug:
                filters["course__specialization__slug"] = specialization_slug

            return CourseDetail.objects.filter(**filters)
        
        return CourseDetail.objects.none()