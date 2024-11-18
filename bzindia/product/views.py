from django.shortcuts import render
from django.views.generic import ListView

from home.views import BaseHomeView
from .models import Product, Category, SubCategory

class ProductListView(BaseHomeView, ListView):
    model = Product
    queryset = model.objects.all().order_by("name")
    context_object_name = "products"
    template_name = "products/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all().order_by("name")
        context["sub_categories"] = SubCategory.objects.all().order_by("name")
        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with"):
            pass
