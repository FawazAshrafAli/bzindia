from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers import MetaTagSerializer, ItemSerializer
from .paginations import ItemPagination, MetaTagPagination

from service.models import MetaTag
from product.models import ProductDetailPage
from service.models import ServiceDetail
from registration.models import RegistrationDetailPage
from educational.models import CourseDetail

class MetaTagApiViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = MetaTagSerializer
    queryset = MetaTag.objects.all().order_by("?")
    lookup_field = "slug"
    pagination_class = MetaTagPagination


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = []
    pagination_class = ItemPagination
    serializer_class = ItemSerializer

    def list(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")

        if not slug:
            return Response({"items": "Slug is not provided"}, status=status.HTTP_400_BAD_REQUEST)

        items = []

        product_details = ProductDetailPage.objects.filter(meta_tags__slug = slug)
        service_details = ServiceDetail.objects.filter(meta_tags__slug = slug)
        course_details = CourseDetail.objects.filter(meta_tags__slug = slug)
        registration_details = RegistrationDetailPage.objects.filter(meta_tags__slug = slug)

        items += [{
            "title": detail.product.name,
            "image_url": request.build_absolute_uri(detail.product.image.url) if detail.product.image and detail.product.image.name else "",
            "summary": detail.summary,
            "company_name": detail.company.name,
            "company_type_name": detail.company.type.name,
            "company_type_slug": detail.company.type.slug,
            "company_slug": detail.company.slug,
            "meta_description": detail.meta_description,
            "price": detail.product.price,
            "slug": detail.slug,
            "updated": detail.updated,
            "url": f"{detail.company.slug}/{detail.product.category.slug}/{detail.product.sub_category.slug}/{detail.slug}"
            } for detail in product_details]
        
        items += [{
            "title": detail.service.name,
            "image_url": request.build_absolute_uri(detail.service.image.url) if detail.service.image and detail.service.image.name else "",
            "summary": detail.summary,
            "company_name": detail.company.name,
            "company_type_name": detail.company.type.name,
            "company_type_slug": detail.company.type.slug,
            "company_slug": detail.company.slug,
            "meta_description": detail.meta_description,
            "price": detail.service.price,
            "slug": detail.slug,
            "updated": detail.updated,
            "url": f"{detail.company.slug}/{detail.service.category.slug}/{detail.service.sub_category.slug}/{detail.slug}"
            } for detail in service_details]
        
        items += [{
            "title": detail.registration.title,
            "image_url": None,
            "summary": detail.summary,
            "company_name": detail.company.name,
            "company_type_name": detail.company.type.name,
            "company_type_slug": detail.company.type.slug,
            "company_slug": detail.company.slug,
            "meta_description": detail.meta_description,
            "price": "",
            "slug": detail.slug,
            "updated": detail.updated,
            "url": f"{detail.company.slug}/{detail.registration.registration_type.slug}/{detail.registration.sub_type.slug}/{detail.slug}"
            } for detail in registration_details]
        
        items += [{
            "title": detail.course.name,
            "image_url": request.build_absolute_uri(detail.course.image.url) if detail.course.image and detail.course.image.name else "",
            "summary": detail.summary,
            "company_name": detail.company.name,
            "company_type_name": detail.company.type.name,
            "company_type_slug": detail.company.type.slug,
            "company_slug": detail.company.slug,
            "meta_description": detail.meta_description,
            "price": detail.course.price,
            "slug": detail.slug,    

            "mode": detail.course.mode,
            "start_date": detail.course.starting_date.date(),
            "end_date": detail.course.ending_date.date(),
            "duration": detail.course.duration,
            "category": detail.course.program.name,
            "rating": detail.course.rating,
            "rating_count": detail.course.rating_count,
            "updated": detail.updated,

            "url": f"{detail.company.slug}/{detail.course.program.slug}/{detail.course.specialization.slug}/{detail.slug}"

            } for detail in course_details]
        
        paginated_items = self.paginate_queryset(items)
        serializer = self.get_serializer(paginated_items, many=True)

        return self.get_paginated_response(serializer.data)