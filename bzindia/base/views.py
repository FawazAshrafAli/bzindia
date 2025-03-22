from django.shortcuts import render
from django.views.generic import View

from company.models import Company, CompanyType
from blog.models import Blog

class BaseView(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["company_types"] = CompanyType.objects.all().order_by("name")
        context["slider_blogs"] = Blog.objects.all().order_by("?")[:3]


        return context
