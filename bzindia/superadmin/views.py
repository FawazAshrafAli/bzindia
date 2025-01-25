from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, View, CreateView, ListView, UpdateView, DetailView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, logout
from django.db import IntegrityError
from datetime import timedelta
from django.db import transaction
import logging

from custom_pages.models import (
    AboutUs, ContactUs, FAQ, PrivacyPolicy, TermsAndConditions,
    ShippingAndDeliveryPolicy, CancellationAndRefundPolicy
    )
from company.models import Company, CompanyType
from locations.models import UniqueState, UniqueDistrict, UniquePlace
from django.contrib.auth.models import User

from .tasks import send_company_created_email

from product.models import Product, Category as ProductCategory, SubCategory as ProductSubCategory, Color, Size, Brand
from educational.models import (
    Program, Course, Specialization, Enquiry as CourseEnquiry, CourseDetail, Feature as CourseFeature,
    VerticalTab as CourseVerticalTab, VerticalBullet as CourseVerticalBullet, HorizontalTab as CourseHorizontalTab,
    HorizontalBullet as CourseHorizontalBullet, TableData as CourseTableData, Table as CourseTable,
    BulletPoints as CourseBulletPoint, Tag as CourseTag, Timeline as CourseTimeline
    )
from directory.models import PostOffice, PoliceStation, Bank, Court, TouristAttraction
from service.models import Service, Category as ServiceCategory, SubCategory as ServiceSubCategory, Enquiry as ServiceEnquiry
from registration.models import RegistrationType, RegistrationSubType, RegistrationDetail

logger = logging.getLogger(__name__)

def get_state(slug):
    try:
        return get_object_or_404(UniqueState, slug = slug)
    except Http404:
        return None
    
def get_district(slug):
        try:
            return get_object_or_404(UniqueDistrict, slug = slug)
        except Http404:
            return None
        
def get_place(slug):
        try:
            return get_object_or_404(UniquePlace, slug = slug)
        except Http404:
            return None  

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
            context['company_type_page'] = True            
        except Exception as e:
            logger.exception(f"Error in fetching context data of admin base company view: {e}")
        return context
    

class CompanyView(BaseCompanyView, ListView):
    model = CompanyType
    template_name = "admin_company/company/list.html"
    context_object_name = "company_types"
    queryset = CompanyType.objects.all() 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["company_types"] = CompanyType.objects.all() 
        except Exception as e:
            logger.exception(f"Error in getting context data of company view in superadmin: {e}")
        return context


class CompanyListView(CompanyView, ListView):
    model = Company
    queryset = Company.objects.none()
    context_object_name = "companies"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['company_list_page'] = True
            try:
                context['current_company_type'] = get_object_or_404(CompanyType, slug = self.kwargs.get("slug"))
            except Http404:
                pass

        except Exception as e:
            logger.exception(f"Error in fetching context data of admin company list view: {e}")
        return context
    
    def get_queryset(self):
        try:
            return Company.objects.filter(type__slug = self.kwargs.get("slug"))        
        except Exception as e:
            logger.exception(f"Error in fetching queryset in company list view: {e}")

        return self.queryset
    

# class FitleredCompanyListView(CompanyListView, ListView):
    # def get_queryset(self):
    #     try:
    #         return Company.objects.filter(type__slug = self.kwargs.get("slug"))        
    #     except Exception as e:
    #         logger.exception(f"Error in fetching queryset in filtered company list view: {e}")

    #     return self.queryset
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["company_type"] = get_object_or_404(CompanyType, slug = self.kwargs.get("slug"))
    #     return context
    

class CompanyDetailView(BaseCompanyView, DetailView):
    template_name = "admin_company/company/detail.html"
    context_object_name = "company"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            try:
                current_company = get_object_or_404(Company, slug = self.kwargs.get("slug"))
                context["current_company"] = current_company

                if current_company.type.name == "Product":
                    products = Product.objects.filter(company = current_company)
                    context["products"] = products if products else None

                    types = ProductCategory.objects.filter(company = current_company)
                    context["types"] = types if types else None

                    sub_types = ProductSubCategory.objects.filter(company = current_company)
                    context["sub_types"] = sub_types if sub_types else None

            except Http404:
                messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of company detail view of superadmin: {e}")

        return context
    

class AddCompanyView(BaseCompanyView, CreateView):
    success_url = redirect_url = reverse_lazy('superadmin:add_company')
    fields = ["name", "type", "slug", "favicon", "logo", "phone1", "phone2", "whatsapp", "email", "description"]
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
            description = request.POST.get("description")

            type = CompanyType.objects.get(slug = type)

            company_obj = self.model.objects.create(
                name = name, type=type, slug=slug,
                favicon=favicon, logo=logo, phone1=phone1,
                phone2=phone2, whatsapp=whatsapp, email=email,
                description=description
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
            pass
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
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
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

            context["categories"] = ProductCategory.objects.filter(company = product_company).values("slug", "name").order_by("name")
            context["sub_categories"] = ProductSubCategory.objects.filter(company = product_company).values("slug", "name").order_by("name")
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
                
            category = get_object_or_404(ProductCategory, slug = category_slug)
            sub_category = get_object_or_404(ProductSubCategory, slug = sub_category_slug)
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
    model = ProductCategory
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
    model = ProductCategory
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
            messages.error(request, "Server Error.")

        return redirect(self.get_redirect_url())
    

class ListProductSubCategoryView(BaseProductCompanyView, ListView):
    model = ProductSubCategory
    queryset = model.objects.none()
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
            context["categories"] = ProductCategory.objects.filter(company = product_company)
        except Exception as e:
            logger.exception(f"Error in fetching context data of list sub category view of superadmin: {e}")
        return context


class AddProductSubCategoryView(BaseProductCompanyView, CreateView):
    model = ProductSubCategory
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
            
            category = get_object_or_404(ProductCategory, slug = category_slug)
            
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
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            context["company_page"] = True
        except Http404:
            logger.error(f"Invalid education company in context of base education company view of superadmin.")
        except Exception as e:
            logger.exception(f"Error in fetching context data of base education company view of super admin: {e}")
        return context
    

class AddCourseView(BaseEducationCompanyView, CreateView): 
    fields = ["company", "name", "program", "specialization", "mode", "duration", "price", "duration", "state", "district", "place"]   
    template_name = "education_company/courses/add.html"
    success_url = redirect_url = reverse_lazy("superadmin:home")
    
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

    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid company")
            return self.get_redirect_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)   
        
        try:
            context["course_page"] = True
            context["add_course_page"] = True
            context["states"] = UniqueState.objects.all()

            current_company = self.get_current_company()

            context["programs"] = Program.objects.filter(company = current_company)
                
        except Exception as e:
            logger.exception(f"Error in getting context data of AddCourseView in superadmin app: {e}")

        return context
    
    def post(self, request, *args, **kwargs):        
        try:
            company = self.get_current_company()

            name = request.POST.get("name")
            program_slug = request.POST.get("program")
            specialization_slug = request.POST.get("specialization")
            mode = request.POST.get("mode")
            duration = request.POST.get("duration")
            price = request.POST.get("price")
            description = request.POST.get("description")

            try:
                program = get_object_or_404(Program, slug = program_slug)
            except Http404:
                messages.error(request, "Failed! Invalid Program")
                return redirect(self.get_redirect_url())

            try:
                specialization = get_object_or_404(Specialization, slug = specialization_slug)
            except Http404:
                messages.error(request, "Failed! Invalid Specialization")
                return redirect(self.get_redirect_url())

            course, created = self.model.objects.get_or_create(
                company = company,
                name=name, program=program, specialization=specialization,
                mode=mode, duration=duration, price=price, description=description
                )
            
            if created:
                messages.success(request, "Success! Course created.")
                return redirect(self.get_success_url())
            
            messages.error(request, "Failed! Course already exists")

        except Exception as e:
            messages.error(request, "Failed! Server Error.")
            logger.exception(f"Error in adding course in add course view: {e}")

        return redirect(self.get_redirect_url())
    

