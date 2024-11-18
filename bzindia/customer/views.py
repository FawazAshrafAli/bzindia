from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404, JsonResponse
import logging

from company.models import Company
from product.models import Category as ProductCategory, Brand, Size, Color, Product, SubCategory as ProductSubCategory

logger = logging.getLogger(__name__)

class CustomerBaseView(LoginRequiredMixin, View):
    login_url = reverse_lazy("authentication:customer_login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["company"] = get_object_or_404(Company, email = self.request.user.email)
            context["categories"] = ProductCategory.objects.all()
            context["brands"] = Brand.objects.all()
            context["standards"] = sorted(["UK", "US", "EU", "JP", "INT", "AUS", "FR"])
        except Exception as e:
            logger.error("Error in fetching context data for Customer Base View: {e}")
        return context
    

class CustomerHomeView(CustomerBaseView, TemplateView):
    template_name = "customer/home.html"


# For Product based company
class BaseProductCategoryView(CustomerBaseView, View):
    model = ProductCategory
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_category_page"] = True
        return context
    

class AddProductCategoryView(BaseProductCategoryView, CreateView):
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("customer:product_categories")

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                product, created = self.model.objects.get_or_create(name = name)

                if created:
                    messages.success(request, "Success! Product category created.")
                    return redirect(self.success_url)

                else:
                    messages.warning(request, "Category already exists.")
            
            else:
                messages.error(request, "Category name is required.")                        
        
        except Exception as e:
            logger.error(f"Error in creating product category: {e}")
            messages.error("Server Error.")

        return redirect(self.redirect_url)
    

class UpdateProductCategoryView(BaseProductCategoryView, UpdateView):
    fields = ["name", "slug"]
    success_url = redirect_url = reverse_lazy("customer:product_categories")

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                if not self.model.objects.filter(name = name).exists():
                    self.object = self.get_object()

                    self.object.name = name
                    self.object.slug = None
                    self.object.save()
                    
                    messages.success(request, "Success! Product category updated.")
                    return redirect(self.success_url)

                else:
                    messages.warning(request, "Category already exists.")
            
            else:
                messages.error(request, "Category name is required.")                        
        
        except Exception as e:
            logger.error(f"Error in updating product category: {e}")
            messages.error("Server Error.")

        return redirect(self.redirect_url)    
    

class ListProductCategoryView(BaseProductCategoryView, ListView):
    queryset = ProductCategory.objects.all().order_by("name")
    template_name = "customer_product/category/list.html"    
    context_object_name = "categories"


class DeleteProductCategoryView(BaseProductCategoryView, View):
    success_url = redirect_url = reverse_lazy("customer:product_categories")

    def get_object(self):
        try:
            return get_object_or_404(ProductCategory, slug = self.kwargs.get("slug"))
        except Http404:
            messages.error(self.request, "Failed! Invalid category object.")
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Removed category.")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception(f"Error in deleting category object: {e}")
            messages.error(request, "Failed! Server Error.")
            return redirect(self.redirect_url)
        

class BaseProductSubCategoryView(CustomerBaseView, View):
    model = ProductSubCategory
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_sub_category_page"] = True
        return context
    

class AddProductSubCategoryView(BaseProductSubCategoryView, CreateView):
    fields = ["name", "category"]
    success_url = redirect_url = reverse_lazy("customer:product_sub_categories")

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            categorySlug = request.POST.get("category")

            if not categorySlug or not name:
                error_msg = "Name of sub category is required."
                if not categorySlug:
                    error_msg = "Category is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.redirect_url)
            
            category = get_object_or_404(ProductCategory, slug = categorySlug)
            
            sub_category, created = self.model.objects.get_or_create(name = name, category = category)

            if created:
                messages.success(request, "Success! Product sub category created.")
                return redirect(self.success_url)

            else:
                messages.warning(request, "Sub Category already exists.")

        except Http404:
            messages.error(request, "Invalid category")                                                
        
        except Exception as e:
            logger.error(f"Error in creating product sub category: {e}")
            messages.error("Server Error.")

        return redirect(self.redirect_url)
    

class UpdateProductSubCategoryView(BaseProductSubCategoryView, UpdateView):
    fields = ["name", "category"]
    success_url = redirect_url = reverse_lazy("customer:product_sub_categories")

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            categorySlug = request.POST.get("category")

            if not categorySlug or not name:
                error_msg = "Name of sub category is required."
                if not categorySlug:
                    error_msg = "Category is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.redirect_url)
            
            category = get_object_or_404(ProductCategory, slug = categorySlug)                        

            if not self.model.objects.filter(name = name, category = category).exists():
                self.object = self.get_object()

                self.object.name = name
                self.object.category = category
                self.object.save()

                messages.success(request, "Success! Product sub category updated.")
                return redirect(self.success_url)

            else:
                messages.warning(request, "Sub category already exists.")

        except Http404:
            messages.error(request, "Invalid category")                      
        
        except Exception as e:
            logger.error(f"Error in updating product sub category: {e}")
            messages.error("Server Error.")

        return redirect(self.redirect_url)
    

class ListProductSubCategoryView(BaseProductSubCategoryView, ListView):
    queryset = ProductSubCategory.objects.all().order_by("name")
    template_name = "customer_product/sub_category/list.html"    
    context_object_name = "sub_categories"


class DeleteProductSubCategoryView(BaseProductSubCategoryView, View):
    success_url = redirect_url = reverse_lazy("customer:product_sub_categories")

    def get_object(self):
        try:
            return get_object_or_404(ProductSubCategory, slug = self.kwargs.get("slug"))
        except Http404:
            messages.error(self.request, "Failed! Invalid sub category object.")
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Removed sub category.")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception(f"Error in deleting sub category object: {e}")
            messages.error(request, "Failed! Server Error.")
            return redirect(self.redirect_url)

        
class BaseBrandView(CustomerBaseView, View):
    model = Brand
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_brand_page"] = True
        return context


class AddBrandView(BaseBrandView, CreateView):
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("customer:brands")

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                product, created = self.model.objects.get_or_create(name = name)

                if created:
                    messages.success(request, "Success! Product brand created.")
                    return redirect(self.success_url)

                else:
                    messages.warning(request, "Brand already exists.")

            else:
                messages.error(request, "Brand name is required.")                        
        
        except Exception as e:
            logger.error(f"Error in creating product brand: {e}")
            messages.error("Server Error.")

        return redirect(self.redirect_url)
    

class UpdateBrandView(BaseBrandView, UpdateView):
    fields = ["name", "slug"]
    success_url = redirect_url = reverse_lazy("customer:brands")
    slug_url_kwarg = "slug"

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                if not self.model.objects.filter(name = name).exists():

                    self.object = self.get_object()
                    self.object.name = name
                    self.object.save()

                    messages.success(request, "Success! Product brand updated.")
                    return redirect(self.success_url)

                else:
                    messages.warning(request, "Brand already exists.")

            else:
                messages.error(request, "Brand name is required.")                        
        
        except Exception as e:
            logger.error(f"Error in updating product brand: {e}")
            messages.error("Server Error.")

        return redirect(self.redirect_url)
    

class ListBrandView(BaseBrandView, ListView):
    queryset = Brand.objects.all().order_by("name")
    template_name = "customer_product/brand/list.html"    
    context_object_name = "brands"


class DeleteBrandView(BaseBrandView, View):
    success_url = redirect_url = reverse_lazy("customer:brands")

    def get_object(self):
        try:
            return get_object_or_404(Brand, slug = self.kwargs.get("slug"))
        except Http404:
            messages.error(self.request, "Failed! Invalid brand object.")
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Removed brand.")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception(f"Error in deleting brand object: {e}")
            messages.error(request, "Failed! Server Error.")
            return redirect(self.redirect_url)


class BaseSizeView(CustomerBaseView, View):
    model = Size
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_size_page"] = True
        return context
    

class AddSizeView(BaseSizeView, CreateView):
    fields = ["name", "category", "standard"]
    success_url = redirect_url = reverse_lazy("customer:sizes")

    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."

        try:
            created_count = 0
            ignored_count = 0

            name = request.POST.get("name")
            name = name.strip() if name else None
            if name:
                names = name.split(',')
            
            categorySlug = request.POST.get("category")
            standard = request.POST.get("standard")

            if not name or not categorySlug:
                if not name:
                    error_msg = "Failed! Name is required."

                if not categorySlug:
                    error_msg = "Failed! Category is required."

                return redirect(self.redirect_url)            

            category = get_object_or_404(ProductCategory, slug = categorySlug)
            
            for name in names:
                name = name.strip()

                if name:
                    size, created = self.model.objects.get_or_create(name = name.upper(), category = category, standard = standard)

                    if created:
                        created_count += 1

                    else:
                        ignored_count += 1


            if created_count > 0:
                success_msg = "Success! Size created."

                if ignored_count > 0:
                    success_msg = f"Success! Created {created_count} sizes. Ignored {ignored_count} sizes as they already exists in the database"
                elif created_count > 1:
                    success_msg = "Success! Created all the sizes."                                

                messages.success(request, success_msg)
                return redirect(self.success_url)
            
            else:
                messages.warning(request, "Given size/sizes already exists in the database.")

        except Http404:
            error_msg = "Failed! Invalid category"
        
        except Exception as e:
            logger.error(f"Error in creating product size: {e}")

        messages.error(request, error_msg)
        return redirect(self.redirect_url)
    

class UpdateSizeView(BaseSizeView, UpdateView):
    fields = ["name", "category", "standard", "slug"]
    success_url = redirect_url = reverse_lazy("customer:sizes")
    slug_url_kwarg = "slug"

    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."

        try:
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            categorySlug = request.POST.get("category")
            standard = request.POST.get("standard")

            if not name or not categorySlug:
                if not name:
                    error_msg = "Failed! Name is required."

                if not categorySlug:
                    error_msg = "Failed! Category is required."

                return redirect(self.redirect_url)            

            category = get_object_or_404(ProductCategory, slug = categorySlug)
            
            self.object = self.get_object()

            if not self.model.objects.filter(name = name, category = category, standard = standard).exists():
                self.object.name = name
                self.object.category = category
                self.slug = None
                self.object.standard = standard if standard else None
                self.object.save()

                messages.success(request, "Success! Size Updated.")
                return redirect(self.success_url)

            else:
                messages.warning(request, "Failed! Size already exists.")        

        except Http404:
            error_msg = "Failed! Invalid category"
        
        except Exception as e:
            logger.error(f"Error in updating product size: {e}")

        messages.error(request, error_msg)
        return redirect(self.redirect_url)
    

class ListSizeView(BaseSizeView, ListView):
    queryset = Size.objects.all().order_by("name")
    template_name = "customer_product/size/list.html"    
    context_object_name = "sizes"


class DeleteSizeView(BaseSizeView, View):
    success_url = redirect_url = reverse_lazy("customer:sizes")

    def get_object(self):
        try:
            return get_object_or_404(Size, slug = self.kwargs.get("slug"))
        except Http404:
            messages.error(self.request, "Failed! Invalid size object.")
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Removed size.")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception(f"Error in deleting size object: {e}")
            messages.error(request, "Failed! Server Error.")
            return redirect(self.redirect_url)


class BaseColorView(CustomerBaseView, View):
    model = Color
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_color_page"] = True
        return context
    

class AddColorView(BaseColorView, CreateView):
    fields = ["name", "hexa"]
    success_url = redirect_url = reverse_lazy("customer:colors")

    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."

        try:            
            name = request.POST.get("name")
            name = name.strip() if name else None

            hexa = request.POST.get("hexa")
            hexa = hexa.strip() if hexa else None

            if not name or not hexa:
                if not name:
                    error_msg = "Failed! Name is required."

                if not hexa:
                    error_msg = "Failed! Hexa is required."

                return redirect(self.redirect_url)            
            
            color, created = self.model.objects.get_or_create(name = name, hexa = hexa)


            if created:
                messages.success(request, "Success! Color created.")
                return redirect(self.success_url)            
            else:
                messages.warning(request, "Failed! Color already exists.")
                return redirect(self.redirect_url)       
        
        except Exception as e:
            logger.error(f"Error in creating product color: {e}")

        messages.error(request, error_msg)
        return redirect(self.redirect_url)


class UpdateColorView(BaseColorView, UpdateView):
    fields = ["name", "hexa"]
    success_url = redirect_url = reverse_lazy("customer:colors")
    slug_url_kwarg = "slug"


    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."

        try:            
            name = request.POST.get("name")
            name = name.strip() if name else None

            hexa = request.POST.get("hexa")
            hexa = hexa.strip() if hexa else None

            if not name or not hexa:
                if not name:
                    error_msg = "Failed! Name is required."

                if not hexa:
                    error_msg = "Failed! Hexa is required."

            if not self.model.objects.filter(name = name, hexa = hexa).exists():

                self.object = self.get_object()
                
                self.object.name = name
                self.object.hexa = hexa
                self.object.slug = None
                self.object.save()

                messages.success(request, "Success! Color updated.")
                return redirect(self.success_url)
                                    
            else:
                messages.warning(request, "Failed! Color already exists.")

        except Exception as e:
            logger.error(f"Error in updating product color: {e}")

        messages.error(request, error_msg)
        return redirect(self.redirect_url)
    

class ListColorView(BaseColorView, ListView):
    queryset = Color.objects.all().order_by("name")
    template_name = "customer_product/color/list.html"    
    context_object_name = "colors"


class DeleteColorView(BaseColorView, View):
    success_url = redirect_url = reverse_lazy("customer:colors")

    def get_object(self):
        try:
            return get_object_or_404(Color, slug = self.kwargs.get("slug"))
        except Http404:
            messages.error(self.request, "Failed! Invalid color object.")
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Removed color.")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception(f"Error in deleting color object: {e}")
            messages.error(request, "Failed! Server Error.")
            return redirect(self.redirect_url)


class BaseProductView(CustomerBaseView, View):
    model = Product
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_page"] = True        
        return context
    

class AddProductView(BaseProductView, CreateView):
    fields = "__all__"
    success_url = redirect_url = reverse_lazy("customer:add_product")
    template_name = "customer_product/product/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["sizes"] = Size.objects.all()
            context["colors"] = Color.objects.all()
            context["units"] = sorted(["mm", "cm", "m"])
        except Exception as e:
            logger.warning(f"Error in loading context data of add product view: {e}")
        return context
    
    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."
        try:
            name = request.POST.get("name").strip() if request.POST.get("name") else None
            categorySlug = request.POST.get("category")
            brandSlug = request.POST.get("brand")
            image = request.FILES.get("image")
            sku = request.POST.get("sku").strip() if request.POST.get("sku") else None
            stock = request.POST.get("stock").strip() if request.POST.get("stock") else None
            price = request.POST.get("price").strip() if request.POST.get("price") else None
            description = request.POST.get("description").strip() if request.POST.get("description") else None
            size = request.POST.getlist("size")
            color = request.POST.getlist("color")
            length = request.POST.get("length")
            width = request.POST.get("width").strip() if request.POST.get("width") else None
            height = request.POST.get("height").strip() if request.POST.get("height") else None
            weight = request.POST.get("weight").strip() if request.POST.get("weight") else None
            unit = request.POST.get("unit").strip() if request.POST.get("unit") else None

            required_fields = {
                "Name": name,
                "Product Category": categorySlug,
                "Brand": brandSlug,
                "Product Image": image,
                "Stock": stock,
                "Price": price                
            }

            if length or width or height:                
                required_fields["unit"] = unit

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed. {field_name.title()} is required.")
                    return redirect(self.redirect_url)
                
            try:
                stock = int(stock)
                if stock <= 0:
                    raise ValueError("Stock must be a positive value.")
            except (TypeError, ValueError):
                messages.error(request, "Enter a valid stock number.")
                return redirect(self.redirect_url)
                            
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError("Price must be a positive value.")
            except (TypeError, ValueError):
                messages.error(request, "Enter a valid price.")
                return redirect(self.redirect_url)
            
            if length:
                try:
                    length = float(length)
                    if length <= 0:
                        raise ValueError("Length must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid length.")
                    return redirect(self.redirect_url)
                
            if width:
                try:
                    width = float(width)
                    if width <= 0:
                        raise ValueError("Width must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid width.")
                    return redirect(self.redirect_url)
                
            if height:
                try:
                    height = float(height)
                    if height <= 0:
                        raise ValueError("Height must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid height.")
                    return redirect(self.redirect_url)                            
                
            category = get_object_or_404(ProductCategory, slug = categorySlug)
            brand = get_object_or_404(Brand, slug = brandSlug)

            product, created = self.model.objects.get_or_create(
                name = name, category = category, brand = brand, image = image,
                sku = sku, stock = stock, price = price,
                description = description, length = length if length else 0, width = width if width else 0,
                height = height if height else 0, weight = weight if weight else 0, unit = unit if unit else None
                )
            
            if created:
                if size and len(size) > 0:
                    size_list = []
                    for sizeSlug in size:
                        try:
                            size_obj = get_object_or_404(Size, slug = sizeSlug)
                            size_list.append(size_obj.pk)
                        except Http404:
                            logger.error(f"Size object not found for slug: {sizeSlug}")
                            continue

                    product.sizes.set(size_list)

                if color and len(color) > 0:
                    color_list = []
                    for colorSlug in color:
                        try:
                            color_obj = get_object_or_404(Color, slug = colorSlug)
                            color_list.append(color_obj.pk)
                        except Http404:
                            logger.error(f"Color object not found for slug: {sizeSlug}")
                            continue

                    product.colors.set(color_list)

                product.save()
            else:
                messages.warning(request, "Failed! Product already exists.")
                return redirect(self.redirect_url)

            messages.success(request, "Success! Product created.")
            return redirect(self.success_url)

        except Http404:
            error_msg = "Failed. Invalid Category."

        except Exception as e:
            logger.exception(f"Error in adding product: {e}")            

        messages.error(request, error_msg)
        return redirect(self.redirect_url)
    

class UpdateProductView(BaseProductView, UpdateView):
    fields = "__all__"
    success_url = redirect_url = reverse_lazy("customer:products")
    template_name = "customer_product/product/update.html"
    slug_url_kwarg = "slug"

    def get_redirect_url(self):
        try:
            return redirect(reverse_lazy("customer:update_product", kwargs = {"slug" : self.kwargs.get("slug")}))
        except Exception as e:
            logger.exception(f"Error in fetching the redirect url of update product view: {e}.")
            messages.error(self.request, "Failed! Server Error.")
            return self.redirect_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            self.object = self.get_object()

            context["sizes"] = Size.objects.filter(category = self.object.category)
            context["colors"] = Color.objects.all()
            context["units"] = sorted(["mm", "cm", "m"])
        except Exception as e:
            logger.warning(f"Error in loading context data of update product view: {e}")
        return context
    
    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."
        try:
            name = request.POST.get("name").strip() if request.POST.get("name") else None
            categorySlug = request.POST.get("category")
            brandSlug = request.POST.get("brand")
            image = request.FILES.get("image")
            sku = request.POST.get("sku").strip() if request.POST.get("sku") else None
            stock = request.POST.get("stock").strip() if request.POST.get("stock") else None
            price = request.POST.get("price").strip() if request.POST.get("price") else None
            description = request.POST.get("description").strip() if request.POST.get("description") else None
            size = request.POST.getlist("size")
            color = request.POST.getlist("color")
            length = request.POST.get("length")
            width = request.POST.get("width").strip() if request.POST.get("width") else None
            height = request.POST.get("height").strip() if request.POST.get("height") else None
            weight = request.POST.get("weight").strip() if request.POST.get("weight") else None
            unit = request.POST.get("unit").strip() if request.POST.get("unit") else None

            required_fields = {
                "Name": name,
                "Product Category": categorySlug,
                "Brand": brandSlug,
                "Stock": stock,
                "Price": price                
            }

            if length or width or height:                
                required_fields["unit"] = unit

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"Failed. {field_name.title()} is required.")
                    return redirect(self.redirect_url)
                
            try:
                stock = int(stock)
                if stock <= 0:
                    raise ValueError("Stock must be a positive value.")
            except (TypeError, ValueError):
                messages.error(request, "Enter a valid stock number.")
                return redirect(self.redirect_url)
                            
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError("Price must be a positive value.")
            except (TypeError, ValueError):
                messages.error(request, "Enter a valid price.")
                return redirect(self.redirect_url)
            
            if length:
                try:
                    length = float(length)
                    if length <= 0:
                        raise ValueError("Length must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid length.")
                    return redirect(self.redirect_url)
                
            if width:
                try:
                    width = float(width)
                    if width <= 0:
                        raise ValueError("Width must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid width.")
                    return redirect(self.redirect_url)
                
            if height:
                try:
                    height = float(height)
                    if height <= 0:
                        raise ValueError("Height must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid height.")
                    return redirect(self.redirect_url)                            
                
            category = get_object_or_404(ProductCategory, slug = categorySlug)
            brand = get_object_or_404(Brand, slug = brandSlug)

            self.object = self.get_object()
            if not image:
                image = self.object.image

            length = length if length else 0.00
            width = width if width else 0.00
            height = height if height else 0.00
            weight = weight if weight else None
            self.object.unit = unit if unit else None

            if not self.model.objects.filter(
                name = name, category = category, brand = brand, image = image,
                sku = sku, stock = stock, price = price,
                description = description, length = length, width = width,
                height = height, weight = weight, unit = unit
                ).exists():                                                                                                                                                                                                                

                self.object.name = name
                self.object.category = category
                self.object.brand = brand
                self.object.image = image
                self.object.sku = sku
                self.object.stock = stock
                self.object.price = price
                self.object.description = description
                self.object.length = length
                self.object.width = width
                self.object.height = height
                self.object.weight = weight
                self.object.unit = unit
                self.object.save()

                if size and len(size) > 0:
                    size_list = []
                    for sizeSlug in size:
                        try:
                            size_obj = get_object_or_404(Size, slug = sizeSlug)
                            size_list.append(size_obj.pk)
                        except Http404:
                            logger.error(f"Size object not found for slug: {sizeSlug}")
                            continue

                    self.object.sizes.set(size_list)

                if color and len(color) > 0:
                    color_list = []
                    for colorSlug in color:
                        try:
                            color_obj = get_object_or_404(Color, slug = colorSlug)
                            color_list.append(color_obj.pk)
                        except Http404:
                            logger.error(f"Color object not found for slug: {sizeSlug}")
                            continue

                    self.object.colors.set(color_list)

                self.object.save()
            else:
                messages.warning(request, "Failed! Product already exists.")
                return redirect(self.redirect_url)

            messages.success(request, "Success! Product updated.")
            return redirect(self.success_url)

        except Http404:
            error_msg = "Failed. Invalid Category."

        except Exception as e:
            logger.exception(f"Error in updating product: {e}")            

        messages.error(request, error_msg)
        return redirect(self.redirect_url)
    

