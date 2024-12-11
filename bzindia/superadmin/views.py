from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, View, CreateView, ListView, UpdateView, DetailView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
import logging

from company.models import Company, CompanyType
from django.contrib.auth.models import User

from .tasks import send_company_created_email

from product.models import Product, Category, SubCategory, Color, Size, Brand
from education.models import Course, CourseProgram
from directory.models import PostOffice, PoliceStation, Bank, Court

logger = logging.getLogger(__name__)

@method_decorator(never_cache, name="dispatch")
class AdminBaseView(LoginRequiredMixin, View):
    login_url = reverse_lazy("authentication:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            companies = Company.objects.all()
            context["product_companies"] = companies.filter(type__name = "product").values("slug", "name").order_by("name")
            context["education_companies"] = companies.filter(type__name = "education").values("slug", "name").order_by("name")
            context["company_types"] = CompanyType.objects.all()
        except Exception as e:
            logger.exception(f"Error in fetching context data of admin base view: {e}")
        return context
    

class HomeView(AdminBaseView, TemplateView):
    template_name = 'admin/home.html'


# Company

class BaseCompanyView(AdminBaseView):
    model = Company

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['company_page'] = True            
        except Exception as e:
            logger.exception(f"Error in fetching context data of admin base company view: {e}")
        return context
    

class CompanyListView(BaseCompanyView, ListView):
    queryset = Company.objects.all().order_by("name")
    context_object_name = "companies"
    template_name = "admin_company/company/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['company_list_page'] = True
        except Exception as e:
            logger.exception(f"Error in fetching context data of admin company list view: {e}")
        return context
    

class FitleredCompanyListView(CompanyListView, ListView):
    def get_queryset(self):
        try:
            return Company.objects.filter(type__slug = self.kwargs.get("slug"))        
        except Exception as e:
            logger.exception(f"Error in fetching queryset in filtered company list view: {e}")

        return self.queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company_type"] = get_object_or_404(CompanyType, slug = self.kwargs.get("slug"))
        return context        
    

class CompanyDetailView(BaseCompanyView, DetailView):
    template_name = "admin_company/company/detail.html"
    context_object_name = "company"
    

class AddCompanyView(BaseCompanyView, CreateView):
    success_url = redirect_url = reverse_lazy('superadmin:add_company')
    fields = ["name", "type", "slug", "favicon", "logo", "phone1", "phone2", "whatsapp", "email"]
    template_name = "admin_company/company/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            pass
        except Exception as e:
            logger.exception(f"Error in fetching context data of admin add company view: {e}")
        return context

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            type = request.POST.get("type")
            slug = request.POST.get("slug")
            favicon = request.FILES.get('favicon')
            logo = request.FILES.get('logo')
            phone1 = request.POST.get("phone1")
            phone2 = request.POST.get("phone2")
            whatsapp = request.POST.get("whatsapp")
            email = request.POST.get("email")

            type = CompanyType.objects.get(slug = type)

            company_obj = self.model.objects.create(
                name = name, type=type, slug=slug,
                favicon=favicon, logo=logo, phone1=phone1,
                phone2=phone2, whatsapp=whatsapp, email=email
                )
            
            User.objects.create_user(
                username = company_obj.email,
                email = company_obj.email,
                password = company_obj.phone1
            )

            company = {
                "name": company_obj.name,
                "phone1": company_obj.phone1,
                "email": company_obj.email
            }

            # send_company_created_email.delay(company)

            messages.success(self.request, "Added Company")

            return redirect(self.success_url)
        
        except Exception as e:
            logger.exception(f"Error in adding company: {e}")
            return redirect(self.redirect_url)
    
    def from_invalid(self, form):
        reponse = super().form_invalid(form)
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error in field: {field}: {error}")
        messages.error(self.request, "Error in adding company")
        return reponse
    
class UpdateCompanyView(BaseCompanyView, UpdateView):
    fields = ["name", "type", "slug", "favicon", "logo", "phone1", "phone2", "whatsapp", "email"]
    template_name = "admin_company/company/update.html"
    success_url = redirect_url = reverse_lazy('superadmin:companies')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            pass
        except Exception as e:
            logger.exception(f"Error in fetching context data of admin update company view: {e}")
        return context

    def get_success_url(self):
        try:
            slug = self.request.POST.get('slug')
            if slug:
                return reverse_lazy('superadmin:update_company',  kwargs = {'slug' : slug})    
            return reverse_lazy('superadmin:update_company',  kwargs = {'slug' : self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in getting success url of update company view: {e}")
            return self.success_url

    def get_redirect_url(self):
        try:
            self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of update company view: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            type = request.POST.get("type")
            slug = request.POST.get("slug")
            favicon = request.FILES.get('favicon')
            logo = request.FILES.get('logo')
            phone1 = request.POST.get("phone1")
            phone2 = request.POST.get("phone2")
            whatsapp = request.POST.get("whatsapp")
            email = request.POST.get("email")

            type = CompanyType.objects.get(slug = type)

            self.object = self.get_object()

            self.object.name = name.strip()
            self.object.type = type
            self.object.slug = slug.strip()
            self.object.favicon = favicon if favicon else self.object.favicon
            self.object.logo = logo if logo else self.object.logo
            self.object.phone1 = phone1.strip()
            self.object.phone2 = phone2.strip()
            self.object.whatsapp = whatsapp.strip()
            self.object.email = email.strip()

            self.object.save()

            messages.success(request, "Company Updation Successfull.")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in updating company: {e}")
            return redirect(self.get_redirect_url())


class DeleteCompanyView(BaseCompanyView, View):
    success_url = redirect_url = reverse_lazy("superadmin:companies")

    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting company object: {e}")
            
        return None

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            print(self.object)
            self.object.delete()
            messages.success(request, "Company Deletion Successfull.")
            return redirect(self.success_url)
        except Exception as e:
            logger.exception(f"Error in deleting company: {e}")
            return redirect(self.redirect_url)
        

class CompanyTypeListView(BaseCompanyView, ListView):
    queryset = CompanyType.objects.all().order_by("name")
    context_object_name = "types"
    template_name = "admin_company/types/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['company_type_page'] = True
        except Exception as e:
            logger.exception(f"Error in fetching context data of company list view: {e}")
        return context
        

class AddCompanyTypeView(BaseCompanyView, CreateView):
    model = CompanyType
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("superadmin:company_types")

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                company_type, created = self.model.objects.get_or_create(name = name)

                if created:
                    messages.success(request, "Success! Company type created.")
                    return redirect(self.success_url)

                else:
                    messages.warning(request, "Company type already exists.")

            else:
                messages.error(request, "Name is required.")                        
        
        except Exception as e:
            logger.error(f"Error in creating company type: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.redirect_url)
    

class UpdateCompanyTypeView(BaseCompanyView, View):
    model = CompanyType
    fields = ["name", "slug"]    
    success_url = redirect_url = reverse_lazy('superadmin:company_types')
        
    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get("slug"))
        except Exception as e:
            logger.exception(f"Error in fetching the object in update company view: {e}")
        
        return None

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")                        

            self.object = self.get_object()

            if self.object:
                self.object.name = name.strip()
                self.object.slug = None

                self.object.save()

                messages.success(request, "Company Type Updation Successfull.")
                return redirect(self.success_url)

        except Exception as e:
            logger.exception(f"Error in updating company type: {e}")
            return redirect(self.redirect_url())
    

class DeleteCompanyTypeView(BaseCompanyView, View):
    model = CompanyType
    success_url = redirect_url = reverse_lazy("superadmin:company_types")

    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Company Type")
        except Exception as e:
            logger.exception(f"Error in getting company type object: {e}")
            
        return redirect(self.redirect_url)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Company Type Deletion Successfull.")
            return redirect(self.success_url)
        except Exception as e:
            logger.exception(f"Error in deleting company type: {e}")
            return redirect(self.redirect_url)


# Product Company
class BaseProductCompanyView(AdminBaseView, View):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:            
            context["product_company_page"] = True
            context["product_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
        except Http404:
            logger.error(f"Invalid product company in context of base product company view of superadmin.")
        except Exception as e:
            logger.exception(f"Error in fetching context data of base product company view of super admin: {e}")
        return context

class ListProductView(BaseProductCompanyView, ListView):
    model = Product
    queryset = model.objects.none()
    context_object_name = "products"
    template_name = "product_company/products/list.html"
    
    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of list product view of superadmin side: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:            
            context["products_page"] = True        
        except Exception as e:
            logger.exception(f"Error in fetching context data of list product view of super admin: {e}")
        return context
    

class AddProductView(BaseProductCompanyView, CreateView):
    model = Product
    fields = "__all__"
    success_url = redirect_url = reverse_lazy("superadmin:add_product")
    template_name = "product_company/products/add.html"

    def get_success_url(self):        
        return reverse_lazy("superadmin:add_product", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["sizes"] = Size.objects.all()
            context["colors"] = Color.objects.all()
            context["units"] = sorted(["mm", "cm", "m"])
            product_company = context["product_company"]

            context["categories"] = Category.objects.filter(company = product_company).values("slug", "name").order_by("name")
            context["sub_categories"] = SubCategory.objects.filter(company = product_company).values("slug", "name").order_by("name")
            context["colors"] = Color.objects.filter(company = product_company).values("slug", "name", "hexa").order_by("name")
            context["sizes"] = Size.objects.filter(company = product_company).values("slug", "name").order_by("name")
            context["brands"] = Brand.objects.filter(company = product_company).values("slug", "name").order_by("name")

        except Exception as e:
            logger.warning(f"Error in loading context data of add product view: {e}")
        return context
    
    def post(self, request, *args, **kwargs):
        error_msg = "Failed! Server Error."
        try:
            product_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name").strip() if request.POST.get("name") else None
            category_slug = request.POST.get("category")
            sub_category_slug = request.POST.get("sub_category")
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
                "Product Category": category_slug,
                "Product Sub Category": sub_category_slug,
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
                    return redirect(self.get_redirect_url())
                
            try:
                stock = int(stock)
                if stock <= 0:
                    raise ValueError("Stock must be a positive value.")
            except (TypeError, ValueError):
                messages.error(request, "Enter a valid stock number.")
                return redirect(self.get_redirect_url())
                            
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError("Price must be a positive value.")
            except (TypeError, ValueError):
                messages.error(request, "Enter a valid price.")
                return redirect(self.get_redirect_url())
            
            if length:
                try:
                    length = float(length)
                    if length <= 0:
                        raise ValueError("Length must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid length.")
                    return redirect(self.get_redirect_url())
                
            if width:
                try:
                    width = float(width)
                    if width <= 0:
                        raise ValueError("Width must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid width.")
                    return redirect(self.get_redirect_url())
                
            if height:
                try:
                    height = float(height)
                    if height <= 0:
                        raise ValueError("Height must be a positive value.")
                except (TypeError, ValueError):
                    messages.error(request, "Enter a valid height.")
                    return redirect(self.get_redirect_url())                            
                
            category = get_object_or_404(Category, slug = category_slug)
            sub_category = get_object_or_404(SubCategory, slug = sub_category_slug)
            brand = get_object_or_404(Brand, slug = brandSlug)

            product, created = self.model.objects.get_or_create(
                company = product_company,
                name = name, category = category, sub_category = sub_category, 
                brand = brand, image = image, sku = sku, stock = stock, price = price,
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
                return redirect(self.get_redirect_url())

            messages.success(request, "Success! Product created.")
            return redirect(self.get_success_url())

        except Http404:
            error_msg = "Failed. Invalid Category."
            if category:
                error_msg = "Failed! Invalid sub category"

        except Exception as e:
            logger.exception(f"Error in adding product: {e}")            

        messages.error(request, error_msg)
        return redirect(self.get_redirect_url())
    

class ListBrandView(BaseProductCompanyView, ListView):
    model = Brand
    queryset = model.objects.none()
    context_object_name = "brands"
    template_name = "product_company/brands/list.html"
    
    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of list brand view of superadmin side: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:                        
            context["brands_page"] = True        
        except Exception as e:
            logger.exception(f"Error in fetching context data of list brand view of superadmin: {e}")
        return context
    

class AddBrandView(BaseProductCompanyView, CreateView):
    model = Brand
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("superadmin:brands")

    def get_success_url(self):        
        return reverse_lazy("superadmin:brands", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()

    def post(self, request, *args, **kwargs):
        try:
            product_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                product, created = self.model.objects.get_or_create(company = product_company, name = name)

                if created:
                    messages.success(request, "Success! Product brand created.")
                    return redirect(self.get_success_url())

                else:
                    messages.warning(request, "Brand already exists.")

            else:
                messages.error(request, "Brand name is required.")                        
        
        except Exception as e:
            logger.error(f"Error in creating product brand: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.get_redirect_url())
    

class ListProductCategoryView(BaseProductCompanyView, ListView):
    model = Category
    queryset = model.objects.none()
    template_name = "product_company/category/list.html"    
    context_object_name = "categories"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of list category view of superadmin side: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:            
            context["categories_page"] = True        
        except Exception as e:
            logger.exception(f"Error in fetching context data of list category view of superadmin: {e}")
        return context

class AddProductCategoryView(BaseProductCompanyView, CreateView):
    model = Category
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("superadmin:categories")

    def get_success_url(self):        
        return reverse_lazy("superadmin:categories", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def post(self, request, *args, **kwargs):
        try:
            product_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                product, created = self.model.objects.get_or_create(company = product_company, name = name)

                if created:
                    messages.success(request, "Success! Product category created.")
                    return redirect(self.get_success_url())

                else:
                    messages.warning(request, "Category already exists.")
            
            else:
                messages.error(request, "Category name is required.")                        
        
        except Exception as e:
            logger.error(f"Error in creating product category: {e}")
            messages.error("Server Error.")

        return redirect(self.get_redirect_url())
    

class ListProductSubCategoryView(BaseProductCompanyView, ListView):
    model = SubCategory
    queryset = SubCategory.objects.none()
    template_name = "product_company/sub_category/list.html"    
    context_object_name = "sub_categories"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of list product sub category view of superadmin side: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:            
            context["sub_categories_page"] = True
            product_company = context["product_company"]
            context["categories"] = Category.objects.filter(company = product_company)
        except Exception as e:
            logger.exception(f"Error in fetching context data of list sub category view of superadmin: {e}")
        return context


class AddProductSubCategoryView(BaseProductCompanyView, CreateView):
    model = SubCategory
    fields = ["name", "category"]
    success_url = redirect_url = reverse_lazy("superadmin:sub_categories")

    def get_success_url(self):        
        return reverse_lazy("superadmin:sub_categories", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url() 

    def post(self, request, *args, **kwargs):
        try:
            product_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name")
            name = name.strip() if name else None

            category_slug = request.POST.get("category")

            if not category_slug or not name:
                error_msg = "Name of sub category is required."
                if not category_slug:
                    error_msg = "Category is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.get_redirect_url())
            
            category = get_object_or_404(Category, slug = category_slug)
            
            sub_category, created = self.model.objects.get_or_create(company = product_company, name = name, category = category)

            if created:
                messages.success(request, "Success! Product sub category created.")
                return redirect(self.get_success_url())

            else:
                messages.warning(request, "Sub Category already exists.")

        except Http404:
            messages.error(request, "Invalid category")                                                
        
        except Exception as e:
            logger.error(f"Error in creating product sub category by superadmin: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.get_redirect_url())
    

class ListProductColorView(BaseProductCompanyView, ListView):
    model = Color
    queryset = model.objects.none()
    template_name = "product_company/colors/list.html"    
    context_object_name = "colors"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of list product colors view of superadmin side: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:            
            context["colors_page"] = True            
        except Exception as e:
            logger.exception(f"Error in fetching context data of list colors view of superadmin: {e}")
        return context
    

class AddProductColorView(BaseProductCompanyView, CreateView):
    model = Color
    fields = ["name", "hexa"]
    success_url = redirect_url = reverse_lazy("superadmin:colors")

    def get_success_url(self):        
        return reverse_lazy("superadmin:colors", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url() 

    def post(self, request, *args, **kwargs):
        try:
            product_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            
            name = request.POST.get("name")
            name = name.strip() if name else None

            hexa = request.POST.get("hexa")
            hexa = hexa.strip() if hexa else None

            if not name or not hexa:
                if not name:
                    error_msg = "Failed! Name is required."

                if not hexa:
                    error_msg = "Failed! Hexa is required."

                messages.error(request, error_msg)                
                return redirect(self.get_redirect_url())
            
            color, created = self.model.objects.get_or_create(company = product_company, name = name, hexa = hexa)

            if created:
                messages.success(request, "Success! Product color created.")
                return redirect(self.get_success_url())

            else:
                messages.warning(request, "Color already exists.")                                               
        
        except Exception as e:
            logger.error(f"Error in creating product color by superadmin: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.get_redirect_url())
    

# Education Company
class BaseEducationCompanyView(AdminBaseView, View):
    model = Course
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:                        
            context["education_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
        except Http404:
            logger.error(f"Invalid education company in context of base education company view of superadmin.")
        except Exception as e:
            logger.exception(f"Error in fetching context data of base education company view of super admin: {e}")
        return context
    

class AddCourseView(BaseEducationCompanyView, CreateView): 
    fields = ["name", "program", "specialization", "image", "mode", "duration", "price", "duration"]   
    template_name = "education_company/courses/add.html"
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_page"] = True
            context["add_course_page"] = True
        except Exception as e:
            logger.exception(f"Error in fetching context data of add course view of super admin: {e}")
        return context

    
    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:courses", kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of add course view: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of add course view: {e}")

        return self.redirect_url
    
    def post(self, request, *args, **kwargs):        
        try:
            company = get_object_or_404(Company, slug = self.kwargs.get('slug'))

            name = request.POST.get("name")
            program = request.POST.get("program")
            specialization = request.POST.get("specialization")
            image = request.FILES.get("image")
            mode = request.POST.get("mode")
            duration = request.POST.get("duration")
            price = request.POST.get("price")

            course, created = self.model.objects.get_or_create(
                name=name, program=program, specialization=specialization,
                image=image, mode=mode, duration=duration, price=price
                )
            
            if created:
                messages.success(request, "Success! Course created.")
                return redirect(self.get_success_url())
            
            messages.error(request, "Failed! Course already exists")

        except Http404:
            messages.error(request, "Invalid Company")            

        except Exception as e:
            messages.error(request, "Failed! Server Error.")
            logger.exception(f"Error in adding course in add course view: {e}")

        return redirect(self.get_redirect_url())


class CourseListView(BaseEducationCompanyView, ListView):
    queryset = Course.objects.none()
    context_object_name = "courses"
    template_name = "education_company/courses/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get("slug"))
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of course list view of admin section")
        
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_page"] = True
            context['course_list_page'] = True
        except Exception as e:
            logger.exception(f"Error in fetching context data of admin course list view: {e}")
        return context
    

class CourseProgramListView(BaseEducationCompanyView, ListView):
    model = CourseProgram
    queryset = model.objects.none()
    context_object_name = "courses"
    template_name = "education_company/programs/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get("slug"))
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of course program list view of admin section")
        
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["program_page"] = True
            context['program_list_page'] = True
        except Exception as e:
            logger.exception(f"Error in fetching context data of admin course program list view: {e}")
        return context
    

# Directory

class ListPostOfficeView(ListView):
    model = PostOffice
    queryset = model.objects.all()
    context_object_name = "post_offices"
    template_name = "directory/post_office/list.html"
    paginate_by = 10


class ListBankView(ListView):
    model = Bank
    queryset = model.objects.all()
    context_object_name = "banks"
    template_name = "directory/bank/list.html"
    paginate_by = 10


class ListCourtView(ListView):
    model = Court
    queryset = model.objects.all()
    context_object_name = "courts"
    template_name = "directory/court/list.html"
    paginate_by = 10
    

class ListPoliceStationView(ListView):
    model = PoliceStation
    queryset = model.objects.all()
    context_object_name = "police_stations"
    template_name = "directory/police_station/list.html"
    paginate_by = 10