class UpdateCourseView(BaseEducationCompanyView, UpdateView): 
    fields = ["name", "program", "specialization", "mode", "duration", "price", "duration"]   
    template_name = "education_company/courses/edit.html"
    success_url = redirect_url = reverse_lazy("superadmin:home")    
    
    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:courses", kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateCourseView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateCourseView of superadmin app: {e}")

        return self.redirect_url

    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid company")
            return self.get_redirect_url()

    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get("course_slug"))
        except Http404:
            messages.error(self.request, "Invalid course")
            return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)   
        
        try:
            context["course_page"] = True
            context["add_course_page"] = True
            context["modes"] = ("Online", "Offline")

            current_company = self.get_current_company()
            current_course = self.get_object()

            context["programs"] = Program.objects.filter(company = current_company)
            context["specializations"] = Specialization.objects.filter(company = current_company, program = current_course.program)
                
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateCourseView in superadmin app: {e}")

        return context
    
    def post(self, request, *args, **kwargs):        
        try:
            name = request.POST.get("name")
            program_slug = request.POST.get("program")
            specialization_slug = request.POST.get("specialization")
            mode = request.POST.get("mode")
            duration = request.POST.get("duration")
            price = request.POST.get("price")
            description = request.POST.get("description")

            try:
                program = get_object_or_404(Program, slug = program_slug)
            except Http404:
                messages.error(request, "Failed! Invalid Program")
                return redirect(self.get_redirect_url())

            try:
                specialization = get_object_or_404(Specialization, slug = specialization_slug)
            except Http404:
                messages.error(request, "Failed! Invalid Specialization")
                return redirect(self.get_redirect_url())

            required_fields = {
                "Name": name.strip(),
                "Program": program,
                "Specialization": specialization,
                "Mode": mode,
                "Price": price.strip()
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url)
                
            course = self.get_object()

            similar_courses = self.model.objects.filter(
                company = course.company, name = name, program = program,
                specialization = specialization, mode = mode
                )
            
            if similar_courses.exists() and similar_courses.first() != course:
                messages.warning(request, "Similar course already exists")
                return redirect(self.get_redirect_url())
            
            course.name = name
            course.program = program
            course.specialization = specialization
            course.mode = mode
            course.duration = duration
            course.price = price
            course.description = description
            course.save()
            
            messages.success(request, "Success! Course updated.")
            return redirect(self.get_success_url())
            
        except Exception as e:
            logger.exception(f"Error in UpdateCourseView of superadmin app: {e}")
            messages.error(request, "An expected error occured")

        return redirect(self.get_redirect_url())
    

