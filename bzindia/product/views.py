from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.generic import ListView
from django.db.models import Q, Count
import logging

from .models import Product, Category, SubCategory, Brand, Color, Size
from home.views import BaseHomeView

logger = logging.getLogger(__name__)

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

        data = {
            "keywords": keywords,
            "sub_category_slug": sub_category_slug,
            "category_slug": category_slug,
            "checked_brands": checked_brands,
            "checked_dimensions": checked_dimensions
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

                products = product_brands = product_dimensions = self.queryset

                if filtering_data["category_slug"]:
                    category = get_object_or_404(Category, slug = filtering_data["category_slug"])

                    sub_categories = list(SubCategory.objects.filter(category = category).values("name", "slug"))

                    products = product_brands = product_dimensions = products.filter(category = category)                                  

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
                        products = product_brands = product_dimensions = products.filter(sub_category = sub_category)               

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

                    dimensions = {product.get_dimension for product in product_dimensions}

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
                    product_brands = products                    
                    products = products.filter(brand__slug__in=filtering_data["checked_brands"])

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
                    product_dimensions = products

                    dimension_products = []

                    for product in products:                        
                        if product.get_dimension in filtering_data["checked_dimensions"]:
                            dimension_products.append(product)                   

                    print(dimension_products)                

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


                brands_ids = product_brands.values_list('brand', flat=True).distinct()
                brands = Brand.objects.filter(id__in =brands_ids)

                list_brands = []
                for brand in brands:
                    list_brands.append({
                        "name": brand.name,             
                        "slug": brand.slug,
                        "count": product_brands.filter(brand = brand).count()
                    })

                data["brands"] = list_brands            

                color_ids = products.values_list('colors__id', flat=True).distinct()
                colors = Color.objects.filter(id__in = color_ids)

                color_counts = products.values('colors__id').annotate(product_count=Count('id'))
                color_count_map = {item['colors__id']: item['product_count'] for item in color_counts}

                list_colors = []
                for color in colors:
                    list_colors.append({
                        "name": color.name,
                        "hexa": color.hexa,             
                        "slug": color.slug,
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