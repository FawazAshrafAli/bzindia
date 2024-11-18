from django.shortcuts import render
from rest_framework import viewsets

from company.models import Company
from .serializers import CompanySerializer

class CompanyApiViewset(viewsets.ModelViewSet):
    model = Company
    serializer_class = CompanySerializer
    queryset = model.objects.all()