class RemoveCourseView(BaseEducationCompanyView, View):
    model = Course
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:courses", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveCourseView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveCourseView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("course_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted course")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid course")

        except Exception as e:
            logger.exception(f"Error in RemoveCourseView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return self.get_redirect_url()


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
    model = Program
    queryset = model.objects.none()
    context_object_name = "programs"
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
            context["course_program_page"] = True
            context['program_list_page'] = True
        except Exception as e:
            logger.exception(f"Error in fetching context data of admin course program list view: {e}")
        return context
    

class AddCourseProgramView(BaseEducationCompanyView, CreateView):
    model = Program
    fields = ["company", "name"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:course_programs", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid company")
            return self.get_redirect_url()    

    def post(self, request, *args, **kwargs):
        try:
            current_company = self.get_current_company()

            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                program, created = self.model.objects.get_or_create(company = current_company, name = name)

                if created:
                    messages.success(request, "Success! Course program created.")
                    return redirect(self.get_success_url())

                else:
                    messages.warning(request, "Course program already exists.")
            
            else:
                messages.error(request, "Course program name is required.")            
        
        except Exception as e:
            logger.error(f"Error in creating course program: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.get_redirect_url())
    

class UpdateCourseProgramView(BaseEducationCompanyView, UpdateView):
    model = Program
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:course_programs", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()
        
    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get("program_slug"))
        except Http404:
            messages.error(self.request, "Invalid course program")
            return redirect(self.get_redirect_url())

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            if not name:
                messages.error(request, "Failed! Name is required")
                return redirect(self.get_redirect_url())
            
            program = self.get_object()

            similar_programs = self.model.objects.filter(company = program.company, name = name)
            
            if similar_programs.exists() and similar_programs.first() != program:
                messages.warning(request, "Similar course program already exists")
                return redirect(self.get_redirect_url())

            program.name = name
            program.save()
            messages.success(request, "Success! Course program updated.")
            return redirect(self.get_success_url())    
        
        except Exception as e:
            logger.error(f"Error in UpdateCourseProgramView of superadmin app: {e}")
            messages.error(request, "An unexpected error occured")

        return redirect(self.get_redirect_url())
    

class RemoveCourseProgramView(BaseEducationCompanyView, View):
    model = Program
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:course_programs", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveCourseProgramView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveCourseProgramView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("program_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted course program")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid course program")

        except Exception as e:
            logger.exception(f"Error in RemoveCourseProgramView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return self.get_redirect_url()
    

class CourseSpecializationListView(BaseEducationCompanyView, ListView):
    model = Specialization
    queryset = model.objects.none()
    context_object_name = "specializations"
    template_name = "education_company/specializations/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get("slug"))
        except Exception as e:
            logger.exception(f"Error in fetching the queryset of CourseSpecializationListView of admin section: {e}")
        
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_specialization_page"] = True
            context['program_list_page'] = True

            context["programs"] = Program.objects.all()
        except Exception as e:
            logger.exception(f"Error in fetching context data of CourseSpecializationListView of superadmin app: {e}")
        return context
    

class AddCourseSpecializationView(BaseEducationCompanyView, CreateView):
    model = Specialization
    fields = ["company", "name", "program"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:course_specializations", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def post(self, request, *args, **kwargs):
        try:
            current_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name")
            name = name.strip() if name else None

            program_slug = request.POST.get("program")

            if not program_slug or not name:
                error_msg = "Name of course specialization is required."
                if not program_slug:
                    error_msg = "Course program is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.get_redirect_url())
            
            program = get_object_or_404(Program, slug = program_slug)
            
            specialization, created = self.model.objects.get_or_create(company = current_company, name = name, program = program)

            if created:
                messages.success(request, "Success! Course specialization created.")
                return redirect(self.get_success_url())

            else:
                messages.warning(request, "Course specialization already exists.")

        except Http404:
            messages.error(request, "Invalid course program")                                    
        
        except Exception as e:
            logger.error(f"Error in AddCourseSpecializationView in superadmin app: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.get_redirect_url())
    

class UpdateCourseSpecializationView(BaseEducationCompanyView, UpdateView):
    model = Specialization
    fields = ["name", "program"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:course_specializations", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of UpdateCourseSpecializationView in superadmin app: {e}")
            return self.success_url
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()  
        except Exception as e:
            logger.exception(f"Error in getting redirect url of UpdateCourseSpecializationView in superadmin app: {e}")
            return self.redirect_url 

    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Company")
            return redirect(self.redirect_url)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_current_company()
            context["programs"] = Program.objects.filter(company = current_company)
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateCourseSpecializationView of superadmin app: {e}")
        
        return context
        
    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get("specialization_slug"))
        except Http404:
            messages.error(self.request, "Invalid course specialization")
            return redirect(self.get_redirect_url())

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            program_slug = request.POST.get("program")

            if not program_slug or not name:
                error_msg = "Name of course specialization is required."
                if not program_slug:
                    error_msg = "Course program is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.get_redirect_url())
            
            program = get_object_or_404(Program, slug = program_slug)

            specialization = self.get_object()
            
            similar_specialization = self.model.objects.filter(
                company = specialization.company, name = name, program = program
                )
            
            if similar_specialization.exists() and similar_specialization.first() != specialization:
                messages.warning(request, "Similar cours specialization already exists")
                return redirect(self.get_redirect_url())

            specialization.name = name
            specialization.program = program
            specialization.save()
            messages.success(request, "Success! Course specialization updated.")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid course program")                                    
        
        except Exception as e:
            logger.error(f"Error in UpdateCourseSpecializationView in superadmin app: {e}")
            messages.error(request, "An unexpected error occured")

        return redirect(self.get_redirect_url())
    

class RemoveCourseSpecializationView(BaseEducationCompanyView, View):
    model = Specialization
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:course_specializations", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveCourseSpecializationView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveCourseSpecializationView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("specialization_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted course specialization")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid course specialization")

        except Exception as e:
            logger.exception(f"Error in RemoveCourseSpecializationView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return self.get_redirect_url()
    

class ListCourseEnquiryView(BaseEducationCompanyView, ListView):
    model = CourseEnquiry
    queryset = model.objects.none()
    context_object_name = "enquiries"
    template_name = "education_company/enquiries/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListCourseEnquiryView of superadmin: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            context["education_enquiry_page"] = True

        except Http404:
            messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of ListCourseEnquiryView: {e}")

        return context


# Service Company
class BaseServiceCompanyView(AdminBaseView, View):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["company_list_page"] = True
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in getting context data of base service company view: {e}")

        return context
    

class ListServiceView(BaseServiceCompanyView, ListView):
    model = Service
    queryset = model.objects.none()
    context_object_name = "services"
    template_name = "service_company/services/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of list service view of superadmin: {e}")
            return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            context["service_page"] = True

        except Http404:
            messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of list service view: {e}")

        return context
    
class AddServiceView(BaseServiceCompanyView, CreateView):
    model = Service
    fields = ["company", "name", "category", "sub_category", "is_active", "duration", "price"]
    template_name = "service_company/services/add.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:add_service", kwargs = {'slug': self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in getting success url of add service view in superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url in add service view of superadmin: {e}")
            return self.redirect_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["categories"] = ServiceCategory.objects.all()
            context["service_page"] = True
        except Exception as e:
            logger.exception(f"Error in getting context data of add service view: {e}")

        return context

    def post(self, request, *args, **kwargs):
        try:
            company_slug = self.kwargs.get('slug')

            name = request.POST.get("name")
            category_slug = request.POST.get("category")
            sub_category_slug = request.POST.get("sub_category")

            description = request.POST.get("description")

            price = request.POST.get("price")
            duration = request.POST.get("duration")
            is_active = request.POST.get("is_active")

            required_fields = {
                "Service Name": name,
                "Category": category_slug,
                "Sub Category": sub_category_slug,                
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            company = None
            try:
                company = get_object_or_404(Company, slug = company_slug.strip())
            except Http404:
                messages.error(request, "Failed! Invalid service company")
                return redirect(self.redirect_url)

            category = None
            try:
                category = get_object_or_404(ServiceCategory, slug = category_slug.strip())
            except Http404:
                messages.error(request, "Failed! Invalid Category")
                return redirect(self.get_redirect_url())
            
            sub_category = None
            try:
                sub_category = get_object_or_404(ServiceSubCategory, slug = sub_category_slug.strip())
            except Http404:
                messages.error(request, "Failed! Invalid Sub Category")
                return redirect(self.get_redirect_url())
            
            if Service.objects.filter(company=company, name=name, category=category, sub_category=sub_category).exists():
                messages.warning(request, "Service already exists")
                return redirect(self.get_redirect_url())

            Service.objects.create(
                company = company, name = name, category = category, sub_category = sub_category, 
                description = description.strip(), price = price.strip(), duration = timedelta(days = int(duration.strip())) if duration else None, 
                is_active = bool(is_active)
                )
            
            messages.success(request, "Success! Service Created.")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in adding service in add service view of superadmin: {e}")
            messages.error(request, "Server Error")
            return redirect(self.get_redirect_url())
        

class UpdateServiceView(BaseServiceCompanyView, UpdateView):
    model = Service
    fields = ["name", "category", "sub_category", "description", "price", "duration", "is_active"]
    success_url = redirect_url = reverse_lazy("superadmin:home")
    template_name = "service_company/services/edit.html"

    def get_success_url(self):
        try:  
            return reverse_lazy("superadmin:services", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting succes url of UpdateServiceView of superadmin app: {e}")
            return self.success_url
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of UpdateServiceView of superadmin app: {e}")
            return self.redirect_url
        
    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Company")
            return self.redirect_url
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_current_company()
            context["categories"] = ServiceCategory.objects.filter(company = current_company)
            context["sub_categories"] = ServiceSubCategory.objects.filter(company = current_company)
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateServiceView of superadmin app: {e}")
        
        return context
        
    def get_object(self):
        try:
            current_company = self.get_current_company()
            return get_object_or_404(self.model, company = current_company, slug = self.kwargs.get("service_slug"))
        
        except Http404:
            messages.error(self.request, "Invalid service")
            return redirect(self.get_redirect_url())        

    def post(self, request, *args, **kwargs):
        try:            
            name = request.POST.get("name")
            category_slug = request.POST.get("category")
            sub_category_slug = request.POST.get("sub_category")

            description = request.POST.get("description")

            price = request.POST.get("price")
            duration = request.POST.get("duration")
            is_active = request.POST.get("is_active")

            required_fields = {
                "Service Name": name.strip(),
                "Category": category_slug,
                "Sub Category": sub_category_slug,                
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            category = None
            try:
                category = get_object_or_404(ServiceCategory, slug = category_slug.strip())
            except Http404:
                messages.error(request, "Failed! Invalid Category")
                return redirect(self.get_redirect_url())
            
            sub_category = None
            try:
                sub_category = get_object_or_404(ServiceSubCategory, slug = sub_category_slug.strip())
            except Http404:
                messages.error(request, "Failed! Invalid Sub Category")
                return redirect(self.get_redirect_url())
            
            service = self.get_object()

            similar_services = self.model.objects.filter(
                company = service.company, name = name, category = category, sub_category = sub_category
                )

            if similar_services.exists() and similar_services.first() != service:                
                messages.warning(request, "Similar service already exists")
                return redirect(self.get_redirect_url())

            service.name = name.strip()
            service.category = category
            service.sub_category = sub_category
            service.description = description.strip() if description else None
            service.price = price.strip() if price else None
            service.duration = timedelta(days = int(duration.strip()))
            service.is_active = bool(is_active)
            service.save()
            
            messages.success(request, "Success! Service Updated")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in UpdateServiceView of superadmin: {e}")
            messages.error(request, "An unexpected error occured")
            return redirect(self.get_redirect_url())
        

class RemoveServiceView(BaseServiceCompanyView, View):
    model = Service
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:services", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveServiceView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveServiceView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("category_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted service")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid service")

        except Exception as e:
            logger.exception(f"Error in RemoveServiceView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return self.get_redirect_url()


class ListServiceCategoryView(BaseServiceCompanyView, ListView):
    model = ServiceCategory
    queryset = model.objects.none()
    context_object_name = "categories"
    template_name = "service_company/categories/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of list service category view of superadmin: {e}")
            return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            context["service_category_page"] = True

        except Http404:
            messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of list service category view: {e}")

        return context
    

class AddServiceCategoryView(BaseServiceCompanyView, CreateView):
    model = ServiceCategory
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:service_categories", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def post(self, request, *args, **kwargs):
        try:
            current_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name")
            name = name.strip() if name else None
            
            if name:
                product, created = self.model.objects.get_or_create(company = current_company, name = name)

                if created:
                    messages.success(request, "Success! Service category created.")
                    return redirect(self.get_success_url())

                else:
                    messages.warning(request, "Service category already exists.")
            
            else:
                messages.error(request, "Service category name is required.")            
        
        except Exception as e:
            logger.error(f"Error in creating service category: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.get_redirect_url())
    

class UpdateServiceCategoryView(BaseServiceCompanyView, UpdateView):
    model = ServiceCategory
    fields = ["name"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:  
            return reverse_lazy("superadmin:service_categories", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting succes url of UpdateServiceCategoryView of superadmin app: {e}")
            return self.success_url
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of UpdateServiceCategoryView of superadmin app: {e}")
            return self.redirect_url
        
    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Company")
            return self.redirect_url
        
    def get_object(self):
        try:
            current_company = self.get_current_company()
            return get_object_or_404(self.model, company = current_company, slug = self.kwargs.get("category_slug"))
        
        except Http404:
            messages.error(self.request, "Invalid service category")
            return redirect(self.get_redirect_url())        

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            if not name:
                messages.error(request, f"Failed! Name of service category is required")
                return redirect(self.get_redirect_url())
            
            category = self.get_object()

            updating_name = name if name else category.name
            
            if self.model.objects.filter(company = category.company, name = updating_name).exists():
                messages.warning(request, "Category with the given name already exists")
                return redirect(self.get_redirect_url())
            
            category.name = updating_name
            category.save()

            messages.success(request, "Success! Service category updated.")
            return redirect(self.get_success_url())                                                       
        
        except Exception as e:
            logger.exception(f"Error in updating service category by superadmin: {e}")
            messages.error(request, "An unexpected error occured")

        return redirect(self.get_redirect_url())
    

class RemoveServiceCategoryView(BaseServiceCompanyView, View):
    model = ServiceCategory
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:service_categories", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveServiceCategoryView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveServiceCategoryView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("category_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted service category")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid service category")

        except Exception as e:
            logger.exception(f"Error in RemoveServiceCategoryView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return self.get_redirect_url()
    

class ListServiceSubCategoryView(BaseServiceCompanyView, ListView):
    model = ServiceSubCategory
    queryset = model.objects.none()
    context_object_name = "sub_categories"
    template_name = "service_company/sub_categories/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of list service sub category view of superadmin: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            context["service_sub_category_page"] = True
            context["categories"] = ServiceCategory.objects.all().order_by('name')

        except Http404:
            messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of list service sub category view: {e}")

        return context
    

class ListServiceEnquiryView(BaseServiceCompanyView, ListView):
    model = ServiceEnquiry
    queryset = model.objects.none()
    context_object_name = "enquiries"
    template_name = "service_company/enquiries/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListServiceEnquiryView of superadmin: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            context["service_enquiry_page"] = True

        except Http404:
            messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of ListServiceEnquiryView: {e}")

        return context
    

class AddServiceSubCategoryView(BaseServiceCompanyView, CreateView):
    model = ServiceSubCategory
    fields = ["name", "category"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:service_sub_categories", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def post(self, request, *args, **kwargs):
        try:
            current_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name")
            name = name.strip() if name else None

            category_slug = request.POST.get("category")

            if not category_slug or not name:
                error_msg = "Name of service sub category is required."
                if not category_slug:
                    error_msg = "Service category is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.get_redirect_url())
            
            category = get_object_or_404(ServiceCategory, slug = category_slug)
            
            sub_category, created = self.model.objects.get_or_create(company = current_company, name = name, category = category)

            if created:
                messages.success(request, "Success! Service sub category created.")
                return redirect(self.get_success_url())

            else:
                messages.warning(request, "Service sub category already exists.")

        except Http404:
            messages.error(request, "Invalid service sub category")                                    
        
        except Exception as e:
            logger.error(f"Error in creating service sub category by superadmin: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.get_redirect_url())
    

class UpdateServiceSubCategoryView(BaseServiceCompanyView, UpdateView):
    model = ServiceSubCategory
    fields = ["name", "category"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:  
            return reverse_lazy("superadmin:service_sub_categories", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting succes url of UpdateServiceSubCategoryView of superadmin app: {e}")
            return self.success_url
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of UpdateServiceSubCategoryView of superadmin app: {e}")
            return self.redirect_url
        
    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Company")
            return self.redirect_url
        
    def get_object(self):
        try:
            current_company = self.get_current_company()
            return get_object_or_404(self.model, company = current_company, slug = self.kwargs.get("sub_category_slug"))
        
        except Http404:
            messages.error(self.request, "Invalid service sub category")
            return redirect(self.get_redirect_url())        

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            category_slug = request.POST.get("category")

            if not category_slug or not name:
                error_msg = "Name of service sub category is required."
                if not category_slug:
                    error_msg = "Service category is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.get_redirect_url())
            
            category = get_object_or_404(ServiceCategory, slug = category_slug)
            
            sub_category = self.get_object()

            updating_name = name if name else sub_category.name
            updating_category = category if category else sub_category.category
            
            if self.model.objects.filter(company = sub_category.company, name = updating_name, category = updating_category).exists():
                messages.warning(request, "Sub category with the given data already exists")
                return redirect(self.get_redirect_url())
            
            sub_category.name = updating_name
            sub_category.category = updating_category
            sub_category.save()

            messages.success(request, "Success! Service sub category updated.")
            return redirect(self.get_success_url())                                                       
        
        except Exception as e:
            logger.error(f"Error in updating service sub category by superadmin: {e}")
            messages.error(request, "An unexpected error occured")

        return redirect(self.get_redirect_url())
    

class RemoveServiceSubCategoryView(BaseServiceCompanyView, View):
    model = ServiceSubCategory
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:service_sub_categories", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveServiceSubCategoryView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveServiceSubCategoryView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("sub_category_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted service sub category")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid service sub category")

        except Exception as e:
            logger.exception(f"Error in RemoveServiceSubCategoryView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return redirect(self.get_redirect_url())
    

# Registration Company
class BaseRegistrationCompanyView(AdminBaseView, View):
    success_url = redirect_url = reverse_lazy('superadmin:home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["company_list_page"] = True
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))

        except Http404:
            messages.error(self.request, "Invalid Company")
            return redirect(self.redirect_url)
        except Exception as e:
            logger.exception(f"Error in getting context data of base registration company view: {e}")

        return context
    

class ListRegistrationView(BaseRegistrationCompanyView, ListView):
    model = RegistrationDetail
    queryset = model.objects.none()
    context_object_name = "registrations"
    template_name = "registration_company/detail/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListRegistrationView of superadmin app: {e}")
            return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:            
            context["registration_page"] = True        
        except Exception as e:
            logger.exception(f"Error in getting context data of ListRegistrationView of superadmin app: {e}")

        return context

class AddRegistrationView(BaseRegistrationCompanyView, CreateView):
    model = RegistrationDetail
    fields = ["company", "sub_type", "price", "time_required", "required_documents", "additional_info"]
    template_name = "registration_company/detail/add.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:add_registration", kwargs = {'slug': self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in getting success url in AddRegistrationView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url in AddRegistrationView of superadmin app: {e}")
            return self.redirect_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["types"] = RegistrationType.objects.all()
            context["registration_page"] = True
            context["add_registration_page"] = True
        except Exception as e:
            logger.exception(f"Error in getting context data in AddRegistrationView of superadmin app: {e}")

        return context
    
    def get_company(self):
        try:
            company_slug = self.kwargs.get('slug')
            return get_object_or_404(Company, slug = company_slug.strip())
        except Http404:
            messages.error(self.request, "Invalid Company")
            return redirect(self.redirect_url)        

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_company()

            sub_type_slug = request.POST.get("sub_type")
            price = request.POST.get("price")
            time_required = request.POST.get("time_required")
            required_documents = request.POST.get("required_documents")
            additional_info = request.POST.get("additional_info")

            required_fields = {
                "Sub Type": sub_type_slug,
                "Price": price,
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())            
            
            sub_type = get_object_or_404(RegistrationSubType, slug = sub_type_slug.strip())
            
            if self.model.objects.filter(company=company, sub_type=sub_type).exists():
                messages.warning(request, "Registration already exists")
                return redirect(self.get_redirect_url())

            self.model.objects.create(
                company = company, sub_type = sub_type, price = price.strip(), 
                time_required = time_required, required_documents = required_documents, 
                additional_info = additional_info
                )
            
            messages.success(request, "Success! Registration Created.")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Failed! Invalid Sub Type")

        except Exception as e:
            logger.exception(f"Error in adding registration in AddRegistrationView of superadmin app: {e}")
            messages.error(request, "An unexpected error occured")

        return redirect(self.get_redirect_url())
    

class UpdateRegistrationView(BaseRegistrationCompanyView, UpdateView):
    model = RegistrationDetail
    fields = ["sub_type", "price", "time_required", "required_documents", "additional_info"]
    template_name = "registration_company/detail/edit.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "registration"

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:registrations", kwargs = {'slug': self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in getting success url in EditRegistrationView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url in EditRegistrationView of superadmin app: {e}")
            return self.redirect_url

    def get_company(self):
        try:
            company_slug = self.kwargs.get('slug')
            return get_object_or_404(Company, slug = company_slug.strip())
        except Http404:
            messages.error(self.request, "Invalid Company")
            return redirect(self.redirect_url)    

    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get('registration_slug'))
        except Http404:
            messages.error(self.request, "Invalid registration")   
            return redirect(self.get_redirect_url())
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_company()
            registration = self.get_object()
            context["types"] = RegistrationType.objects.filter(company = current_company)
            context["sub_types"] = RegistrationSubType.objects.filter(company = current_company, type = registration.sub_type.type)
            context["registration_page"] = True            
        except Exception as e:
            logger.exception(f"Error in getting context data in EditRegistrationView of superadmin app: {e}")

        return context 

    def post(self, request, *args, **kwargs):
        try:
            sub_type_slug = request.POST.get("sub_type")
            price = request.POST.get("price")
            time_required = request.POST.get("time_required")
            required_documents = request.POST.get("required_documents")
            additional_info = request.POST.get("additional_info")

            required_fields = {
                "Sub Type": sub_type_slug,
                "Price": price.strip(),
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())            
            
            sub_type = get_object_or_404(RegistrationSubType, slug = sub_type_slug.strip())
            
            registration = self.get_object()
                        
            similar_registrations = self.model.objects.filter(company = registration.company, sub_type=sub_type)
            
            if similar_registrations.exists() and similar_registrations.first() != registration:
                messages.warning(request, "similar registration already exists")
                return redirect(self.get_redirect_url())

            registration.sub_type = sub_type
            registration.price = price.strip()
            registration.time_required = time_required.strip() if time_required else None
            registration.required_documents = required_documents.strip() if required_documents else None
            registration.additional_info = additional_info.strip() if additional_info else None
            registration.save()        
            
            messages.success(request, "Success! Registration Updated.")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Failed! Invalid Sub Type")

        except Exception as e:
            logger.exception(f"Error in updating registration in EditRegistrationView of superadmin app: {e}")
            messages.error(request, "An unexpected error occured")

        return redirect(self.get_redirect_url())
    

class RemoveRegistrationView(BaseRegistrationCompanyView, View):
    model = RegistrationDetail
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:registrations", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveRegistrationView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveRegistrationView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("registration_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted registration")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid registration")

        except Exception as e:
            logger.exception(f"Error in RemoveRegistrationView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return self.get_redirect_url()
    

class ListRegistrationTypeView(BaseRegistrationCompanyView, ListView):
    model = RegistrationType
    queryset = model.objects.none()
    context_object_name = "types"
    template_name = "registration_company/types/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListRegistrationTypeView of superadmin app: {e}")
            return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            context["registration_type_page"] = True

        except Http404:
            messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of ListRegistrationTypeView of superadmin app: {e}")

        return context
    

class AddRegistrationTypeView(BaseRegistrationCompanyView, CreateView):
    model = RegistrationType
    fields = ["name", "description"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:registration_types", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def post(self, request, *args, **kwargs):
        try:
            current_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name")
            name = name.strip() if name else None

            description = request.POST.get("description")
            description = description.strip() if description else None

            if not name:
                messages.error(request, "Name of registration type is required.")
                return redirect(self.get_redirect_url())
            
            registration_type, created = self.model.objects.get_or_create(company = current_company, name = name, description = description)

            if not created:
                messages.warning(request, "Registration type already exists.")
                return redirect(self.get_redirect_url())

            messages.success(request, "Success! Registration type created.")
            return redirect(self.get_success_url())
        
        except Exception as e:
            logger.error(f"Error in creating registration type: {e}")
            messages.error(request, "Server Error.")
            return redirect(self.get_redirect_url())
        

class UpdateRegistrationTypeView(BaseRegistrationCompanyView, UpdateView):
    model = RegistrationType
    fields = ["name", "description"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:registration_types", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get("registration_type_slug"))
        except Http404:
            messages.error(self.request, "Invalid registration type")
            return redirect(self.get_redirect_url())

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            description = request.POST.get("description")
            description = description.strip() if description else None

            if not name:
                messages.error(request, "Name of registration type is required.")
                return redirect(self.get_redirect_url())
            
            registration_type = self.get_object()

            similar_registration_types = self.model.objects.filter(company = registration_type.company, name = name)

            if similar_registration_types.exists() and similar_registration_types.first() != registration_type:
                messages.warning(request, "Similar registration type already exists")
                return redirect(self.get_redirect_url())
            
            registration_type.name = name
            registration_type.description = description
            registration_type.save()

            messages.success(request, "Success! Registration type updated.")
            return redirect(self.get_success_url())
        
        except Exception as e:
            logger.error(f"Error in updating registration type: {e}")
            messages.error(request, "An unexpected error occured")
            return redirect(self.get_redirect_url())
        

class RemoveRegistrationTypeView(BaseRegistrationCompanyView, View):
    model = RegistrationType
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:registration_types", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveRegistrationTypeView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveRegistrationTypeView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("registration_type_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted registration type")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid registration type")

        except Exception as e:
            logger.exception(f"Error in RemoveRegistrationTypeView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return self.get_redirect_url()


class ListRegistrationSubTypeView(BaseRegistrationCompanyView, ListView):
    model = RegistrationSubType
    queryset = model.objects.none()
    context_object_name = "sub_types"
    template_name = "registration_company/sub_types/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get('slug'))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListRegistrationSubTypeView of superadmin app: {e}")
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            context["registration_sub_type_page"] = True
            context["types"] = RegistrationType.objects.all().order_by('name')

        except Http404:
            messages.error(self.request, "Invalid Company")
        except Exception as e:
            logger.exception(f"Error in getting context data of ListRegistrationSubTypeView of superadmin app: {e}")

        return context
    
    
class AddRegistrationSubTypeView(BaseRegistrationCompanyView, CreateView):
    model = RegistrationSubType
    fields = ["name", "category", "description"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):        
        return reverse_lazy("superadmin:registration_sub_types", kwargs = {"slug": self.kwargs.get("slug")})
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def post(self, request, *args, **kwargs):
        try:
            current_company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            name = request.POST.get("name")
            name = name.strip() if name else None

            type_slug = request.POST.get("type")

            description = request.POST.get("description")
            description = description.strip() if description else None

            if not type_slug or not name:
                error_msg = "Name of registration sub type is required."
                if not type_slug:
                    error_msg = "Registration type is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.get_redirect_url())
            
            type = get_object_or_404(RegistrationType, slug = type_slug)
            
            sub_type, created = self.model.objects.get_or_create(company = current_company, name = name, type = type, description = description)

            if not created:
                messages.warning(request, "Registration sub type already exists.")
                return redirect(self.get_redirect_url())

            messages.success(request, "Success! Registration sub type created.")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid registration sub type")                                   
        
        except Exception as e:
            logger.error(f"Error in creating registration sub type by superadmin: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.get_redirect_url())
    

class UpdateRegistrationSubTypeView(BaseRegistrationCompanyView, UpdateView):
    model = RegistrationSubType
    fields = ["name", "category", "description"]
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:  
            return reverse_lazy("superadmin:registration_sub_types", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of UpdateRegistrationSubTypeView of superadmin app: {e}")
            return self.success_url
    
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of UpdateRegistrationSubTypeView of superadmin app: {e}")
            return self.redirect_url
        
    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Company")
            return redirect(self.redirect_url)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_current_company()
            context["types"] = RegistrationType.objects.filter(company = current_company)
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateRegistrationSubTypeView of superadmin app: {e}")
        
        return context
    
    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get("registration_sub_type_slug"))
        except Exception as e:
            messages.error(self.request, "Invalid registration sub type")
            return redirect(self.get_redirect_url())

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")
            name = name.strip() if name else None

            type_slug = request.POST.get("type")

            description = request.POST.get("description")
            description = description.strip() if description else None

            if not type_slug or not name:
                error_msg = "Name of registration sub type is required."
                if not type_slug:
                    error_msg = "Registration type is required."

                messages.error(request, f"Failed! {error_msg}")
                return redirect(self.get_redirect_url())
            
            type = get_object_or_404(RegistrationType, slug = type_slug)
            
            registration_sub_type = self.get_object()

            similar_registration_sub_types = self.model.objects.filter(
                company = registration_sub_type.company, name = name, type = type
                )
            
            if similar_registration_sub_types.exists() and similar_registration_sub_types.first() != registration_sub_type:
                messages.warning(request, "Similar registration sub type already exists")
                return redirect(self.get_redirect_url())
            
            registration_sub_type.name = name
            registration_sub_type.type = type
            registration_sub_type.description = description
            registration_sub_type.save()

            messages.success(request, "Success! Registration sub type updated.")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid registration sub type")                                   
        
        except Exception as e:
            logger.error(f"Error in updating registration sub type by superadmin: {e}")
            messages.error(request, "Server Error.")

        return redirect(self.get_redirect_url())
    

class RemoveRegistrationSubTypeView(BaseRegistrationCompanyView, View):
    model = RegistrationSubType
    success_url = redirect_url = reverse_lazy("superadmin:home")

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:registration_sub_types", kwargs = {"slug": self.kwargs.get("slug")})
        except Exception as e:
            logger.exception(f"Error in getting success url of RemoveRegistrationSubTypeView of superadmin app: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in getting redirect url of RemoveRegistrationSubTypeView of superadmin app: {e}")
            return self.redirect_url
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs.get("registration_sub_type_slug"))
            self.object.delete()
            messages.success(request, "Success! Deleted registration sub type")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid registration sub type")

        except Exception as e:
            logger.exception(f"Error in RemoveRegistrationSubTypeView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occured")

        return self.get_redirect_url()
    

# Directory
class BaseDirectoryView(AdminBaseView, ListView):
    model = Bank
    template_name = "directory/list.html"    
    queryset = model.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["directory_page"] = True
        except Exception as e:
            logger.exception(f"Error in getting context data of BaseDirectoryView in superadmin app: {e}")
        return context


class ListBankView(BaseDirectoryView, ListView):
    model = Bank
    queryset = model.objects.all()
    context_object_name = "banks"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_directory"] = "Bank"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListBankView in superadmin app: {e}")
        return context
    

class ListCourtView(BaseDirectoryView, ListView):
    model = Court
    queryset = model.objects.all()
    context_object_name = "courts"
    paginate_by = 10
    ordering = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_directory"] = "Court"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListCourtView in superadmin app: {e}")
        return context


class ListDestinationView(BaseDirectoryView, ListView):
    model = TouristAttraction
    queryset = model.objects.all()
    context_object_name = "destinations"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_directory"] = "Destination"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListDestinationView in superadmin app: {e}")
        return context


class ListPoliceStationView(BaseDirectoryView, ListView):
    model = PoliceStation
    queryset = model.objects.all()
    context_object_name = "police_stations"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_directory"] = "Police Station"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListPoliceStationView in superadmin app: {e}")
        return context


class ListPostOfficeView(BaseDirectoryView, ListView):
    model = PostOffice
    queryset = model.objects.all()
    context_object_name = "post_offices"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_directory"] = "Post Office"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListPostOfficeView in superadmin app: {e}")
        return context
    

# Settings

class SettingsView(AdminBaseView, TemplateView):
    model = User
    template_name = "settings/settings.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UpdatePasswordView(SettingsView, UpdateView):
    model = User
    success_url = reverse_lazy('authentication:login')
    redirect_url = reverse_lazy('superadmin:settings')

    def validate_password(self, password):
        password = str(password)

        if len(password) < 8:
            return "Password must contain at least 8 characters"
        
        if " " in password:
            return "Password cannot have any white spaces"
        
        if password.isalpha():
            return "Password must contain at least one digit"
        
        if password.isnumeric():
            return "Password must contain at least one alphabet"
        
        if password == password.lower() or password == password.upper():
            return "Password must contain at least one uppercase and one lowercase alphabet"
        
        if password.isalnum():
            return "Password must contain at least one special character"
        
        return None        

    def post(self, request, *args, **kwargs):
        try:
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            required_fields = {
                "Current password": current_password,
                "New password": new_password,
                "Confirm password": confirm_password
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! Field '{key}' is required")
                    return redirect(self.redirect_url)

            user = authenticate(request, username = request.user.username, password = current_password)

            if not user:
                messages.error(request, "The current password you entered is incorrect")
                return redirect(self.redirect_url)
            
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match")
                return redirect(self.redirect_url)
            
            validation_error_msg = self.validate_password(new_password)

            if validation_error_msg is not None:
                messages.warning(request, validation_error_msg)
                return redirect(self.redirect_url)
            
            user.set_password(new_password)
            user.save()

            logout(request)
            messages.success(request, "Success! Password changed")
            return redirect(self.success_url)
            
        except Exception as e:
            logger.exception(f"Error in UpdatePasswordView of superadmin app: {e}")
            return redirect(self.redirect_url)
        

class UpdateUserDetailView(SettingsView, UpdateView):
    model = User
    success_url = redirect_url = reverse_lazy('superadmin:settings')

    def post(self, request, *args, **kwargs):
        try:
            username = request.POST.get("username")
            email = request.POST.get("email")

            username = username.strip() if username else None
            email = email.strip() if email else None    
            
            required_fields = {
                "Username": username,
                "Email": email
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! Field {key} is required")
                    return redirect(self.redirect_url)
                
            user = request.user

            user.username = username
            user.email = email
            user.save()

            messages.success(request, "Success! User detail updation successfull")
            return redirect(self.success_url)

        except Exception as e:
            logger.exception(f"Error in UpdateUserDetailView in superadmin app: {e}")
            messages.error(request, "An unexpected error occured")
            return redirect(self.redirect_url)
        

# Custome Pages
class AddCustomPageView(AdminBaseView, TemplateView):
    template_name = "custom_pages/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["page_types"] = ("About Us", "Contact Us", "FAQ", "Privacy Policy", "Terms And Conditions", "Shipping And Delivery Policy", "Cancellation And Refund Policy")
            context["companies"] = Company.objects.all().order_by("name")
            context["states"] = UniqueState.objects.all()
        except Exception as e:
            logger.exception(f"Error in getting context data of AddCustomPageView of superadmin app: {e}")
        
        return context
    

class AddAboutUsPageView(AddCustomPageView, CreateView):
    model = AboutUs
    fields = ["company", "content"]
    success_url = redirect_url = reverse_lazy('superadmin:add_custom_page')

    def post(self, request, *args, **kwargs):
        try:
            company_slug = request.POST.get("company")
            content = request.POST.get("content")        

            company_slug = company_slug.strip() if company_slug else None
            content = content.strip() if content else None          

            if not company_slug:
                messages.error(request, "Failed! Company is required")
                return redirect(self.redirect_url)

            if not content:
                messages.error(request, "Failed! Content is required")
                return redirect(self.redirect_url)

            company = get_object_or_404(Company, slug = company_slug)

            self.model.objects.update_or_create(
                company = company, 
                defaults = {"content": content}
                )
            
            messages.success(request, f"Success! About us created for company: {company.name}")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in AddAboutUsPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occured.")

        return redirect(self.redirect_url)
    

class AddContactUsPageView(AddCustomPageView, CreateView):
    model = ContactUs
    fields = [
        "company", "email", "phone", "provide_query", "city", "district",
        "state", "pincode", "facebook", "x", "youtube", "instagram", "lat", "lon"
        ]
    success_url = redirect_url = reverse_lazy('superadmin:add_custom_page')    

    def post(self, request, *args, **kwargs):
        try:
            company_slug = request.POST.get("company")

            email = request.POST.get("email")
            phone = request.POST.get("phone")

            provide_query = request.POST.get("provide_query")

            place_slug = request.POST.get("place")
            district_slug = request.POST.get("district")
            state_slug = request.POST.get("state")
            pincode = request.POST.get("pincode")

            facebook = request.POST.get("facebook")
            x = request.POST.get("x")
            youtube = request.POST.get("youtube")
            instagram = request.POST.get("instagram")

            lat = request.POST.get("lat")
            lon = request.POST.get("lon")

            company_slug = company_slug.strip() if company_slug else None

            email = email.strip() if email else None
            phone = phone.strip() if phone else None

            pincode = pincode.strip() if pincode else None

            facebook = facebook.strip() if facebook else None
            x = x.strip() if x else None
            youtube = youtube.strip() if youtube else None
            instagram = instagram.strip() if instagram else None

            lat = lat.strip() if lat else None
            lon = lon.strip() if lon else None

            if not company_slug:
                messages.error(request, "Failed! Company is required")
                return redirect(self.redirect_url)

            if not email:
                messages.error(request, "Failed! Email is required")
                return redirect(self.redirect_url)
            
            if not phone:
                messages.error(request, "Failed! Phone is required")
                return redirect(self.redirect_url)

            company = get_object_or_404(Company, slug = company_slug)

            state = district = place = None

            if state_slug:
                state = get_state(state_slug)

                if not state:
                    messages.error(self.request, "Invalid State")
                    return redirect(self.redirect_url)

            if district_slug:
                district = get_district(district_slug)

                if not district:
                    messages.error(self.request, "Invalid District")
                    return redirect(self.redirect_url)

            if place_slug:
                place = get_place(place_slug)

                if not place:
                    messages.error(self.request, "Invalid Place")
                    return redirect(self.redirect_url)

            self.model.objects.update_or_create(
                company = company, 
                defaults = {
                    "email": email, "phone": phone, "provide_query": True if provide_query else False,
                    "place": place, "district": district, "state": state, "pincode": pincode, "facebook": facebook,
                    "x": x, "youtube": youtube, "instagram": instagram, "lat": lat, "lon": lon
                    }
                )
            
            messages.success(request, f"Success! Contact us created for company: {company.name}")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in AddContactUsPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occured.")

        return redirect(self.redirect_url)
    

class AddFaqPageView(AddCustomPageView, CreateView):
    model = FAQ
    fields = ["company", "question", "answer"]
    success_url = redirect_url = reverse_lazy('superadmin:add_custom_page')

    def post(self, request, *args, **kwargs):
        try:
            company_slug = request.POST.get("company")

            question = request.POST.get("question")
            answer = request.POST.get("answer")

            company_slug = company_slug.strip() if company_slug else None

            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            if not company_slug:
                messages.error(request, "Failed! Company is required")
                return redirect(self.redirect_url)

            if not question:
                messages.error(request, "Failed! Question is required")
                return redirect(self.redirect_url)
            
            if not answer:
                messages.error(request, "Failed! Answer is required")
                return redirect(self.redirect_url)

            company = get_object_or_404(Company, slug = company_slug)

            self.model.objects.update_or_create(
                company = company, question = question,
                defaults = {"answer": answer}
                )
            
            messages.success(request, f"Success! FAQ created for company: {company.name}")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in AddFaqPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occured.")

        return redirect(self.redirect_url)
    

class AddPrivacyPolicyPageView(AddCustomPageView, CreateView):
    model = PrivacyPolicy
    fields = [
        "company", "content", "support_email", "effective_date"        
        ]
    success_url = redirect_url = reverse_lazy('superadmin:add_custom_page')

    def post(self, request, *args, **kwargs):
        try:
            company_slug = request.POST.get("company")

            content = request.POST.get("content")
            support_email = request.POST.get("support_email")
            effective_date = request.POST.get("effective_date")        

            company_slug = company_slug.strip() if company_slug else None

            content = content.strip() if content else None
            support_email = support_email.strip() if support_email else None
            effective_date = effective_date.strip() if effective_date else None

            if not company_slug:
                messages.error(request, "Failed! Company is required")
                return redirect(self.redirect_url)
            
            if not content:
                messages.error(request, "Failed! Content is required")
                return redirect(self.redirect_url)

            if not effective_date:
                messages.error(request, "Failed! Effective date is required")
                return redirect(self.redirect_url)            

            company = get_object_or_404(Company, slug = company_slug)

            self.model.objects.update_or_create(
                company = company, 
                defaults = {
                    "effective_date": effective_date, "content": content,
                    "support_email": support_email
                    }
                )
            
            messages.success(request, f"Success! Privacy policy page created for company: {company.name}")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in AddPrivacyPolicyPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occured.")

        return redirect(self.redirect_url)
    

class AddTermsAndConditionsPageView(AddCustomPageView, CreateView):
    model = TermsAndConditions
    fields = ["company", "content", "version", "effective_date"]
    success_url = redirect_url = reverse_lazy('superadmin:add_custom_page')

    def post(self, request, *args, **kwargs):
        try:
            company_slug = request.POST.get("company")

            content = request.POST.get("content")
            version = request.POST.get("version")
            effective_date = request.POST.get("effective_date")

            company_slug = company_slug.strip() if company_slug else None

            content = content.strip() if content else None
            version = version.strip() if version else None

            if not company_slug:
                messages.error(request, "Failed! Company is required")
                return redirect(self.redirect_url)

            if not content:
                messages.error(request, "Failed! Content is required")
                return redirect(self.redirect_url)
            
            if not version:
                messages.error(request, "Failed! Version is required")
                return redirect(self.redirect_url)
            
            if not effective_date:
                messages.error(request, "Failed! Effective date is required")
                return redirect(self.redirect_url)

            company = get_object_or_404(Company, slug = company_slug)

            self.model.objects.update_or_create(
                company = company,
                defaults = {
                    "content": content,
                    "version": version,
                    "effective_date": effective_date
                    }
                )
            
            messages.success(request, f"Success! Terms and conditions created for company: {company.name}")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in AddTermsAndConditionsPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occured.")

        return redirect(self.redirect_url)
    

class BaseCustomPageView(AdminBaseView, ListView):
    model = AboutUs
    template_name = "custom_pages/list.html"    
    queryset = model.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["custom_page"] = True
        except Exception as e:
            logger.exception(f"Error in getting context data of BaseCustomPageView in superadmin app: {e}")
        return context
    

class ListAboutUsView(BaseCustomPageView, ListView):
    model = AboutUs
    queryset = model.objects.all()
    context_object_name = "about_us_objects"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "About Us"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListAboutUsView in superadmin app: {e}")
        return context
    

class ListContactUsView(BaseCustomPageView, ListView):
    model = ContactUs
    queryset = model.objects.all()
    context_object_name = "contact_us_objects"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "Contact Us"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListContactUsView in superadmin app: {e}")
        return context
    

class ListFaqView(BaseCustomPageView, ListView):
    model = FAQ
    queryset = model.objects.all()
    context_object_name = "faqs"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "FAQ"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListFaqView in superadmin app: {e}")
        return context
    

class ListPrivacyPolicyView(BaseCustomPageView, ListView):
    model = PrivacyPolicy
    queryset = model.objects.all()
    context_object_name = "privacy_policies"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "Privacy Policy"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListPrivacyPolicyView in superadmin app: {e}")
        return context
    

class ListPrivacyPolicyView(BaseCustomPageView, ListView):
    model = PrivacyPolicy
    queryset = model.objects.all()
    context_object_name = "privacy_policies"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "Privacy Policy"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListPrivacyPolicyView in superadmin app: {e}")
        return context


class ListTermsAndConditionsView(BaseCustomPageView, ListView):
    model = TermsAndConditions
    queryset = model.objects.all()
    context_object_name = "terms_and_conditions"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "Terms And Conditions"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListTermsAndConditionsView in superadmin app: {e}")
        return context
    

class AddShippingAndDeliveryPolicyPageView(AddCustomPageView, CreateView):
    model = ShippingAndDeliveryPolicy
    fields = ["company", "content"]
    success_url = redirect_url = reverse_lazy('superadmin:add_custom_page')

    def post(self, request, *args, **kwargs):
        try:
            company_slug = request.POST.get("company")
            content = request.POST.get("content")        

            company_slug = company_slug.strip() if company_slug else None
            content = content.strip() if content else None          

            if not company_slug:
                messages.error(request, "Failed! Company is required")
                return redirect(self.redirect_url)

            if not content:
                messages.error(request, "Failed! Content is required")
                return redirect(self.redirect_url)

            company = get_object_or_404(Company, slug = company_slug)

            self.model.objects.update_or_create(
                company = company, 
                defaults = {"content": content}
                )
            
            messages.success(request, f"Success! Shipping and Delivery Policy page created for company: {company.name}")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in AddShippingAndDeliveryPolicyPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occured.")

        return redirect(self.redirect_url)
    

class ListShippingAndDeliveryPolicyView(BaseCustomPageView, ListView):
    model = ShippingAndDeliveryPolicy
    queryset = model.objects.all()
    context_object_name = "shipping_and_delivery_policies"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "Shipping And Delivery Policy"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListShippingAndDeliveryPolicyView in superadmin app: {e}")
        return context
    

class AddCancellationAndRefundPolicyPageView(AddCustomPageView, CreateView):
    model = CancellationAndRefundPolicy
    fields = ["company", "content"]
    success_url = redirect_url = reverse_lazy('superadmin:add_custom_page')

    def post(self, request, *args, **kwargs):
        try:
            company_slug = request.POST.get("company")
            content = request.POST.get("content")        

            company_slug = company_slug.strip() if company_slug else None
            content = content.strip() if content else None          

            if not company_slug:
                messages.error(request, "Failed! Company is required")
                return redirect(self.redirect_url)

            if not content:
                messages.error(request, "Failed! Content is required")
                return redirect(self.redirect_url)

            company = get_object_or_404(Company, slug = company_slug)

            self.model.objects.update_or_create(
                company = company, 
                defaults = {"content": content}
                )
            
            messages.success(request, f"Success! Cancellation and Refund Policy page created for company: {company.name}")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Company")

        except Exception as e:
            logger.exception(f"Error in AddCancellationAndRefundPolicyPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occured.")

        return redirect(self.redirect_url)


class ListCancellationAndRefundPolicyView(BaseCustomPageView, ListView):
    model = CancellationAndRefundPolicy
    queryset = model.objects.all()
    context_object_name = "Cancellation_and_refund_policies"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["current_custom_page"] = "Cancellation And Refund Policy"
        except Exception as e:
            logger.exception(f"Error in getting context data of ListCancellationAndRefundPolicyView in superadmin app: {e}")
        return context


# Company Detail
class AddCourseDetailView(BaseCompanyView, CreateView):
    model = CourseDetail
    fields = "__all__"
    template_name = "education_company/course_detail/add.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_current_company(self):
        try:
            company_slug = self.kwargs.get('slug')            
            return get_object_or_404(Company, slug = company_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Company")
            return redirect(self.redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_detail_page"] = True
            
            current_company = self.get_current_company()
            
            context["current_company"] = current_company

            context["courses"] = Course.objects.filter(company = current_company)
        except Exception as e:
            logger.exception(f"Error in getting context data of AddCompanyDetailView of superadmin: {e}")
        
        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_course_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddCompanyDetailView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of AddCompanyDetailView of superadmin: {e}")
            return self.redirect_url
        
    def get_course(self, course_slug):
        try:
            return get_object_or_404(Course, slug = course_slug)
        except Http404:
            messages.error(self.request, "Invalid Course")
            return redirect(self.get_redirect_url())
        
    def handle_features(self, request, company, course):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    CourseFeature.objects.filter(company = company, course = course).delete()

                    features = [CourseFeature(company=company, course=course, feature=feature) for feature in features_list]
                    CourseFeature.objects.bulk_create(features)

                    feature_objs = CourseFeature.objects.filter(company = company, course = course)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of AddCourseDetailView: {e}")
        
        return []

    def handle_vertical_tab(self, request, company, course):
        try:
            vertical_tab_objects = []

            vertical_heading_list = request.POST.getlist("vertical_heading")
            vertical_sub_heading_list = request.POST.getlist("vertical_sub_heading")
            vertical_summary_list = request.POST.getlist("vertical_summary")
            vertical_bullet_list = request.POST.getlist("vertical_bullet")
            vertical_bullet_count_list = request.POST.getlist("vertical_bullet_count")            

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")

            vertical_bullet_count_list = [int(count) for count in vertical_bullet_count_list]

            vertical_heading_list = [heading.strip() for heading in vertical_heading_list]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in vertical_sub_heading_list]
            vertical_summary_list = [summary.strip() for summary in vertical_summary_list]
            vertical_bullet_list = [bullet.strip() for bullet in vertical_bullet_list]
            
            initial = 0

            CourseVerticalTab.objects.filter(company = company, course = course).delete()
            CourseVerticalBullet.objects.filter(company = company, course = course).delete()

            with transaction.atomic():
                for i in range(len(vertical_bullet_count_list)):
                    vertical_tab_obj = CourseVerticalTab.objects.create(
                        company = company,
                        course = course,
                        heading = vertical_heading_list[i],
                        sub_heading = vertical_sub_heading_list[i],
                        summary = vertical_summary_list[i]
                    )

                    final = initial + vertical_bullet_count_list[i]
                    vertical_bullets = vertical_bullet_list[initial:final]
                    initial = final

                    if vertical_bullet_count_list[i] == 0:
                        continue
                    
                    creating_vertical_bullets = [CourseVerticalBullet(
                        company = company, course = course, heading = vertical_heading_list[i],
                        bullet = bullet
                    ) for bullet in vertical_bullets]

                    CourseVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                    created_vertical_bullets = CourseVerticalBullet.objects.filter(company = company, course = course)

                    vertical_tab_obj.bullets.set(created_vertical_bullets)

                    vertical_tab_objects.append(vertical_tab_obj)                        

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tab function of AddCourseDetailView: {e}")

        return None
    
    def handle_horizontal_tab(self, request, company, course):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = request.POST.getlist("horizontal_heading")
            horizontal_summary_list = request.POST.getlist("horizontal_summary")
            horizontal_bullet_list = request.POST.getlist("horizontal_bullet")
            horizontal_bullet_count_list = request.POST.getlist("horizontal_bullet_count")            

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")

            horizontal_bullet_count_list = [int(count) for count in horizontal_bullet_count_list]

            horizontal_heading_list = [heading.strip() for heading in horizontal_heading_list]
            horizontal_summary_list = [summary.strip() for summary in horizontal_summary_list]
            horizontal_bullet_list = [bullet.strip() for bullet in horizontal_bullet_list]
            
            initial = 0

            CourseHorizontalTab.objects.filter(company = company, course = course).delete()
            CourseHorizontalBullet.objects.filter(company = company, course = course).delete()

            with transaction.atomic():
                for i in range(len(horizontal_bullet_count_list)):
                    horizontal_tab_obj = CourseHorizontalTab.objects.create(
                        company = company,
                        course = course,
                        heading = horizontal_heading_list[i],
                        summary = horizontal_summary_list[i]
                    )

                    final = initial + horizontal_bullet_count_list[i]
                    horizontal_bullets = horizontal_bullet_list[initial:final]
                    initial = final
                    
                    if horizontal_bullet_count_list[i] == 0:
                        continue
                    
                    creating_horizontal_bullets = [CourseHorizontalBullet(
                        company = company, course = course, heading = horizontal_heading_list[i],
                        bullet = bullet
                    ) for bullet in horizontal_bullets]

                    CourseHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                    created_horizontal_bullets = CourseHorizontalBullet.objects.filter(company = company, course = course)

                    horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                    horizontal_tab_objects.append(horizontal_tab_obj)                                        

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tab function of AddCourseDetailView: {e}")

        return None
    
    def handle_table(self, request, company, course):
        try:
            course_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)

            CourseTableData.objects.filter(company = company, course = course).delete()
            CourseTable.objects.filter(company = company, course = course).delete()

            with transaction.atomic():
                for index, heading in enumerate(heading_list):
                    course_table = CourseTable.objects.create(
                        company = company, course = course, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [CourseTableData(
                            company = company, course = course,
                            heading = heading, data = data
                            ) for data in data_list_of_heading]

                    CourseTableData.objects.bulk_create(table_data_objs )


                    course_table_data_objs = CourseTableData.objects.filter(company = company, course = course, heading = heading)

                    course_table.datas.set(course_table_data_objs)

                    course_tables.append(course_table)

            return course_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_table function of AddCourseDetailView: {e}")

        return None
    
    def handle_bullet_points(self, request, company, course):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            CourseBulletPoint.objects.filter(company = company, course = course).delete()

            if bullet_point_list:
                bullet_point_objects = [CourseBulletPoint(
                    company = company, course = course,
                    bullet_point = bullet_point
                ) for bullet_point in bullet_point_list]

                CourseBulletPoint.objects.bulk_create(bullet_point_objects)

                bullet_points = CourseBulletPoint.objects.filter(company = company, course = course)                

                return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of AddCourseDetailView: {e}")

        return []

    def handle_tags(self, request, company, course):
        try:
            tag_list = [tag.strip() for tag in request.POST.getlist("tag")]
            tag_link_list = [tag_link.strip() for tag_link in request.POST.getlist("tag_link")]

            print("Received tags: ", tag_list)
            print("Received links: ", tag_link_list)

            if len(tag_link_list) != len(tag_list):
                raise ValueError("The number of tags does not match the number of links.")

            CourseTag.objects.filter(company = company, course = course).delete()
            if tag_list and tag_link_list:                
                creating_tags = [CourseTag(
                    company = company, course = course,
                    tag = tag, link = link
                    ) for tag, link in zip(tag_list, tag_link_list)]

                CourseTag.objects.bulk_create(creating_tags)

                course_tags = CourseTag.objects.filter(company = company, course = course)                

                return course_tags

        except Exception as e:
            logger.exception(f"Error in handle_tags function of AddCourseDetailView: {e}")

        return []

    def handle_timelines(self, request, company, course):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]

            print("Received headings: ", heading_list)
            print("Received summaries: ", summary_list)

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            if heading_list and summary_list:
                creating_timelines = [CourseTimeline(
                    company = company, course = course,
                    heading = heading, summary = summary
                    ) for heading, summary in zip(heading_list, summary_list)]

                CourseTimeline.objects.bulk_create(creating_timelines)

                course_timelines = CourseTimeline.objects.filter(company = company, course = course)

                for index, timeline in enumerate(course_timelines):
                    print({
                        "No": index + 1,
                        "Timeline Name": timeline.heading,
                        "Timeline": timeline.summary
                    })
                    print()

                return course_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of AddCourseDetailView: {e}")

        return []

    def post(self, request, *args, **kwargs):
        try:
            course_slug = request.POST.get('course')

            summary = request.POST.get("summary")
            description = request.POST.get("description")
            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")            

            # Fetch current company
            company = self.get_current_company()

            if not company or company.type.name != "Education" :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Course": course_slug,
                "summary": summary,
                "description": description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            course = self.get_course(course_slug)

            with transaction.atomic():
            
                course_detail = self.model.objects.create(
                    company = company, course = course, summary = summary, description = description,
                    vertical_title = vertical_title, horizontal_title = horizontal_title,
                    table_title = table_title, bullet_title = bullet_title, tag_title = tag_title, 
                    timeline_title = timeline_title
                )

                # For Features
                feature_objs = self.handle_features(request, company, course)
                if feature_objs:
                    course_detail.features.set(feature_objs)
                
                # For Vertical Tab            
                vertical_tab_objects =  self.handle_vertical_tab(request, company, course)
                if vertical_tab_objects:
                    course_detail.vertical_tabs.set(vertical_tab_objects)

                # For Horizontal Tab            
                horizontal_tab_objects =  self.handle_horizontal_tab(request, company, course)
                if horizontal_tab_objects:
                    course_detail.horizontal_tabs.set(horizontal_tab_objects)

                # For Table
                table_objects = self.handle_table(request, company, course)
                if table_objects:
                    course_detail.tables.set(table_objects)    

                # For Bullet Points
                bullet_points = self.handle_bullet_points(request, company, course)
                if bullet_points:
                    course_detail.bullet_points.set(bullet_points)

                # For Tags
                tags = self.handle_tags(request, company, course)
                if tags:
                    course_detail.tags.set(tags)

                # For Timeline
                timelines = self.handle_timelines(request, company, course)
                if timelines:
                    course_detail.timelines.set(timelines)

                messages.success(request, "Success! Created course detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddCompanyDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occured")

        return redirect(self.get_redirect_url())
    

class CourseDetailsListView(BaseEducationCompanyView, ListView):
    model = CourseDetail
    template_name = "education_company/course_detail/list.html"
    queryset = model.objects.none()
    success_url = redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "course_details"

    def get_current_company(self):
        try:
            company_slug = self.kwargs.get('slug')            
            return get_object_or_404(Company, slug = company_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Company")
            return redirect(self.redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_detail_page"] = True
            
            current_company = self.get_current_company()
            
            context["current_company"] = current_company

        except Exception as e:
            logger.exception(f"Error in getting context data of AddCompanyDetailView of superadmin: {e}")
        
        return context
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company)
        except Exception as e:
            logger.exception(f"Error in getting queryset of CourseDetailsListView of superadmin: {e}")
            return self.queryset
        

class CourseDetailView(BaseEducationCompanyView, DetailView):
    model = CourseDetail
    template_name = "education_company/course_detail/detail.html"
    redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "course_detail"

    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:course_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url function of CourseDetailView: {e}")
            return self.redirect_url

    def get_current_company(self):
        try:
            company_slug = self.kwargs.get('slug')            
            return get_object_or_404(Company, slug = company_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Company")
            return redirect(self.redirect_url)
        
    def get_current_course(self):
        try:
            course_slug = self.kwargs.get('course_slug')
            return get_object_or_404(Course, slug = course_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Course")
            return redirect(self.redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_detail_page"] = True
            
            current_company = self.get_current_company()
            
            context["current_company"] = current_company

        except Exception as e:
            logger.exception(f"Error in getting context data of AddCompanyDetailView of superadmin: {e}")
        
        return context
    
    def get_object(self):
        try:
            current_company = self.get_current_company()
            current_course = self.get_current_course()
            return get_object_or_404(self.model, company = current_company, course = current_course)
        
        except Http404:
            messages.error(self.request, "Invalid course for this company")

        except Exception as e:
            logger.exception(f"Error in get_object function of CourseDetailView of superadmin: {e}")

        return redirect(self.get_redirect_url())
    

class UpdateCourseDetailView(BaseCompanyView, UpdateView):
    model = CourseDetail
    fields = "__all__"
    template_name = "education_company/course_detail/update.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')
    
    def get_current_company(self):
        try:
            company_slug = self.kwargs.get('slug')            
            return get_object_or_404(Company, slug = company_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Company")
            return redirect(self.redirect_url)
        
    def get_course(self):
        try:
            course_slug = self.kwargs.get('course_slug')
            return get_object_or_404(Course, slug = course_slug)
        except Http404:
            messages.error(self.request, "Invalid Course")
            return redirect(self.get_redirect_url())
        
    def get_course_detail(self):
        try:
            current_company = self.get_current_company()
            current_course = self.get_course()

            return get_object_or_404(CourseDetail, company = current_company, course = current_course)
        
        except Http404:
            messages.error(self.request, "Invalid course detail object")
            return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_detail_page"] = True
            
            current_company = self.get_current_company()
            
            context["current_company"] = current_company

            context["course_detail"] = self.get_course_detail()

            context["course"] = Course.objects.filter(company = current_company)
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateCourseDetailView of superadmin: {e}")
        
        return context
    
    def get_object(self):
        try:
            return self.get_course_detail()
        except Exception as e:
            logger.exception(f"Error in get_object function of UpdateCourseDetailView of superadmin: {e}")
            return None
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_course_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateCourseDetailView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateCourseDetailView of superadmin: {e}")
            return self.redirect_url
        
    def get_course(self, course_slug):
        try:
            return get_object_or_404(Course, slug = course_slug)
        except Http404:
            messages.error(self.request, "Invalid Course")
            return redirect(self.get_redirect_url())
        