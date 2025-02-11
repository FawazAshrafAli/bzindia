from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.generic import ListView, View
from django.db.models import Q, Count
import logging

from .models import Product, Category, SubCategory, Brand, Color, Size
from home.views import BaseHomeView

logger = logging.getLogger(__name__)

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
            logger.exception(f"Error in get function of GetSubCategoriesView in product app: {e}")
            return JsonResponse({"status": "failed", "error": "Some unexpected error occured."}, status=500)


class GetProductsView(View):
    model = Product

    def get(self, request, *args, **kwargs):
        try:
            if request.headers.get('x-requested-with') != "XMLHttpRequest":
                return JsonResponse({"status": "failed", "error": "Method not allowed"}, status=405)    
            
            company_slug = request.GET.get("company_slug")
            sub_category_slug = request.GET.get("sub_category_slug")

            if not company_slug or not sub_category_slug:
                return JsonResponse({"status": "failed", "error": "Bad Request"}, status=400)
            
            products = list(self.model.objects.filter(company__slug = company_slug, sub_category__slug = sub_category_slug).values("name", "slug"))

            return JsonResponse({"status": "success", "products": products}, status=200)

        except Exception as e:
            logger.exception(f"Error in get function of GetProductsView in product app: {e}")
            return JsonResponse({"status": "failed", "error": "Some unexpected error occured."}, status=500)


