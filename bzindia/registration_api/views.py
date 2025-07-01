from rest_framework import viewsets, status, serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.http import Http404

from .serializers import (
    SubTypeSerializer, DetailSerializer, TypeSerializer, 
    EnquirySerializer
    )
from company_api.serializers import CompanySerializer

from registration.models import RegistrationSubType, RegistrationDetailPage, RegistrationType, Enquiry, MultiPage
from company.models import Company

from .paginations import RegistrationPagination

import logging

logger = logging.getLogger(__name__)

class SubTypeApiViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubTypeSerializer

    def get_queryset(self):
        slug = self.kwargs.get("company_slug")

        if slug:
            return RegistrationSubType.objects.filter(company__slug = slug)
        
        return RegistrationSubType.objects.none()


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.filter(type__name = "Registration")
    lookup_field = "slug"


class TypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TypeSerializer

    def get_queryset(self):
        slug = self.kwargs.get("company_slug")

        if slug:
            return RegistrationType.objects.filter(company__slug = slug)
        
        return RegistrationType.objects.none()


class DetailViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DetailSerializer
    lookup_field = "slug"
    pagination_class = RegistrationPagination

    def get_queryset(self):
        slug = self.kwargs.get("company_slug")
        registration_type = self.request.query_params.get("type")

        if slug:
            filters = {"company__slug": slug}  

            if registration_type:       
                filters["registration_sub_type__type__name"] = registration_type

            return RegistrationDetailPage.objects.filter(**filters)
        
        return RegistrationDetailPage.objects.none()


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
            print(e)

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