class ListProductView(BaseProductView, ListView):
    queryset = Product.objects.all().order_by("name")
    template_name = "customer_product/product/list.html"    
    context_object_name = "products"


class DeleteProductView(BaseProductView, View):
    success_url = redirect_url = reverse_lazy("customer:products")

    def get_object(self):
        try:
            return get_object_or_404(Product, slug = self.kwargs.get("slug"))
        except Http404:
            messages.error(self.request, "Failed! Invalid product object.")
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Removed product.")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception(f"Error in deleting product object: {e}")
            messages.error(request, "Failed! Server Error.")
            return redirect(self.redirect_url)
        

class CategoryFilteredSizesView(BaseProductView, ListView):
    model = Size
    queryset = Size.objects.all()

    def get(self, request, *args, **kwargs):
        data = {}
        try:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                categorySlug = request.GET.get("category")
                category = get_object_or_404(ProductCategory, slug = categorySlug)

                filtered_query = self.queryset.filter(category = category)

                list_sizes = []
                for size in filtered_query:
                    list_sizes.append({
                        "name": size.name,
                        "standard": size.standard if size.standard else None,
                        "slug": size.slug
                    })

                data["sizes"] = list_sizes

        except Http404:
            data["error"] = "Invalid Category"

        except Exception as e:
            data["error"] = "Failed! Server Error"

        return JsonResponse(data)

                