class ProductListView(BaseHomeView, ListView):
    model = Product
    queryset = model.objects.all().order_by("name")
    context_object_name = "products"
    template_name = "products/list.html"

    def get_filter_data(self, request):
        keywords = request.GET.get("keywords")
        sub_category_slug = request.GET.get("sub_category")
        category_slug = request.GET.get("category")
        checked_brands = request.GET.getlist("checked_brands[]")
        checked_dimensions = request.GET.getlist("checked_dimensions[]")
        checked_colors = request.GET.getlist("checked_colors[]")

        data = {
            "keywords": keywords,
            "sub_category_slug": sub_category_slug,
            "category_slug": category_slug,
            "checked_brands": checked_brands,
            "checked_dimensions": checked_dimensions,
            "checked_colors": checked_colors
        }

        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all().order_by("name")
        context["sub_categories"] = SubCategory.objects.all().order_by("name")

        error_msg = "No products to display"

        products = self.queryset

        filtering_data = self.get_filter_data(self.request)

        if filtering_data["category_slug"]:
            products = products.filter(category__slug = filtering_data["category_slug"])
        if filtering_data["sub_category_slug"]:
            products = products.filter(sub_category__slug = filtering_data["sub_category_slug"])

        if filtering_data["keywords"]:
            products = products.filter(
                Q(name__icontains = filtering_data["keywords"]) | 
                Q(category__name__icontains = filtering_data["keywords"]) | 
                Q(sub_category__name__icontains = filtering_data["keywords"]) |
                Q(brand__name__icontains = filtering_data["keywords"])
                )
        
        brand_ids = products.values_list('brand', flat=True).distinct()
        brands = Brand.objects.filter(id__in=brand_ids)

        list_brands = []
        for brand in brands:
            list_brands.append({
                "name": brand.name,             
                "slug": brand.slug,
                "count": products.filter(brand = brand).count()
            })

        context["brands"] = list_brands        

        if self.queryset and filtering_data["keywords"]:
            error_msg = "No product found with the given keywords."        

        context["error_msg"] = error_msg
        context["keywords"] = filtering_data["keywords"]
        context["current_sub_category"] = filtering_data["sub_category_slug"]
        context["current_category"] = filtering_data["category_slug"]

        return context
    
    def get_queryset(self):
        filtering_data = self.get_filter_data(self.request)

        products = self.queryset

        if filtering_data["category_slug"]:
            category = get_object_or_404(Category, slug = filtering_data["category_slug"])
            products = products.filter(category = category)

        if filtering_data["sub_category_slug"]:
            sub_category = get_object_or_404(SubCategory, slug = filtering_data["sub_category_slug"])  
            products = products.filter(sub_category = sub_category)
    
        if filtering_data["keywords"]:
            products = products.filter(
                Q(name__icontains = filtering_data["keywords"]) | 
                Q(category__name__icontains = filtering_data["keywords"]) | 
                Q(sub_category__name__icontains = filtering_data["keywords"]) |
                Q(brand__name__icontains = filtering_data["keywords"])
                )
            
        return products

    def get(self, request, *args, **kwargs):
        try:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                data = {}

                filtering_data = self.get_filter_data(request)

                products = brand_products = dimension_products = color_products = self.queryset

                if filtering_data["category_slug"]:
                    category = get_object_or_404(Category, slug = filtering_data["category_slug"])

                    sub_categories = list(SubCategory.objects.filter(category = category).values("name", "slug"))

                    products = brand_products = dimension_products = color_products = products.filter(category = category)                                  

                    list_products = []
                    for product in products:
                        list_products.append({
                            "name": product.name,
                            "image": product.image.url,
                            "price": product.price,
                            "slug": product.slug
                        })

                    data["products"] = list_products
                    if not filtering_data["checked_brands"]:
                        data["sub_categories"] = sub_categories
                                        
                
                if filtering_data["sub_category_slug"]:
                    sub_category = get_object_or_404(SubCategory, slug = filtering_data["sub_category_slug"])

                    if sub_category:
                        products = brand_products = dimension_products = color_products = products.filter(sub_category = sub_category)               

                    list_products = []
                    for product in products:
                        list_products.append({
                            "name": product.name,
                            "image": product.image.url,
                            "price": product.price,
                            "slug": product.slug
                        })

                    data["products"] = list_products

                    if sub_category:
                        data["current_catalog"] = sub_category.name

                    dimensions = {product.get_dimension for product in dimension_products}

                    list_dimensions = []
                    for dimension in dimensions:
                        if dimension:
                            count = sum(1 for product in products if product.get_dimension == dimension)
                            list_dimensions.append({
                                "name": dimension,
                                "count": count,
                            })

                    data["dimensions"] = list_dimensions

                if filtering_data["checked_brands"]:                    
                    brand_products = products                    
                    products = products.filter(brand__slug__in=filtering_data["checked_brands"]).distinct()

                    list_products = []
                    for product in products:
                        list_products.append({
                            "name": product.name,
                            "image": product.image.url,
                            "price": product.price,
                            "slug": product.slug
                        })

                    data["products"] = list_products
                    data["checked_brands"] = filtering_data["checked_brands"]
                    if filtering_data["checked_dimensions"]:
                        data["checked_dimensions"] = filtering_data["checked_dimensions"]

                else:
                    list_products = []
                    for product in products:
                        list_products.append({
                            "name": product.name,
                            "image": product.image.url,
                            "price": product.price,
                            "slug": product.slug
                        })

                    data["products"] = list_products

                if filtering_data["checked_dimensions"]:
                    dimension_products = products

                    dimension_products = []

                    for product in products:                        
                        if product.get_dimension in filtering_data["checked_dimensions"]:
                            dimension_products.append(product)                   

                    list_products = []
                    for product in dimension_products:
                        list_products.append({
                            "name": product.name,
                            "image": product.image.url,
                            "price": product.price,
                            "slug": product.slug
                        })

                    data["products"] = list_products
                    data["checked_dimensions"] = filtering_data["checked_dimensions"]
                    if filtering_data["checked_brands"]:
                        data["checked_brands"] = filtering_data["checked_brands"]

                else:
                    list_products = []
                    for product in products:
                        list_products.append({
                            "name": product.name,
                            "image": product.image.url,
                            "price": product.price,
                            "slug": product.slug
                        })

                    data["products"] = list_products

                if filtering_data["checked_colors"]:                    
                    color_products = products                    
                    products = products.filter(colors__slug__in=filtering_data["checked_colors"]).distinct()

                    list_products = []
                    for product in products:
                        list_products.append({
                            "name": product.name,
                            "image": product.image.url,
                            "price": product.price,
                            "slug": product.slug
                        })                    

                    data["products"] = list_products
                    data["checked_colors"] = filtering_data["checked_colors"]
                    if filtering_data["checked_dimensions"]:
                        data["checked_dimensions"] = filtering_data["checked_dimensions"]

                else:
                    list_products = []
                    for product in products:
                        list_products.append({
                            "name": product.name,
                            "image": product.image.url,
                            "price": product.price,
                            "slug": product.slug
                        })

                    data["products"] = list_products


                brands_ids = brand_products.values_list('brand', flat=True).distinct()
                brands = Brand.objects.filter(id__in =brands_ids)

                list_brands = []
                for brand in brands:
                    list_brands.append({
                        "name": brand.name,             
                        "slug": brand.slug,
                        "count": brand_products.filter(brand = brand).count()
                    })

                data["brands"] = list_brands


                color_counts = (
                    color_products
                    .values('colors__id')
                    .annotate(count=Count('id', distinct=True))
                    .order_by('colors__name')
                )

                color_ids = [item['colors__id'] for item in color_counts]
                colors = Color.objects.filter(id__in=color_ids)

                color_count_map = {item['colors__id']: item['count'] for item in color_counts}                

                list_colors = []
                for color in colors:
                    list_colors.append({
                        "name": color.name,
                        "slug": color.slug,
                        "hexa": color.hexa,
                        "count": color_count_map.get(color.id, 0)
                    })

                data["colors"] = list_colors

                size_ids = products.values_list('sizes__id', flat=True).distinct()
                sizes = Size.objects.filter(id__in = size_ids)

                size_counts = products.values('sizes__id').annotate(product_count=Count('id'))
                size_count_map = {item['sizes__id']: item['product_count'] for item in size_counts}

                list_sizes = []
                for size in sizes:
                    list_sizes.append({
                        "name": size.name,             
                        "slug": size.slug,
                        "count": size_count_map.get(size.id, 0)
                    })

                data["sizes"] = list_sizes

                return JsonResponse(data)

        except Http404:
            return JsonResponse({"error": "Invalid category"})

        except Exception as e:
            error_msg = "Error in get function of product list view."
            logger.exception(f"{error_msg}: {e}")

            return JsonResponse({"error": error_msg})

        return super().get(request, *args, **kwargs)
    
