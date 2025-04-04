from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, View, CreateView, ListView, UpdateView, DetailView, DeleteView
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
from django.contrib.auth.models import User
import logging
from .tasks import send_company_created_email
from django.db import transaction

from .forms import (
    CourseMultiPageDescriptionForm, CourseDetailDescriptionForm, ServiceMultiPageDescriptionForm, RegistrationMultiPageDescriptionForm,
    ServiceDetailDescriptionForm, RegistrationDetailPageDescriptionForm, ProductMultiPageDescriptionForm, 
    ProductDetailDescriptionForm, CompanyForm, BlogContentForm, MetaTagDescriptionForm
    )

from custom_pages.models import (
    AboutUs, ContactUs, FAQ, PrivacyPolicy, TermsAndConditions,
    ShippingAndDeliveryPolicy, CancellationAndRefundPolicy
    )
from company.models import Company, CompanyType, Client, Testimonial, Testimonial
from locations.models import UniqueState, UniqueDistrict, UniquePlace

from product.models import (
    Product, Category as ProductCategory, SubCategory as ProductSubCategory, Color, Size, Brand,
    Faq as ProductFaq, Review as ProductReview, Enquiry as ProductEnquiry,

    ProductDetailPage, Feature as ProductFeature, VerticalTab as ProductVerticalTab, VerticalBullet as ProductVerticalBullet,
    HorizontalTab as ProductHorizontalTab, HorizontalBullet as ProductHorizontalBullet, Table as ProductTable, 
    TableData as ProductTableData, BulletPoint as ProductBulletPoint, Tag as ProductTag, Timeline as ProductTimeline,

    MultiPage as ProductMultiPage, MultiPageFeature as ProductMultiPageFeature, MultiPageVerticalTab as ProductMultiPageVerticalTab,
    MultiPageVerticalBullet as ProductMultiPageVerticalBullet, MultiPageHorizontalTab as ProductMultiPageHorizontalTab,
    MultiPageHorizontalBullet as ProductMultiPageHorizontalBullet, MultiPageTable as ProductMultiPageTable, 
    MultiPageTableData as ProductMultiPageTableData, MultiPageBulletPoint as ProductMultiPageBulletPoint,
    MultiPageTag as ProductMultiPageTag, MultiPageFaq as ProductMultiPageFaq, MultiPageTimeline as ProductMultiPageTimeline
    )

from educational.models import (
    Program, Course, Specialization, Enquiry as CourseEnquiry, CourseDetail, Feature as CourseFeature,
    VerticalTab as CourseVerticalTab, VerticalBullet as CourseVerticalBullet, HorizontalTab as CourseHorizontalTab,
    HorizontalBullet as CourseHorizontalBullet, TableData as CourseTableData, Table as CourseTable,
    BulletPoints as CourseBulletPoint, Tag as CourseTag, Timeline as CourseTimeline, Faq as CourseFaq,
    Testimonial as StudentTestimonial, MultiPage as CourseMultiPage,

    MultiPageFeature as CourseMultiPageFeature, MultiPageVerticalTab as CourseMultiPageVerticalTab, 
    MultiPageVerticalBullet as CourseMultiPageVerticalBullet, MultiPageHorizontalTab as CourseMultiPageHorizontalTab,
    MultiPageHorizontalBullet as CourseMultiPageHorizontalBullet, MultiPageTableData as CourseMultiPageTableData, 
    MultiPageTable as CourseMultiPageTable, MultiPageBulletPoints as CourseMultiPageBulletPoint, 
    MultiPageTag as CourseMultiPageTag, MultiPageTimeline as CourseMultiPageTimeline, MultiPageFaq as CourseMultiPageFaq,
    )

from directory.models import PostOffice, PoliceStation, Bank, Court, TouristAttraction

from service.models import (
    Service, Category as ServiceCategory, SubCategory as ServiceSubCategory, Enquiry as ServiceEnquiry,
    Faq as ServiceFaq, ServiceDetail, Feature as ServiceFeature,
    VerticalTab as ServiceVerticalTab, VerticalBullet as ServiceVerticalBullet, HorizontalTab as ServiceHorizontalTab,
    HorizontalBullet as ServiceHorizontalBullet, TableData as ServiceTableData, Table as ServiceTable,
    BulletPoints as ServiceBulletPoint, Tag as ServiceTag, Timeline as ServiceTimeline,

    MultiPage as ServiceMultiPage, MultiPageFeature as ServiceMultiPageFeature, MultiPageHorizontalTab as ServiceMultiPageHorizontalTab,
    MultiPageHorizontalBullet as ServiceMultiPageHorizontalBullet, MultiPageVerticalTab as ServiceMultiPageVerticalTab,
    MultiPageVerticalBullet as ServiceMultiPageVerticalBullet, MultiPageBulletPoint as ServiceMultiPageBulletPoint,
    MultiPageTag as ServiceMultiPageTag, MultiPageTimeline as ServiceMultiPageTimeline, MultiPageFaq as ServiceMultiPageFaq,
    MultiPageTable as ServiceMultiPageTable, MultiPageTableData as ServiceMultiPageTableData,
    )

from registration.models import (
    RegistrationType, RegistrationSubType, RegistrationDetail, Faq as RegistrationFaq,
    Enquiry as RegistrationEnquiry,

    RegistrationDetailPage, Feature as RegistrationFeature, HorizontalTab as RegistrationHorizontalTab,
    HorizontalBullet as RegistrationHorizontalBullet, VerticalTab as RegistrationVerticalTab, VerticalBullet as RegistrationVerticalBullet, 
    Table as RegistrationTable, BulletPoint as RegistrationBulletPoint, Tag as RegistrationTag, TableData as RegistrationTableData,
    Timeline as RegistrationTimeline,

    MultiPage as RegistrationMultiPage, MultiPageFeature as RegistrationMultiPageFeature, MultiPageVerticalTab as RegistrationMultiPageVerticalTab,
    MultiPageVerticalBullet as RegistrationMultiPageVerticalBullet, MultiPageHorizontalTab as RegistrationMultiPageHorizontalTab,
    MultiPageHorizontalBullet as RegistrationMultiPageHorizontalBullet, MultiPageTable as RegistrationMultiPageTable,
    MultiPageTableData as RegistrationMultiPageTableData, MultiPageTag as RegistrationMultiPageTag, MultiPageTimeline as RegistrationMultiPageTimeline,
    MultiPageFaq as RegistrationMultiPageFaq, MultiPageBulletPoint as RegistrationMultiPageBulletPoint
    )
from blog.models import Blog

from base.models import MetaTag

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["home_page"] = True
        return context


# Company

class BaseCompanyView(AdminBaseView):
    model = Company
    slug_url_kwarg = 'slug'

    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get(self.slug_url_kwarg), type__name = "Product")
        except Http404:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # context['company_type_page'] = True
            context["current_company"] = self.get_current_company()
            context["company_page"] = True
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
    form_class = CompanyForm
    template_name = "admin_company/company/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = MetaTag.objects.all().order_by("name")
        return context

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            name = request.POST.get("name")
            type = request.POST.get("type")
            slug = request.POST.get("slug")
            favicon = request.FILES.get('favicon')
            logo = request.FILES.get('logo')
            phone1 = request.POST.get("phone1")
            phone2 = request.POST.get("phone2")
            whatsapp = request.POST.get("whatsapp")
            email = request.POST.get("email")

            facebook = request.POST.get("email")
            twitter = request.POST.get("twitter")
            linkedin = request.POST.get("linkedin")
            youtube = request.POST.get("youtube")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            name = name.strip() if name else None
            type = type.strip() if type else None
            slug = slug.strip() if slug else None
            phone1 = phone1.strip() if phone1 else None
            phone2 = phone2.strip() if phone2 else None
            whatsapp = whatsapp.strip() if whatsapp else None
            email = email.strip() if email else None

            facebook = facebook.strip() if facebook else None
            twitter = twitter.strip() if twitter else None
            linkedin = linkedin.strip() if linkedin else None
            youtube = youtube.strip() if youtube else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]
            
            required_fields = {
                "Name": name, "Type": type, "Contact Number 1": phone1,
                "Contact Number 2": phone2, "Whats App Number": whatsapp,
                "Email": email, "Meta Tags": meta_tags, 
                "Meta Description": meta_description
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.redirect_url)

            description = None
            if form.is_valid():
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")
                description = description.strip() if description else None

            type = CompanyType.objects.get(slug = type)

            with transaction.atomic():

                company_obj = self.model.objects.create(
                    name = name, type=type, slug=slug,
                    favicon=favicon, logo=logo, phone1=phone1,
                    phone2=phone2, whatsapp=whatsapp, email=email,
                    description=description, meta_title = meta_title,
                    meta_description = meta_description,

                    facebook = facebook, twitter = twitter, 
                    linkedin = linkedin, youtube = youtube
                    )

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)

                company_obj.meta_tags.set(meta_tag_objs)

                company_obj.save()
                
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
    form_class = CompanyForm
    template_name = "admin_company/company/update.html"
    success_url = redirect_url = reverse_lazy('superadmin:companies')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context["tags"] = MetaTag.objects.all().order_by("name")
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
            form = self.get_form()

            name = request.POST.get("name")
            type = request.POST.get("type")
            slug = request.POST.get("slug")
            favicon = request.FILES.get('favicon')
            logo = request.FILES.get('logo')
            phone1 = request.POST.get("phone1")
            phone2 = request.POST.get("phone2")
            whatsapp = request.POST.get("whatsapp")
            email = request.POST.get("email")

            facebook = request.POST.get("facebook")
            twitter = request.POST.get("twitter")
            linkedin = request.POST.get("linkedin")
            youtube = request.POST.get("youtube")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            name = name.strip() if name else None
            type = type.strip() if type else None
            slug = slug.strip() if slug else None
            phone1 = phone1.strip() if phone1 else None
            phone2 = phone2.strip() if phone2 else None
            whatsapp = whatsapp.strip() if whatsapp else None
            email = email.strip() if email else None

            facebook = facebook.strip() if facebook else None
            twitter = twitter.strip() if twitter else None
            linkedin = linkedin.strip() if linkedin else None
            youtube = youtube.strip() if youtube else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            required_fields = {
                "Name": name, "Type": type, "Contact Number 1": phone1,
                "Contact Number 2": phone2, "Whats App Number": whatsapp,
                "Email": email, "Meta Tags": meta_tags, 
                "Meta Description": meta_description
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.redirect_url)

            type = CompanyType.objects.get(slug = type)

            self.object = self.get_object()

            description = None

            if form.is_valid():
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")
                description = description.strip() if description else None

            self.object.name = name
            self.object.type = type
            self.object.slug = slug
            self.object.favicon = favicon if favicon else self.object.favicon
            self.object.logo = logo if logo else self.object.logo
            self.object.phone1 = phone1
            self.object.phone2 = phone2
            self.object.whatsapp = whatsapp
            self.object.email = email
            self.object.description = description

            self.object.facebook = facebook
            self.object.twitter = twitter
            self.object.linkedin = linkedin
            self.object.youtube = youtube

            self.object.meta_title = meta_title
            self.object.meta_description = meta_description

            meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)

            self.object.meta_tags.set(meta_tag_objs)

            self.object.save()

            messages.success(request, "Company Updation Successfull.")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in updating company: {e}")
            return redirect(self.get_redirect_url())


class DeleteCompanyView(BaseCompanyView, UpdateView):
    success_url = redirect_url = reverse_lazy("superadmin:companies")
    slug_url_kwarg = 'slug'
            
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Company Deletion Successfull.")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Failed! Invalid Company")

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
class BaseProductCompanyView(BaseCompanyView, View):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try: 
            context["company_type"] = False
            context["product_company_page"] = True
            context["current_company"] = get_object_or_404(Company, slug = self.kwargs.get('slug'))
        except Http404:
            logger.error(f"Invalid product company in context of base product company view of superadmin.")
        except Exception as e:
            logger.exception(f"Error in fetching context data of base product company view of super admin: {e}")
        return context

class BaseProductView(BaseProductCompanyView, View):
    model = Product
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:products', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of BaseProductView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get(self.slug_url_kwarg), type__name = "Product")
        except Http404:
            return None
    
    def get_object(self):
        try:
            company_slug = self.kwargs.get(self.slug_url_kwarg)
            product_slug = self.kwargs.get('product_slug')

            return get_object_or_404(self.model, company__slug = company_slug, slug = product_slug)
        except Http404:
            return None
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company_page"] = True
        context["product_page"] = True        
        return context

class ListProductView(BaseProductView, ListView):
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
    

class AddProductView(BaseProductView, CreateView):
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
            context["add_product_page"] = True

            context["sizes"] = Size.objects.all()
            context["colors"] = Color.objects.all()
            context["units"] = sorted(["mm", "cm", "m"])
            current_company = self.get_current_company()

            context["categories"] = ProductCategory.objects.filter(company = current_company).values("slug", "name").order_by("name")
            context["sub_categories"] = ProductSubCategory.objects.filter(company = current_company).values("slug", "name").order_by("name")
            context["colors"] = Color.objects.filter(company = current_company).values("slug", "name", "hexa").order_by("name")
            context["sizes"] = Size.objects.filter(company = current_company).values("slug", "name").order_by("name")
            context["brands"] = Brand.objects.filter(company = current_company).values("slug", "name").order_by("name")            

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
    

class DeleteProductView(BaseProductView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            if not self.object:
                messages.error(request, "Invalid product")
                return redirect(self.get_redirect_url())
            
            self.object.delete()
            messages.success(request, "Success! Product Deleted")
            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(f"Error in post function of DeleteProductView of superadmin: {e}")
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
            context["product_categories_page"] = True        
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
            context["product_sub_categories_page"] = True
            current_company = self.get_current_company()
            context["categories"] = ProductCategory.objects.filter(company = current_company)
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
    

# Product FAQ
class ProductFaqBaseView(BaseProductCompanyView):
    model = ProductFaq
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:product_faqs', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseProductFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_current_company(self):
        try:
            company_slug = self.kwargs.get(self.slug_url_kwarg)            
            self.company = get_object_or_404(Company, slug = company_slug, type__name = "Product")
            return self.company
        except Http404:
            return None
        
    def get_product(self, product_slug):
        try:            
            return get_object_or_404(Product, slug = product_slug)
        except Http404:
            return None
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context["company_page"] = True
        context["product_faq_page"] = True

        return context


class AddProductFaqView(ProductFaqBaseView, CreateView):    
    fields = ["company", "product", "question", "answer", "dynamic_place_rendering"]
    template_name = "product_company/faqs/add.html"    

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_product_faq', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddProductFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        return self.get_success_url()        
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["add_product_faq_page"] = True
        context["categories"] = ProductCategory.objects.filter(company__slug = company_slug).order_by("name")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            product_slug = self.request.POST.get('product')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

            product_slug = product_slug.strip() if product_slug else None
            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Product": product_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            company = self.get_current_company()
            product = self.get_product(product_slug)

            if not company or not product:
                invalid_msg = ""
                
                if not company:
                    invalid_msg = "Invalid Product Company"
                else:
                    invalid_msg = "Invalid Product"

                messages.error(request, invalid_msg)
                return redirect(self.get_redirect_url())
            
            dynamic_place_rendering = True if dynamic_place_rendering else False

            ProductFaq.objects.update_or_create(
                company = company, product = product, question = question, dynamic_place_rendering = dynamic_place_rendering, 
                defaults={"answer": answer}
                )

            messages.success(request, "Success! Added FAQ")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in get function of AddProductFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class ListProductFaqView(ProductFaqBaseView, ListView):
    model = ProductFaq
    template_name = "product_company/faqs/list.html"
    queryset = model.objects.none()
    context_object_name = "faqs"

    def get_queryset(self):
        try:
            company_slug = self.kwargs.get(self.slug_url_kwarg)
            company = get_object_or_404(Company, slug = company_slug, type__name = "Product")
            return self.model.objects.filter(company = company)
            
        except Http404:
            messages.error(self.request, "Invalid product company")
            return redirect(self.redirect_url)


class UpdateProductFaqView(ProductFaqBaseView, UpdateView):
    model = ProductFaq
    fields = ["product", "question", "answer", "dynamic_place_rendering"]
    template_name = "product_company/faqs/update.html"
    context_object_name = "faq"

    def get_product(self, product_slug):
        try:
            return get_object_or_404(Product, slug = product_slug)
        except Http404:
            return None
        
    def get_object(self):
        company_slug = self.kwargs.get('slug') 
        product_faq_slug = self.kwargs.get('product_faq_slug') 

        self.object = get_object_or_404(ProductFaq, company__slug = company_slug, slug = product_faq_slug)

        return self.object
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["update_product_faq_page"] = True

        context["categories"] = ProductCategory.objects.filter(company__slug = company_slug).order_by("name")
        context["sub_categories"] = ProductSubCategory.objects.filter(company__slug = company_slug, category = self.object.product.category).order_by("name")
        context["products"] = Product.objects.filter(company__slug = company_slug, category = self.object.product.category, sub_category = self.object.product.sub_category).order_by("name")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            product_slug = self.request.POST.get('product')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Product": product_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            product = self.get_product(product_slug)

            if not product:
                messages.error(request, "Invalid Product")
                return redirect(self.get_redirect_url())
            
            dynamic_place_rendering = True if dynamic_place_rendering else False

            similar_faq = self.model.objects.filter(
                company = self.object.company, product = product, question = question, answer = answer, dynamic_place_rendering = dynamic_place_rendering
                ).first()

            if similar_faq:
                if similar_faq.slug == self.object.slug:
                    messages.warning(request, "No changes detected")
                else:
                    messages.warning(request, "Similar product FAQ already exists")
                return redirect(self.get_redirect_url())

            self.object.product = product
            self.object.question = question
            self.object.answer = answer
            self.object.dynamic_place_rendering = dynamic_place_rendering
            self.object.save()

            messages.success(request, f"Success! Updated FAQ")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid product FAQ object")

        except Exception as e:
            logger.exception(f"Error in get function of UpdateProductFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteProductFaqView(ProductFaqBaseView, View):
    model = ProductFaq
        
    def get_object(self):
        faq_slug = self.kwargs.get('product_faq_slug')
        company_slug = self.kwargs.get('slug')

        return get_object_or_404(self.model, slug = faq_slug, company__slug = company_slug)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            product_name = str(self.object.product.name)[:25]
            if len(str(self.object.product.name)) > 25:
                product_name += "..."
            self.object.delete()

            messages.success(request, f"Success! Removed product FAQ object of: {product_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Product FAQ")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteProductFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


# Product Review
class BaseProductReviewView(BaseProductCompanyView):
    model = ProductReview
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_current_company(self):
        try:
            self.company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            return self.company
        except Http404:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_review_page"] = context["company_page"] = True
        context["current_company"] = self.get_current_company()
        context["company_type_page"] = False
        return context
    
    def get_success_url(self):
        try:
            if self.slug_url_kwarg:
                return reverse_lazy("superadmin:product_reviews", kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of BaseProductReviewView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_object(self):
        company_slug = self.kwargs.get(self.slug_url_kwarg)
        product_review_slug = self.kwargs.get('product_review_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = product_review_slug)
    
    def get_product(self, product_slug):
        try:
            company = self.get_current_company()
            return get_object_or_404(Product, company = company, slug = product_slug)
        except Http404:
            return None
    

class AddProductReviewView(BaseProductReviewView, CreateView):    
    template_name = "product_company/reviews/add.html"
    fields = ["company", "product", "user", "review_by", "text", "rating", "order"]

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:add_product_reviews", kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of AddProductReviewView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["add_product_review_page"] = True
        context["ratings"] = list(range(1,6))

        context["categories"] = ProductCategory.objects.filter(company__slug = self.kwargs.get(self.slug_url_kwarg))
        
        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()

            product_slug = request.POST.get("product")
            review_by = request.POST.get("reviewed_by")
            text = request.POST.get("testimonial")
            rating = request.POST.get("rating", 5)
            order = request.POST.get("order", 0)

            product_slug = product_slug.strip() if product_slug else None
            review_by = review_by.strip() if review_by else None
            text = text.strip() if text else None
            rating = rating.strip() if rating else None
            order = order.strip() if order else None

            required_fields = {
                "Product": product_slug,
                "Review By": review_by,
                "Review Text": text,
                "Rating": rating,
                "Order": order 
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
                

            product = self.get_product(product_slug)

            if not product:
                messages.error(request, "Invalid Product")
                return redirect(self.get_redirect_url())                          
                                   
            
            self.model.objects.create(
                company = company, user = request.user, product = product, review_by = review_by,
                text = text, rating = rating, order = order
            )

            messages.success(request, "Success! Review Added")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddProductReviewView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
            return redirect(self.get_redirect_url())


class ProductReviewListView(BaseProductReviewView, ListView):
    template_name = "product_company/reviews/list.html"
    context_object_name = "reviews"
    queryset = ProductReview.objects.none()
    
    def get_queryset(self):
        company_slug = self.kwargs.get('slug')
        if company_slug:
            return self.model.objects.filter(company__slug = company_slug).order_by("order")
        
        return self.queryset
    

class UpdateProductReviewView(BaseProductReviewView, UpdateView):    
    fields = ["review_by", "product", "text", "rating", "order"]
    template_name = "product_company/reviews/update.html"
    slug_url_kwarg = 'slug'
        
    def get_redirect_url(self):
        try:
            return reverse_lazy("superadmin:update_product_review", kwargs = {"slug": self.kwargs.get('slug'), "product_review_slug": self.kwargs.get('product_review_slug')})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of AddProductReviewView of superadmin app: {e}")
        
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["update_review_page"] = True
        context["ratings"] = list(range(1,6))

        context["categories"] = ProductCategory.objects.filter(company = self.get_current_company()).order_by('name')
        context["sub_categories"] = ProductSubCategory.objects.filter(
            company = self.get_current_company(), category = self.object.product.category
            ).order_by('name')
        context["products"] = Product.objects.filter(
            company = self.get_current_company(), category = self.object.product.category, sub_category = self.object.product.sub_category
            ).order_by('name')
        
        return context    

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            review_by = request.POST.get("review_by")
            product_slug = request.POST.get("product")
            text = request.POST.get("text")
            rating = request.POST.get("rating", 5)
            order = request.POST.get("order", 0)

            review_by = review_by.strip() if review_by else None
            product_slug = product_slug.strip() if product_slug else None
            text = text.strip() if text else None
            rating = rating.strip() if rating else None
            order = order.strip() if order else None

            required_fields = {
                "Reviewer Name": review_by,
                "Product": product_slug,
                "Review Text": text,
                "Rating": rating,
                "Order": order 
            }

            for key, value in required_fields.items():                
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            product = self.get_product(product_slug)

            if not product:
                messages.error(request, "Invalid Product")
                return redirect(self.get_redirect_url())                
            
            similar_client = self.model.objects.filter(
                company = self.object.company, review_by = review_by, product = product
                ).first()

            if similar_client:
                dublicate_error_msg = ""

                if similar_client.slug == self.object.slug:
                    if not (order or text or rating):
                        dublicate_error_msg = "No changes detected"
                else:
                    dublicate_error_msg = "Similar review already exists"

                if dublicate_error_msg:
                    messages.warning(request, dublicate_error_msg)
                    return redirect(self.get_redirect_url())
            
            self.object.review_by = review_by
            self.object.product = product
            self.object.text = text
            self.object.rating = rating
            self.object.order = order            

            self.object.save()

            messages.success(request, "Success! Review Updated")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid Review")

        except Exception as e:
            logger.exception(f"Error in post function of UpdateProductReviewView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class DeleteProductReviewView(BaseProductReviewView, DeleteView):
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Review Deleted")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Review")

        except Exception as e:
            logger.exception(f"Error in delete function of DeleteProductReviewView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class BaseProductEnquiryView(BaseProductCompanyView, View):
    model = ProductEnquiry
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get(self.slug_url_kwarg))
        except Http404:
            messages.error(self.request, "Invalid Company")
            return self.redirect_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = self.get_current_company()
            context["product_enquiry_page"] = True

        except Exception as e:
            logger.exception(f"Error in getting context data of BaseProductEnquiryView: {e}")

        return context


class ListProductEnquiryView(BaseProductEnquiryView, ListView):
    queryset = ProductEnquiry.objects.none()
    context_object_name = "enquiries"
    template_name = "product_company/enquiries/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get(self.slug_url_kwarg))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListProductEnquiryView of superadmin: {e}")
            return self.queryset


class DeleteProductEnquiryView(BaseProductEnquiryView, View):
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:product_enquiries', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of DeleteProductEnquiryView of superadmin app: {e}")
            return self.success_url

    def get_redirect_url(self):
        return self.get_success_url()
            

    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(ProductEnquiry, company__slug = self.kwargs.get(self.slug_url_kwarg), slug = self.kwargs.get('enquiry_slug'))
            self.object.delete()

            messages.success(request, "Success! Delete Product Enquiry")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid Product Enquiry")
            return redirect(self.get_redirect_url())


class BaseProductDetailPageView(BaseProductCompanyView):
    model = ProductDetailPage
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["product_detail_page"] = True
            
            current_company = self.get_current_company()

            context["current_company"] = current_company

        except Exception as e:
            logger.exception(f"Error in getting context data of BaseProductDetailPageView of superadmin: {e}")
        
        return context
        
    def get_product(self, product_slug):
        try:
            return get_object_or_404(Product, slug = product_slug)
        except Http404:
            messages.error(self.request, "Invalid Product")
            return redirect(self.get_redirect_url())
        
    def get_current_product(self):
        try:
            product_slug = self.kwargs.get('product_slug')

            product =  get_object_or_404(Product, slug = product_slug)
            return product
        except Http404:
            messages.error(self.request, "Failed! Invalid Product")
            return redirect(self.redirect_url)

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:product_detail_pages', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseProductDetailPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseProductDetailPageView of superadmin: {e}")
            return self.redirect_url

    def get_object(self):
        try:
            current_company = self.get_current_company()
            current_product = self.get_current_product()

            return get_object_or_404(self.model, company = current_company, product = current_product)
        
        except Http404:
            messages.error(self.request, "Invalid product for this company")

        except Exception as e:
            logger.exception(f"Error in get_object function of BaseProductDetailPageView of superadmin: {e}")

        return redirect(self.get_redirect_url())
        
    def handle_features(self, request, company, product):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    ProductFeature.objects.filter(company = company, product = product).delete()

                    features = [ProductFeature(company=company, product=product, feature=feature) for feature in features_list]
                    ProductFeature.objects.bulk_create(features)

                    feature_objs = ProductFeature.objects.filter(company = company, product = product)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of BaseProductDetailPageView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, product):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")            
            
            initial = 0


            with transaction.atomic():
                ProductVerticalTab.objects.filter(company = company, product = product).delete()
                ProductVerticalBullet.objects.filter(company = company, product = product).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = ProductVerticalTab.objects.create(
                            company = company,
                            product = product,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [ProductVerticalBullet(
                                company = company, product = product, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                ProductVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = ProductVerticalBullet.objects.filter(company = company, product = product, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)

                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of BaseProductDetailPageView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, product):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")                        
            
            initial = 0


            with transaction.atomic():
                ProductHorizontalTab.objects.filter(company = company, product = product).delete()
                ProductHorizontalBullet.objects.filter(company = company, product = product).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = ProductHorizontalTab.objects.create(
                            company = company,
                            product = product,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:
                        
                            creating_horizontal_bullets = [ProductHorizontalBullet(
                                company = company, product = product, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                ProductHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = ProductHorizontalBullet.objects.filter(company = company, product = product, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tabs function of BaseProductDetailPageView: {e}")

        return []
    
    def handle_tables(self, request, company, product):
        try:
            product_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)


            with transaction.atomic():
                ProductTableData.objects.filter(company = company, product = product).delete()
                ProductTable.objects.filter(company = company, product = product).delete()

                for index, heading in enumerate(heading_list):
                    product_table = ProductTable.objects.create(
                        company = company, product = product, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [ProductTableData(
                            company = company, product = product,
                            heading = heading, data = data
                            ) for data in data_list_of_heading]

                    ProductTableData.objects.bulk_create(table_data_objs )

                    product_table_data_objs = ProductTableData.objects.filter(company = company, product = product, heading = heading)

                    product_table.datas.set(product_table_data_objs)

                    product_tables.append(product_table)

            return product_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_tables function of BaseProductDetailPageView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, product):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                ProductBulletPoint.objects.filter(company = company, product = product).delete()

                if bullet_point_list:
                    bullet_point_objects = [ProductBulletPoint(
                        company = company, product = product,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    ProductBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = ProductBulletPoint.objects.filter(company = company, product = product)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of BaseProductDetailPageView: {e}")

        return []

    def handle_tags(self, request, company, product):
        try:
            tag_list = [tag.strip() for tag in request.POST.getlist("tag")]            

            with transaction.atomic():
                ProductTag.objects.filter(company = company, product = product).delete()

                if tag_list:
                    creating_tags = [ProductTag(
                        company = company, product = product,
                        tag = tag
                        ) for tag in tag_list if tag]

                    ProductTag.objects.bulk_create(creating_tags)

                    product_tags = ProductTag.objects.filter(company = company, product = product)                

                    return product_tags

        except Exception as e:
            logger.exception(f"Error in handle_tags function of BaseProductDetailPageView: {e}")

        return []

    def handle_timelines(self, request, company, product):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                ProductTimeline.objects.filter(company = company, product = product).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [ProductTimeline(
                        company = company, product = product,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    ProductTimeline.objects.bulk_create(creating_timelines)

                    product_timelines = ProductTimeline.objects.filter(company = company, product = product)                
                                            
                    return product_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of BaseProductDetailPageView: {e}")

        return []


class AddProductDetailPageView(BaseProductDetailPageView, CreateView):
    form_class = ProductDetailDescriptionForm
    template_name = "product_company/detail_page/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["add_product_detail_page"] = True

        current_company = self.get_current_company()        
        context["categories"] = ProductCategory.objects.filter(company = current_company)

        context["tags"] = MetaTag.objects.all().order_by("name")
        
        return context

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_product_detail_page', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseProductDetailPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseProductDetailPageView of superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            product_slug = request.POST.get('product')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            buy_now_action = request.POST.get("buy_now_action")
            whatsapp = request.POST.get("whatsapp")
            external_link = request.POST.get("external_link")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")
            
            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")

            summary = summary.strip() if summary else None
            
            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None
            
            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            buy_now_action = buy_now_action.strip() if buy_now_action else None
            whatsapp = whatsapp.strip() if whatsapp else None
            external_link = external_link.strip() if external_link else None

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Product": product_slug,
                "summary": summary,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            buy_now_missing_field = ""
            if buy_now_action == "whatsapp" and not whatsapp:
                buy_now_missing_field = "Whatsapp Number"
            
            if buy_now_action == "external_link" and not external_link:
                buy_now_missing_field = "External Link"

            if buy_now_missing_field:
                messages.error(request, f"Failed! {buy_now_missing_field} is not provided")
                return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                }

            product = self.get_product(product_slug)

            with transaction.atomic():
                
                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                product_detail = self.model.objects.create(
                    company = company, product = product, summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    buy_now_action = buy_now_action, whatsapp = whatsapp, external_link = external_link,
                    vertical_title = vertical_title, horizontal_title = horizontal_title,
                    table_title = table_title, bullet_title = bullet_title, tag_title = tag_title, 
                    timeline_title = timeline_title
                )

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)

                product_detail.meta_tags.set(meta_tag_objs)           

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(product_detail, key, True)

                product_detail.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, product)
                    getattr(product_detail, field).set(objects)

                messages.success(request, "Success! Created product detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddProductDetailPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class ProductDetailPageListView(BaseProductDetailPageView, ListView):
    template_name = "product_company/detail_page/list.html"
    queryset = ProductDetailPage.objects.none()
    success_url = redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "detail_pages"        
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company)
        except Exception as e:
            logger.exception(f"Error in getting queryset of ProductDetailsListView of superadmin: {e}")
            return self.queryset


class ProductDetailPageView(BaseProductDetailPageView, DetailView):
    model = ProductDetailPage
    template_name = "product_company/detail_page/detail.html"
    redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "detail_page"

    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:product_detail_pages', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url function of ProductDetailPageView: {e}")
            return self.redirect_url


class UpdateProductDetailPageView(BaseProductDetailPageView, UpdateView):    
    form_class = ProductDetailDescriptionForm
    template_name = "product_company/detail_page/update.html"
    context_object_name = "detail_page"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object()
        current_company = self.get_current_company()        
        context["categories"] = ProductCategory.objects.filter(company = current_company)
        context["sub_categories"] = ProductSubCategory.objects.filter(company = current_company, category = self.object.product.category)
        context["products"] = Product.objects.filter(company = current_company, category = self.object.product.category, sub_category = self.object.product.sub_category)

        context["tags"] = MetaTag.objects.all().order_by("name")
        
        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:update_product_detail_page', kwargs = {"slug": self.kwargs.get('slug'), "product_slug": self.kwargs.get('product_slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateProductDetailPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateProductDetailPageView of superadmin: {e}")
            return self.redirect_url


    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            product_slug = request.POST.get('product')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            buy_now_action = request.POST.get("buy_now_action")
            whatsapp = request.POST.get("whatsapp")
            external_link = request.POST.get("external_link")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")   

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            buy_now_action = buy_now_action.strip() if buy_now_action else None
            whatsapp = whatsapp.strip() if whatsapp else None
            external_link = external_link.strip() if external_link else None

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")

            # Fetch current company
            company = self.get_current_company()

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Product": product_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            buy_now_missing_field = ""
            if buy_now_action == "whatsapp" and not whatsapp:
                buy_now_missing_field = "Whatsapp Number"
            
            if buy_now_action == "external_link" and not external_link:
                buy_now_missing_field = "External Link"

            if buy_now_missing_field:
                messages.error(request, f"Failed! {buy_now_missing_field} is not provided")
                return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                }

            product = self.get_product(product_slug)

            with transaction.atomic():

                product_detail = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                product_detail.product = product
                product_detail.summary = summary

                product_detail.description = description

                product_detail.meta_title = meta_title
                product_detail.meta_description = meta_description

                product_detail.buy_now_action = buy_now_action

                if buy_now_action == "whatsapp":
                    product_detail.whatsapp = whatsapp 

                if buy_now_action == "external_link":
                    product_detail.external_link = external_link 

                product_detail.vertical_title = vertical_title
                product_detail.horizontal_title = horizontal_title
                product_detail.table_title = table_title
                product_detail.bullet_title = bullet_title
                product_detail.tag_title = tag_title
                product_detail.timeline_title = timeline_title 

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)
                
                product_detail.meta_tags.set(meta_tag_objs)

                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:                    
                        assigning_value = True

                    setattr(product_detail, key, assigning_value)
                
                product_detail.save()                             

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, product)
                    getattr(product_detail, field).set(objects)

                product_detail.save()

                messages.success(request, "Success! Updated product detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateProductDetailPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())

class DeleteProductDetailPageView(BaseProductDetailPageView, View):
    def get_object(self, **kwargs):
        company_slug = self.kwargs.get('slug')
        detail_page_slug = self.kwargs.get('detail_page_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = detail_page_slug)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            product_name = self.object.product.name
            self.object.delete()

            messages.success(request, f"Success! Removed product detail page of: {product_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Product Detail")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteProductDetailPageView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class BaseProductMultiPageView(BaseProductCompanyView, View):
    model = ProductMultiPage
    success_url = redirect_url = reverse_lazy('superadmin:home')        
        
    def get_categories(self):
        return ProductCategory.objects.filter(company = self.current_company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["product_multipage"] = True
            
            self.current_company = self.get_current_company()
            
            context["current_company"] = self.current_company            
        except Exception as e:
            logger.exception(f"Error in getting context data of BaseProductMultiPageView of superadmin: {e}")
        
        return context    
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:product_multipages', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseProductMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseProductMultiPageView of superadmin: {e}")
            return self.redirect_url
        
    def get_product(self, product_slug):
        try:
            return get_object_or_404(Product, slug = product_slug)
        except Http404:
            messages.error(self.request, "Invalid Product")
            return redirect(self.get_redirect_url())
        
    def handle_features(self, request, company, product):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    ProductMultiPageFeature.objects.filter(company = company, product = product).delete()

                    features = [ProductMultiPageFeature(company=company, product=product, feature=feature) for feature in features_list]
                    ProductMultiPageFeature.objects.bulk_create(features)

                    feature_objs = ProductMultiPageFeature.objects.filter(company = company, product = product)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of BaseProductMultiPageView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, product):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")            
            
            initial = 0


            with transaction.atomic():
                ProductMultiPageVerticalTab.objects.filter(company = company, product = product).delete()
                ProductMultiPageVerticalBullet.objects.filter(company = company, product = product).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = ProductMultiPageVerticalTab.objects.create(
                            company = company,
                            product = product,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [ProductMultiPageVerticalBullet(
                                company = company, product = product, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                ProductMultiPageVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = ProductMultiPageVerticalBullet.objects.filter(company = company, product = product, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)


                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of BaseProductMultiPageView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, product):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")                        
            
            initial = 0


            with transaction.atomic():
                ProductMultiPageHorizontalTab.objects.filter(company = company, product = product).delete()
                ProductMultiPageHorizontalBullet.objects.filter(company = company, product = product).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = ProductMultiPageHorizontalTab.objects.create(
                            company = company,
                            product = product,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:
                        
                            creating_horizontal_bullets = [ProductMultiPageHorizontalBullet(
                                company = company, product = product, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                ProductMultiPageHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = ProductMultiPageHorizontalBullet.objects.filter(company = company, product = product, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tabs function of BaseProductMultiPageView: {e}")

        return []
    
    def handle_tables(self, request, company, product):
        try:
            product_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)


            with transaction.atomic():
                ProductMultiPageTableData.objects.filter(company = company, product = product).delete()
                ProductMultiPageTable.objects.filter(company = company, product = product).delete()

                for index, heading in enumerate(heading_list):
                    product_table = ProductMultiPageTable.objects.create(
                        company = company, product = product, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [ProductMultiPageTableData(
                            company = company, product = product,
                            heading = heading, data = data
                            ) for data in data_list_of_heading if data]

                    ProductMultiPageTableData.objects.bulk_create(table_data_objs )

                    product_table_data_objs = ProductMultiPageTableData.objects.filter(company = company, product = product, heading = heading)

                    product_table.datas.set(product_table_data_objs)
                    product_tables.append(product_table)

            return product_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_tables function of BaseProductMultiPageView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, product):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                ProductMultiPageBulletPoint.objects.filter(company = company, product = product).delete()

                if bullet_point_list:
                    bullet_point_objects = [ProductMultiPageBulletPoint(
                        company = company, product = product,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    ProductMultiPageBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = ProductMultiPageBulletPoint.objects.filter(company = company, product = product)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of BaseProductMultiPageView: {e}")

        return []

    def handle_tags(self, request, company, product):
        try:
            tag_list = [tag.strip() for tag in request.POST.getlist("tag")]            

            with transaction.atomic():
                ProductMultiPageTag.objects.filter(company = company, product = product).delete()

                if tag_list:                
                    creating_tags = [ProductMultiPageTag(
                        company = company, product = product,
                        tag = tag
                        ) for tag in tag_list if tag]

                    ProductMultiPageTag.objects.bulk_create(creating_tags)

                    product_tags = ProductMultiPageTag.objects.filter(company = company, product = product)                

                    return product_tags

        except Exception as e:
            logger.exception(f"Error in handle_tags function of BaseProductMultiPageView: {e}")

        return []

    def handle_timelines(self, request, company, product):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                ProductMultiPageTimeline.objects.filter(company = company, product = product).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [ProductMultiPageTimeline(
                        company = company, product = product,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    ProductMultiPageTimeline.objects.bulk_create(creating_timelines)

                    product_timelines = ProductMultiPageTimeline.objects.filter(company = company, product = product)                
                                            
                    return product_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of BaseProductMultiPageView: {e}")

        return []

    def handle_faqs(self, request, company, product):
        try:
            question_list = [question.strip() for question in request.POST.getlist("faq_question")]
            answer_list = [answer.strip() for answer in request.POST.getlist("faq_answer")]                        

            if len(question_list) != len(answer_list):
                raise ValueError("The number of questions does not match the number of summaries.")

            with transaction.atomic():
                ProductMultiPageFaq.objects.filter(company = company, product = product).delete()
                
                if question_list and answer_list:
                    creating_faqs = [ProductMultiPageFaq(
                        company = company, product = product,
                        question = question, answer = answer
                        ) for question, answer in zip(question_list, answer_list) if question and answer]

                    ProductMultiPageFaq.objects.bulk_create(creating_faqs)

                    product_faqs = ProductMultiPageFaq.objects.filter(company = company, product = product)                
                                            
                    return product_faqs
        except Exception as e:
            logger.exception(f"Error in handle_faqs function of BaseProductMultiPageView: {e}")

        return []


class AddProductMultiPageView(BaseProductMultiPageView, CreateView):
    form_class = ProductMultiPageDescriptionForm
    template_name = "product_company/multipage/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["categories"] = self.get_categories()
        context["tags"] = MetaTag.objects.all().order_by("name")

        return context

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_product_multipage', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddProductMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of AddProductMultiPageView of superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            current_company = self.get_current_company()

            form = self.get_form()

            product_slug = request.POST.get('product')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")

            buy_now_action = request.POST.get("buy_now_action")
            whatsapp = request.POST.get("whatsapp")
            external_link = request.POST.get("external_link")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None

            buy_now_action = buy_now_action.strip() if buy_now_action else None
            whatsapp = whatsapp.strip() if whatsapp else None
            external_link = external_link.strip() if external_link else None

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = current_company

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Product": product_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
                
            buy_now_missing_field = ""
            if buy_now_action == "whatsapp" and not whatsapp:
                buy_now_missing_field = "Whatsapp Number"
            
            if buy_now_action == "external_link" and not external_link:
                buy_now_missing_field = "External Link"

            if buy_now_missing_field:
                messages.error(request, f"Failed! {buy_now_missing_field} is not provided")
                return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }

            product = self.get_product(product_slug)

            with transaction.atomic():
                if self.model.objects.filter(company = company, product = product).exists():
                    messages.error(request, "Multipage for this product already exists")
                    return redirect(self.get_redirect_url())
                
                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                product_multi_page = self.model.objects.create(
                    company = company, product = product, summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    url_type = url_type, 
                    buy_now_action = buy_now_action, whatsapp = whatsapp, external_link = external_link,
                    vertical_title = vertical_title, horizontal_title = horizontal_title,
                    table_title = table_title, bullet_title = bullet_title, tag_title = tag_title, 
                    timeline_title = timeline_title
                )

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)

                product_multi_page.meta_tags.set(meta_tag_objs)  

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(product_multi_page, key, True)
                
                product_multi_page.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, product)
                    getattr(product_multi_page, field).set(objects)

                messages.success(request, "Success! Created product multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddProductMultiPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class ProductMultiPageListView(BaseProductMultiPageView, ListView):
    template_name = "product_company/multipage/list.html"
    queryset = ProductMultiPage.objects.none()
    context_object_name = "multipages"    
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company)
        except Exception as e:
            logger.exception(f"Error in getting queryset of ProductMultiPageListView of superadmin: {e}")
            return self.queryset
        
class ProductMultiPageDetailView(BaseProductMultiPageView, DetailView):
    template_name = "product_company/multipage/detail.html"
    context_object_name = "multipage"

    def get_object(self):
        try:
            current_company = self.get_current_company()
            current_product = self.get_current_product()
            return get_object_or_404(self.model, company = current_company, product = current_product)
        
        except Http404:
            messages.error(self.request, "Invalid product for this company")

        except Exception as e:
            logger.exception(f"Error in get_object function of ProductMultipageDetailView of superadmin: {e}")

        return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object
        
        context[self.context_object_name] = self.object
        return context
        
    def get_current_product(self):
        try:
            product_slug = self.kwargs.get('product_slug')
            return get_object_or_404(Product, slug = product_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Product")
            return redirect(self.redirect_url)        
    

class UpdateProductMultiPageView(BaseProductMultiPageView, UpdateView):    
    form_class = ProductMultiPageDescriptionForm
    template_name = "product_company/multipage/update.html"
    context_object_name = "multipage"    

    def get_object(self):
        try:
            company_slug = self.kwargs.get('slug')
            multipage_slug = self.kwargs.get('multipage_slug')            
            
            return get_object_or_404(self.model, company__slug = company_slug, slug = multipage_slug)
        
        except Http404:
            messages.error(self.request, "Invalid product multipage object")
            return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_current_company()
            self.object = self.get_object()
            context[self.context_object_name] = self.object

            context["categories"] = ProductCategory.objects.filter(company = current_company)
            context["sub_categories"] = ProductSubCategory.objects.filter(company = current_company, category = self.object.product.category)
            context["products"] = Product.objects.filter(company = current_company, sub_category = self.object.product.sub_category)
            context["tags"] = MetaTag.objects.all().order_by("name")
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateMultiPageView of superadmin: {e}")
        
        return context    
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:update_product_multipage', kwargs = {"slug": self.kwargs.get('slug'), "multipage_slug": self.kwargs.get('multipage_slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateMultiPageView of superadmin: {e}")
            return self.redirect_url
        
        
    def post(self, request, *args, **kwargs):
        try:            
            form = self.get_form()

            product_slug = request.POST.get('product')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")

            buy_now_action = request.POST.get("buy_now_action")
            whatsapp = request.POST.get("whatsapp")
            external_link = request.POST.get("external_link")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None
            
            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None

            buy_now_action = buy_now_action.strip() if buy_now_action else None
            whatsapp = whatsapp.strip() if whatsapp else None
            external_link = external_link.strip() if external_link else None

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Product": product_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            buy_now_missing_field = ""
            if buy_now_action == "whatsapp" and not whatsapp:
                buy_now_missing_field = "Whatsapp Number"
            
            if buy_now_action == "external_link" and not external_link:
                buy_now_missing_field = "External Link"

            if buy_now_missing_field:
                messages.error(request, f"Failed! {buy_now_missing_field} is not provided")
                return redirect(self.get_redirect_url())
                
            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }

            product = self.get_product(product_slug)

            with transaction.atomic():

                multipage = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                multipage.product = product
                multipage.summary = summary

                multipage.description = description

                multipage.meta_title = meta_title
                multipage.meta_description = meta_description

                multipage.url_type = url_type

                multipage.buy_now_action = buy_now_action

                if buy_now_action == "whatsapp":
                    multipage.whatsapp = whatsapp 

                if buy_now_action == "external_link":
                    multipage.external_link = external_link 

                multipage.vertical_title = vertical_title
                multipage.horizontal_title = horizontal_title
                multipage.table_title = table_title
                multipage.bullet_title = bullet_title
                multipage.tag_title = tag_title
                multipage.timeline_title = timeline_title                

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)
                
                multipage.meta_tags.set(meta_tag_objs)

                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:
                        assigning_value = True

                    setattr(multipage, key, assigning_value)
                
                multipage.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, product)
                    getattr(multipage, field).set(objects)

                multipage.save()

                messages.success(request, "Success! Updated product multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateCompanyDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteProductMultiPageView(BaseProductMultiPageView, View):
    def get_object(self, **kwargs):
        company_slug = self.kwargs.get('slug')
        multipage_slug = self.kwargs.get('multipage_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = multipage_slug)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            product_name = self.object.product.name
            self.object.delete()

            messages.success(request, f"Success! Removed product multipage of: {product_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Product Multipage")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteProductMultiPageView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

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
    fields = ["company", "image", "name", "program", "specialization", "mode", "duration", "price", "duration", "meta_tags", "meta_description", "subtitles"]
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
            return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)   
        
        try:
            context["course_page"] = True
            context["add_course_page"] = True

            current_company = self.get_current_company()

            context["programs"] = Program.objects.filter(company = current_company)
                
        except Exception as e:
            logger.exception(f"Error in getting context data of AddCourseView in superadmin app: {e}")

        return context
    
    def post(self, request, *args, **kwargs):        
        try:
            company = self.get_current_company()

            image = request.FILES.get('image')
            name = request.POST.get("name")
            program_slug = request.POST.get("program")
            specialization_slug = request.POST.get("specialization")
            mode = request.POST.get("mode")
            duration = request.POST.get("duration")
            price = request.POST.get("price")

            subtitles = request.POST.get("subtitles")
            meta_tags = request.POST.get("meta_tags")
            meta_description = request.POST.get("meta_description")

            name = name.strip() if name else None
            program_slug = program_slug.strip() if program_slug else None
            specialization_slug = specialization_slug.strip() if specialization_slug else None
            mode = mode.strip() if mode else None
            duration = duration.strip() if duration else None
            price = price.strip() if price else None
            subtitles = subtitles.strip() if subtitles else None
            meta_tags = meta_tags.strip() if meta_tags else None
            meta_description = meta_description.strip() if meta_description else None

            required_fields = {
                "Name": name,
                "Program": program,
                "Specialization": specialization,
                "Mode": mode,
                "Price": price,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url)

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
                company = company, image = image,
                name=name, program=program, specialization=specialization,
                mode=mode, duration=duration, price=price, subtitles = subtitles,
                meta_tags = meta_tags, meta_description = meta_description
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
    fields = ["image", "name", "program", "specialization", "mode", "duration", "price", "duration", "subtitles", "meta_tags", "meta_description"]   
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
            return redirect(self.get_redirect_url())

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
            image = request.FILES.get("image")

            name = request.POST.get("name")
            program_slug = request.POST.get("program")
            specialization_slug = request.POST.get("specialization")
            mode = request.POST.get("mode")
            duration = request.POST.get("duration")
            price = request.POST.get("price")
            description = request.POST.get("description")

            subtitles = request.POST.get("subtitles")
            meta_tags = request.POST.get("meta_tags")
            meta_description = request.POST.get("meta_description")

            name = name.strip() if name else None
            program_slug = program_slug.strip() if program_slug else None
            specialization_slug = specialization_slug.strip() if specialization_slug else None
            mode = mode.strip() if mode else None
            duration = duration.strip() if duration else None
            price = price.strip() if price else None
            description = description.strip() if description else None
            subtitles = subtitles.strip() if subtitles else None
            meta_tags = meta_tags.strip() if meta_tags else None
            meta_description = meta_description.strip() if meta_description else None

            required_fields = {
                "Name": name,
                "Program": program_slug,
                "Specialization": specialization_slug,
                "Mode": mode,
                "Price": price,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url)
                
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

            course = self.get_object()

            similar_course = self.model.objects.filter(
                company = course.company, name = name, program = program,
                specialization = specialization, mode = mode
                ).first()
            
            if similar_course:
                similar_msg = ""
                if similar_course.slug == self.object.slug:
                    if self.object.image == image and self.object.duration == duration and self.object.price == price and self.object.subtitles == subtitles and self.object.meta_tags == meta_tags and self.object.meta_description == meta_description:
                        similar_msg = "No Changes Detected"
                else:
                    similar_msg = "Similar course already exists"
                
                if similar_msg:
                    messages.warning(request, similar_msg)
                    return redirect(self.get_redirect_url())
            
            course.name = name
            course.program = program
            course.specialization = specialization
            course.mode = mode
            course.duration = duration
            course.price = price
            course.description = description
            course.subtitles = subtitles
            course.meta_tags = meta_tags
            course.meta_description = meta_description
            if image:
                course.image = image
            course.save()
            
            messages.success(request, "Success! Course updated.")
            return redirect(self.get_success_url())
            
        except Exception as e:
            logger.exception(f"Error in UpdateCourseView of superadmin app: {e}")
            messages.error(request, "An expected error occurred")

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
            messages.error(request, "Failed! An unexpected error occurred")

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
            return redirect(self.get_redirect_url())    

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
            messages.error(request, "An unexpected error occurred")

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
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

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
            messages.error(request, "An unexpected error occurred")

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
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    
# Course Detail
class AddCourseDetailView(BaseEducationCompanyView, CreateView):
    model = CourseDetail
    form_class = CourseDetailDescriptionForm
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

            context["tags"] = MetaTag.objects.all().order_by("name")

            context["programs"] = Program.objects.filter(company = current_company)
        except Exception as e:
            logger.exception(f"Error in getting context data of AddCourseDetailView of superadmin: {e}")
        
        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_course_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddCourseDetailView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of AddCourseDetailView of superadmin: {e}")
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

    def handle_vertical_tabs(self, request, company, course):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")            
            
            initial = 0


            with transaction.atomic():
                CourseVerticalTab.objects.filter(company = company, course = course).delete()
                CourseVerticalBullet.objects.filter(company = company, course = course).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = CourseVerticalTab.objects.create(
                            company = company,
                            course = course,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [CourseVerticalBullet(
                                company = company, course = course, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                CourseVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = CourseVerticalBullet.objects.filter(company = company, course = course, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)

                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of AddCourseDetailView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, course):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")                        
            
            initial = 0


            with transaction.atomic():
                CourseHorizontalTab.objects.filter(company = company, course = course).delete()
                CourseHorizontalBullet.objects.filter(company = company, course = course).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = CourseHorizontalTab.objects.create(
                            company = company,
                            course = course,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:
                        
                            creating_horizontal_bullets = [CourseHorizontalBullet(
                                company = company, course = course, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                CourseHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = CourseHorizontalBullet.objects.filter(company = company, course = course, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tabs function of AddCourseDetailView: {e}")

        return []
    
    def handle_tables(self, request, company, course):
        try:
            course_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)


            with transaction.atomic():
                CourseTableData.objects.filter(company = company, course = course).delete()
                CourseTable.objects.filter(company = company, course = course).delete()

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
            logger.exception(f"Error in handle_tables function of AddCourseDetailView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, course):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                CourseBulletPoint.objects.filter(company = company, course = course).delete()

                if bullet_point_list:
                    bullet_point_objects = [CourseBulletPoint(
                        company = company, course = course,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    CourseBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = CourseBulletPoint.objects.filter(company = company, course = course)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of AddCourseDetailView: {e}")

        return []

    def handle_tags(self, request, company, course):
        try:
            tag_list = [tag.strip() for tag in request.POST.getlist("tag")]            

            with transaction.atomic():
                CourseTag.objects.filter(company = company, course = course).delete()

                if tag_list:
                    creating_tags = [CourseTag(
                        company = company, course = course,
                        tag = tag
                        ) for tag in tag_list if tag]

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

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                CourseTimeline.objects.filter(company = company, course = course).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [CourseTimeline(
                        company = company, course = course,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    CourseTimeline.objects.bulk_create(creating_timelines)

                    course_timelines = CourseTimeline.objects.filter(company = company, course = course)                
                                            
                    return course_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of AddCourseDetailView: {e}")

        return []

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            course_slug = request.POST.get('course')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")

            hide_support_languages = request.POST.get("hide_support_languages")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company or company.type.name != "Education" :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Course": course_slug,
                "summary": summary,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
                
            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                }

            course = self.get_course(course_slug)

            with transaction.atomic():

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                course_detail = self.model.objects.create(
                    company = company, course = course, summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    vertical_title = vertical_title, horizontal_title = horizontal_title,
                    table_title = table_title, bullet_title = bullet_title, tag_title = tag_title, 
                    timeline_title = timeline_title, hide_support_languages = True if hide_support_languages else False
                )

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)

                course_detail.meta_tags.set(meta_tag_objs)

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(course_detail, key, True)

                course_detail.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, course)
                    getattr(course_detail, field).set(objects)

                messages.success(request, "Success! Created course detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddCompanyDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

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
    

class UpdateCourseDetailView(BaseEducationCompanyView, UpdateView):
    model = CourseDetail
    form_class = CourseDetailDescriptionForm
    template_name = "education_company/course_detail/update.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "course_detail"
    
    def get_current_company(self):
        try:
            company_slug = self.kwargs.get('slug')            
            return get_object_or_404(Company, slug = company_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Company")
            return redirect(self.redirect_url)
    
    def get_object(self):
        try:
            company_slug = self.kwargs.get('slug')
            course_detail_slug = self.kwargs.get('course_detail_slug')
            
            return get_object_or_404(CourseDetail, company__slug = company_slug, slug = course_detail_slug)
        
        except Http404:
            messages.error(self.request, "Invalid course detail object")
            return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_detail_page"] = True
            
            current_company = self.get_current_company()
            
            context["current_company"] = current_company 
            context["tags"] = MetaTag.objects.all().order_by("name")  

            self.object = self.get_object()         

            context["programs"] = Program.objects.filter(company = current_company)
            context["courses"] = Course.objects.filter(company = current_company, program = self.object.course.program)
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateCourseDetailView of superadmin: {e}")
        
        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:update_course_details', kwargs = {"slug": self.kwargs.get('slug'), "course_detail_slug": self.kwargs.get('course_detail_slug')})
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
            logger.exception(f"Error in handle_features function of UpdateCourseDetailView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, course):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")

            initial = 0

            with transaction.atomic():
                CourseVerticalTab.objects.filter(company = company, course = course).delete()
                CourseVerticalBullet.objects.filter(company = company, course = course).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = CourseVerticalTab.objects.create(
                            company = company,
                            course = course,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )                    

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [CourseVerticalBullet(
                                company = company, course = course, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                CourseVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = CourseVerticalBullet.objects.filter(company = company, course = course, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)

                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of UpdateCourseDetailView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, course):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")

            initial = 0

            with transaction.atomic():
                CourseHorizontalTab.objects.filter(company = company, course = course).delete()
                CourseHorizontalBullet.objects.filter(company = company, course = course).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = CourseHorizontalTab.objects.create(
                            company = company,
                            course = course,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:

                            creating_horizontal_bullets = [CourseHorizontalBullet(
                                company = company, course = course, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                CourseHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = CourseHorizontalBullet.objects.filter(company = company, course = course, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)                                        

            return horizontal_tab_objects

        except Exception as e:
            logger.exception(f"Error in handle_horizontal_tabs function of UpdateCourseDetailView: {e}")

        return []
    
    def handle_tables(self, request, company, course):
        try:
            course_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)

            with transaction.atomic():
                CourseTableData.objects.filter(company = company, course = course).delete()
                CourseTable.objects.filter(company = company, course = course).delete()

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
            logger.exception(f"Error in handle_tables function of UpdateCourseDetailView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, course):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                CourseBulletPoint.objects.filter(company = company, course = course).delete()

                if bullet_point_list:
                    bullet_point_objects = [CourseBulletPoint(
                        company = company, course = course,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    CourseBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = CourseBulletPoint.objects.filter(company = company, course = course)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of UpdateCourseDetailView: {e}")

        return []

    def handle_tags(self, request, company, course):
        try:
            tag_list = [tag.strip() for tag in request.POST.getlist("tag")]            

            with transaction.atomic():
                CourseTag.objects.filter(company = company, course = course).delete()

                if tag_list:
                    creating_tags = [CourseTag(
                        company = company, course = course,
                        tag = tag
                        ) for tag in tag_list if tag]

                    CourseTag.objects.bulk_create(creating_tags)

                    course_tags = CourseTag.objects.filter(company = company, course = course)                

                    return course_tags

        except Exception as e:
            logger.exception(f"Error in handle_tags function of UpdateCourseDetailView: {e}")

        return []

    def handle_timelines(self, request, company, course):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                CourseTimeline.objects.filter(company = company, course = course).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [CourseTimeline(
                        company = company, course = course,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    CourseTimeline.objects.bulk_create(creating_timelines)

                    course_timelines = CourseTimeline.objects.filter(company = company, course = course)

                    return course_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of UpdateCourseDetailView: {e}")

        return []
        
    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            course_slug = request.POST.get('course')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")
            
            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title") 

            hide_support_languages = request.POST.get("hide_support_languages")  

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")

            # Fetch current company
            company = self.get_current_company()

            if not company or company.type.name != "Education" :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Course": course_slug,
                "summary": summary,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                }

            course = self.get_course(course_slug)

            with transaction.atomic():

                course_detail = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                course_detail.course = course
                course_detail.summary = summary

                course_detail.description = description

                course_detail.meta_title = meta_title
                course_detail.meta_description = meta_description

                course_detail.vertical_title = vertical_title
                course_detail.horizontal_title = horizontal_title
                course_detail.table_title = table_title
                course_detail.bullet_title = bullet_title
                course_detail.tag_title = tag_title
                course_detail.timeline_title = timeline_title

                course_detail.hide_support_languages = True if hide_support_languages else False

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)
                
                course_detail.meta_tags.set(meta_tag_objs)
                
                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:                    
                        assigning_value = True

                    setattr(course_detail, key, assigning_value)
                
                course_detail.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, course)
                    getattr(course_detail, field).set(objects)

                course_detail.save()

                messages.success(request, "Success! Updated course detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateCompanyDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())



class DeleteCourseDetailView(BaseEducationCompanyView, View):
    model = CourseDetail
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:course_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of DeleteCourseDetailView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of DeleteCourseDetailView of superadmin: {e}")
            return self.redirect_url
        
    def get_object(self):
        course_slug = self.kwargs.get('course_detail_slug')
        company_slug = self.kwargs.get('slug')

        return get_object_or_404(self.model, slug = course_slug, company__slug = company_slug)

    def get(self, request, *args, **kwargs):
        try:
            course_detail = self.get_object()
            course_name = course_detail.course.name
            course_detail.delete()

            messages.success(request, f"Success! Removed course detail page of: {course_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Course Detail")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteCourseDetailView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())

class AddCourseFaqView(BaseEducationCompanyView, CreateView):
    model = CourseFaq
    fields = ["company", "dynamic_place_rendering", "course", "question", "answer"]
    template_name = "education_company/course_faqs/add.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_course_faq', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddCourseFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of AddCourseFaqView of superadmin: {e}")
            return self.redirect_url
        
    def get_current_company(self):
        try:
            company_slug = self.kwargs.get('slug')            
            return get_object_or_404(Company, slug = company_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Company")
            return redirect(self.redirect_url)

    def get_course(self, course_slug):
        try:
            
            return get_object_or_404(Course, slug = course_slug)
        except Http404:
            messages.error(self.request, "Invalid Course")
            return redirect(self.get_redirect_url())
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["course_faq_page"] = context["add_course_faq_page"] = True
        context["programs"] = Program.objects.filter(company__slug = company_slug).order_by("name")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            course_slug = self.request.POST.get('course')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Course": course_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            company = self.get_current_company()
            course = self.get_course(course_slug)

            dynamic_place_rendering = True if dynamic_place_rendering else False

            CourseFaq.objects.update_or_create(company = company, course = course, question = question, dynamic_place_rendering = dynamic_place_rendering, defaults={"answer": answer})

            messages.success(request, f"Success! Created FAQ object for course: {course.name}")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in get function of AddCourseFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class UpdateCourseFaqView(BaseEducationCompanyView, UpdateView):
    model = CourseFaq
    fields = ["course", "dynamic_place_rendering", "question", "answer"]
    template_name = "education_company/course_faqs/update.html"
    success_url = redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "faq"

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:update_course_faq', kwargs = {"slug": self.kwargs.get('slug'), "course_faq_slug": self.kwargs.get('course_faq_slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateCourseFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateCourseFaqView of superadmin: {e}")
            return self.redirect_url

    def get_course(self, course_slug):
        try:
            
            return get_object_or_404(Course, slug = course_slug)
        except Http404:
            messages.error(self.request, "Invalid Course")
            return redirect(self.get_redirect_url())
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["course_faq_page"] = context["update_course_faq_page"] = True
        context["programs"] = Program.objects.filter(company__slug = company_slug).order_by("name")

        return context
    
    def get_object(self):
        company_slug = self.kwargs.get('slug') 
        course_faq_slug = self.kwargs.get('course_faq_slug') 

        return get_object_or_404(CourseFaq, company__slug = company_slug, slug = course_faq_slug)
        
    def post(self, request, *args, **kwargs):
        try:
            faq = self.get_object()

            course_slug = self.request.POST.get('course')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Course": course_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            course = self.get_course(course_slug)

            dynamic_place_rendering = True if dynamic_place_rendering else False

            similar_faq = self.model.objects.filter(
                company = faq.company, course = course, question = question, answer = answer, dynamic_place_rendering = dynamic_place_rendering
                ).first()

            if similar_faq:
                if similar_faq.slug == faq.slug:
                    messages.warning(request, "No changes detected")
                else:
                    messages.warning(request, "Similar course FAQ already exists")
                return redirect(self.get_redirect_url())

            faq.course = course
            faq.question = question
            faq.answer = answer
            faq.dynamic_place_rendering = dynamic_place_rendering
            faq.save()

            messages.success(request, f"Success! Updated FAQ")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid course FAQ object")

        except Exception as e:
            logger.exception(f"Error in get function of UpdateCourseFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteCourseFaqView(BaseEducationCompanyView, View):
    model = CourseFaq
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:course_faqs', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of DeleteCourseFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of DeleteCourseFaqView of superadmin: {e}")
            return self.redirect_url
        
    def get_object(self):
        faq_slug = self.kwargs.get('course_faq_slug')
        company_slug = self.kwargs.get('slug')

        return get_object_or_404(self.model, slug = faq_slug, company__slug = company_slug)

    def get(self, request, *args, **kwargs):
        try:
            faq = self.get_object()
            course_name = faq.course.name
            faq.delete()

            messages.success(request, f"Success! Removed course FAQ object of: {course_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Course FAQ")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteCourseFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class ListCourseFaqView(BaseEducationCompanyView, ListView):
    model = CourseFaq
    template_name = "education_company/course_faqs/list.html"
    queryset = model.objects.none()
    context_object_name = "faqs"
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["course_faq_page"] = True

        return context

    def get_queryset(self):
        try:
            company_slug = self.kwargs.get('slug')
            company = get_object_or_404(Company, slug = company_slug, type__name = "Education")
            return self.model.objects.filter(company = company)
            
        except Http404:
            messages.error(self.request, "Invalid educational company")
            return redirect(self.redirect_url)           


class BaseCourseEnquiryView(BaseEducationCompanyView, View):
    model = CourseEnquiry
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get(self.slug_url_kwarg))
        except Http404:
            messages.error(self.request, "Invalid Company")
            return self.redirect_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = self.get_current_company()
            context["education_enquiry_page"] = True

        except Exception as e:
            logger.exception(f"Error in getting context data of BaseCourseEnquiryView: {e}")

        return context

class ListCourseEnquiryView(BaseCourseEnquiryView, ListView):
    queryset = CourseEnquiry.objects.none()
    context_object_name = "enquiries"
    template_name = "education_company/enquiries/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get(self.slug_url_kwarg))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListCourseEnquiryView of superadmin: {e}")
            return self.queryset


class DeleteCourseEnquiryView(BaseCourseEnquiryView, View):
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:course_enquiries', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of DeleteCourseEnquiryView of superadmin app: {e}")
            return self.success_url

    def get_redirect_url(self):
        return self.get_success_url()
            

    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(CourseEnquiry, company__slug = self.kwargs.get(self.slug_url_kwarg), slug = self.kwargs.get('enquiry_slug'))
            self.object.delete()

            messages.success(request, "Success! Delete Course Enquiry")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid Course Enquiry")
            return redirect(self.get_redirect_url())


class BaseCourseMultiPageView(BaseEducationCompanyView, View):
    model = CourseMultiPage
    success_url = redirect_url = reverse_lazy('superadmin:home')    

    def get_current_company(self):
        try:
            company_slug = self.kwargs.get('slug')            
            return get_object_or_404(Company, slug = company_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Company")
            return redirect(self.redirect_url)
        
    def get_programs(self):
        return Program.objects.filter(company = self.current_company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["course_multipage"] = True
            
            self.current_company = self.get_current_company()
            
            context["current_company"] = self.current_company            
        except Exception as e:
            logger.exception(f"Error in getting context data of BaseCourseMultiPageView of superadmin: {e}")
        
        return context    
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:course_multipages', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseCourseMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseCourseMultiPageView of superadmin: {e}")
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

                    CourseMultiPageFeature.objects.filter(company = company, course = course).delete()

                    features = [CourseMultiPageFeature(company=company, course=course, feature=feature) for feature in features_list]
                    CourseMultiPageFeature.objects.bulk_create(features)

                    feature_objs = CourseMultiPageFeature.objects.filter(company = company, course = course)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of BaseCourseMultiPageView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, course):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")            
            
            initial = 0


            with transaction.atomic():
                CourseMultiPageVerticalTab.objects.filter(company = company, course = course).delete()
                CourseMultiPageVerticalBullet.objects.filter(company = company, course = course).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = CourseMultiPageVerticalTab.objects.create(
                            company = company,
                            course = course,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [CourseMultiPageVerticalBullet(
                                company = company, course = course, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                CourseMultiPageVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = CourseMultiPageVerticalBullet.objects.filter(company = company, course = course, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)


                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of BaseCourseMultiPageView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, course):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")                        
            
            initial = 0


            with transaction.atomic():
                CourseMultiPageHorizontalTab.objects.filter(company = company, course = course).delete()
                CourseMultiPageHorizontalBullet.objects.filter(company = company, course = course).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = CourseMultiPageHorizontalTab.objects.create(
                            company = company,
                            course = course,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:
                        
                            creating_horizontal_bullets = [CourseMultiPageHorizontalBullet(
                                company = company, course = course, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                CourseMultiPageHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = CourseMultiPageHorizontalBullet.objects.filter(company = company, course = course, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tabs function of BaseCourseMultiPageView: {e}")

        return []
    
    def handle_tables(self, request, company, course):
        try:
            course_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)


            with transaction.atomic():
                CourseMultiPageTableData.objects.filter(company = company, course = course).delete()
                CourseMultiPageTable.objects.filter(company = company, course = course).delete()

                for index, heading in enumerate(heading_list):
                    course_table = CourseMultiPageTable.objects.create(
                        company = company, course = course, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [CourseMultiPageTableData(
                            company = company, course = course,
                            heading = heading, data = data
                            ) for data in data_list_of_heading if data]

                    CourseMultiPageTableData.objects.bulk_create(table_data_objs )

                    course_table_data_objs = CourseMultiPageTableData.objects.filter(company = company, course = course, heading = heading)

                    course_table.datas.set(course_table_data_objs)
                    course_tables.append(course_table)

            return course_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_tables function of BaseCourseMultiPageView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, course):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                CourseMultiPageBulletPoint.objects.filter(company = company, course = course).delete()

                if bullet_point_list:
                    bullet_point_objects = [CourseMultiPageBulletPoint(
                        company = company, course = course,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    CourseMultiPageBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = CourseMultiPageBulletPoint.objects.filter(company = company, course = course)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of BaseCourseMultiPageView: {e}")

        return []

    def handle_tags(self, request, company, course):
        try:
            tag_list = [tag.strip() for tag in request.POST.getlist("tag")]            

            with transaction.atomic():
                CourseMultiPageTag.objects.filter(company = company, course = course).delete()

                if tag_list:                
                    creating_tags = [CourseMultiPageTag(
                        company = company, course = course,
                        tag = tag
                        ) for tag in tag_list if tag]

                    CourseMultiPageTag.objects.bulk_create(creating_tags)

                    course_tags = CourseMultiPageTag.objects.filter(company = company, course = course)                

                    return course_tags

        except Exception as e:
            logger.exception(f"Error in handle_tags function of BaseCourseMultiPageView: {e}")

        return []

    def handle_timelines(self, request, company, course):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                CourseMultiPageTimeline.objects.filter(company = company, course = course).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [CourseMultiPageTimeline(
                        company = company, course = course,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    CourseMultiPageTimeline.objects.bulk_create(creating_timelines)

                    course_timelines = CourseMultiPageTimeline.objects.filter(company = company, course = course)                
                                            
                    return course_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of BaseCourseMultiPageView: {e}")

        return []

    def handle_faqs(self, request, company, course):
        try:
            question_list = [question.strip() for question in request.POST.getlist("faq_question")]
            answer_list = [answer.strip() for answer in request.POST.getlist("faq_answer")]                        

            if len(question_list) != len(answer_list):
                raise ValueError("The number of questions does not match the number of summaries.")

            with transaction.atomic():
                CourseMultiPageFaq.objects.filter(company = company, course = course).delete()
                
                if question_list and answer_list:
                    creating_faqs = [CourseMultiPageFaq(
                        company = company, course = course,
                        question = question, answer = answer
                        ) for question, answer in zip(question_list, answer_list) if question and answer]

                    CourseMultiPageFaq.objects.bulk_create(creating_faqs)

                    course_faqs = CourseMultiPageFaq.objects.filter(company = company, course = course)                
                                            
                    return course_faqs
        except Exception as e:
            logger.exception(f"Error in handle_faqs function of BaseCourseMultiPageView: {e}")

        return []


class AddCourseMultiPageView(BaseCourseMultiPageView, CreateView):
    form_class = CourseMultiPageDescriptionForm
    template_name = "education_company/multipage/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["programs"] = self.get_programs()
        context["tags"] = MetaTag.objects.all().order_by("name")

        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_course_multipage', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseCourseMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseCourseMultiPageView of superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            current_company = self.get_current_company()
            form = self.get_form()

            course_slug = request.POST.get('course')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None
            
            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = current_company

            if not company or company.type.name != "Education" :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Course": course_slug,
                "summary": summary,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }

            course = self.get_course(course_slug)

            updating_meta_tags = []
            with transaction.atomic():
                if self.model.objects.filter(company = company, course = course).exists():
                    messages.error(request, "Multipage for this course already exists")
                    return redirect(self.get_redirect_url())

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                course_multi_page = self.model.objects.create(
                    company = company, course = course, summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    url_type = url_type,
                    vertical_title = vertical_title, horizontal_title = horizontal_title,
                    table_title = table_title, bullet_title = bullet_title, tag_title = tag_title, 
                    timeline_title = timeline_title
                )             

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(course_multi_page, key, True)
                
                course_multi_page.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, course)
                    getattr(course_multi_page, field).set(objects)

                if course_multi_page:
                    if meta_tags:
                        meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                        course_multi_page.meta_tags.set(meta_tag_objects)

                messages.success(request, "Success! Created course multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddCourseMultiPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class CourseMultiPageListView(BaseCourseMultiPageView, ListView):
    template_name = "education_company/multipage/list.html"
    queryset = CourseMultiPage.objects.none()
    context_object_name = "multipages"    
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company)
        except Exception as e:
            logger.exception(f"Error in getting queryset of CourseMultiPageListView of superadmin: {e}")
            return self.queryset
        
class CourseMultiPageDetailView(BaseCourseMultiPageView, DetailView):
    template_name = "education_company/multipage/detail.html"
    context_object_name = "multipage"

    def get_object(self):
        try:
            current_company = self.get_current_company()
            current_course = self.get_current_course()
            return get_object_or_404(self.model, company = current_company, course = current_course)
        
        except Http404:
            messages.error(self.request, "Invalid course for this company")

        except Exception as e:
            logger.exception(f"Error in get_object function of CourseMultipageDetailView of superadmin: {e}")

        return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object
        
        context[self.context_object_name] = self.object
        return context
        
    def get_current_course(self):
        try:
            course_slug = self.kwargs.get('course_slug')
            return get_object_or_404(Course, slug = course_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Course")
            return redirect(self.redirect_url)        
    

class UpdateCourseMultiPageView(BaseCourseMultiPageView, UpdateView):    
    form_class = CourseMultiPageDescriptionForm
    template_name = "education_company/multipage/update.html"
    context_object_name = "multipage"    

    def get_object(self):
        try:
            company_slug = self.kwargs.get('slug')
            multipage_slug = self.kwargs.get('multipage_slug')            
            
            return get_object_or_404(self.model, company__slug = company_slug, slug = multipage_slug)
        
        except Http404:
            messages.error(self.request, "Invalid course multipage object")
            return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_current_company()
            self.object = self.get_object()
            context[self.context_object_name] = self.object

            context["programs"] = Program.objects.filter(company = current_company)
            context["courses"] = Course.objects.filter(company = current_company, program = self.object.course.program)
            context["tags"] = MetaTag.objects.all().order_by("name")
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateMultiPageView of superadmin: {e}")
        
        return context    
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:update_course_multipage', kwargs = {"slug": self.kwargs.get('slug'), "multipage_slug": self.kwargs.get('multipage_slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateMultiPageView of superadmin: {e}")
            return self.redirect_url
        
        
    def post(self, request, *args, **kwargs):
        try:            
            form = self.get_form()

            course_slug = request.POST.get('course')

            summary = request.POST.get("summary")
            
            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company or company.type.name != "Education" :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Course": course_slug,
                "summary": summary,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
                
            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }

            course = self.get_course(course_slug)

            updating_meta_tags = []
            with transaction.atomic():

                multipage = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                multipage.course = course
                multipage.summary = summary

                multipage.description = description

                multipage.meta_title = meta_title
                multipage.meta_description = meta_description

                multipage.url_type = url_type

                multipage.vertical_title = vertical_title
                multipage.horizontal_title = horizontal_title
                multipage.table_title = table_title
                multipage.bullet_title = bullet_title
                multipage.tag_title = tag_title
                multipage.timeline_title = timeline_title                

                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:
                        assigning_value = True

                    setattr(multipage, key, assigning_value)
                
                multipage.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, course)
                    getattr(multipage, field).set(objects)

                multipage.save()

                meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                multipage.meta_tags.set(meta_tag_objects)

                messages.success(request, "Success! Updated course multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateCompanyDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteCourseMultiPageView(BaseCourseMultiPageView, View):
    def get_object(self):
        multipage_slug = self.kwargs.get('multipage_slug')
        company_slug = self.kwargs.get('slug')

        return get_object_or_404(self.model, slug = multipage_slug, company__slug = company_slug)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            course_name = self.object.course.name
            self.object.delete()

            messages.success(request, f"Success! Removed course multipage of: {course_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Course Multipage")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteCourseMultiPageView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


# Service Company
class BaseServiceCompanyView(AdminBaseView, View):
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get('slug'), type__name = "Service")
        except Http404:
            messages.error(self.request, "Invalid company")
            return redirect(self.redirect_url)
    
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
            context["categories"] = ServiceCategory.objects.filter(company = self.get_current_company()).order_by("name")
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
            messages.error(request, "An unexpected error occurred")
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
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())


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
            messages.error(request, "An unexpected error occurred")

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
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

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
            context["categories"] = ServiceCategory.objects.filter(company = self.get_current_company).order_by('name')

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
            messages.error(request, "Invalid service category")                                    
        
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
            messages.error(request, "An unexpected error occurred")

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
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    
# Service FAQ
class ServiceFaqBaseView(BaseServiceCompanyView):
    model = ServiceFaq
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:service_faqs', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseServiceFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_current_company(self):
        try:
            company_slug = self.kwargs.get(self.slug_url_kwarg)            
            self.company = get_object_or_404(Company, slug = company_slug, type__name = "Service")
            return self.company
        except Http404:
            return None
        
    def get_service(self, service_slug):
        try:            
            return get_object_or_404(Service, slug = service_slug)
        except Http404:
            return None
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context["service_faq_page"] = True

        return context


class AddServiceFaqView(ServiceFaqBaseView, CreateView):    
    fields = ["company", "service", "question", "answer", "dynamic_place_rendering"]
    template_name = "service_company/faqs/add.html"    

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_service_faq', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddServiceFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        return self.get_success_url()        
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["add_service_faq_page"] = True
        context["categories"] = ServiceCategory.objects.filter(company__slug = company_slug).order_by("name")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            service_slug = self.request.POST.get('service')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

            service_slug = service_slug.strip() if service_slug else None
            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Service": service_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            company = self.get_current_company()
            service = self.get_service(service_slug)

            if not company or not service:
                invalid_msg = ""
                
                if not company:
                    invalid_msg = "Invalid Service Company"
                else:
                    invalid_msg = "Invalid Service"

                messages.error(request, invalid_msg)
                return redirect(self.get_redirect_url())
            
            dynamic_place_rendering = True if dynamic_place_rendering else False

            ServiceFaq.objects.update_or_create(
                company = company, service = service, question = question, dynamic_place_rendering = dynamic_place_rendering, 
                defaults={"answer": answer}
                )

            messages.success(request, f"Success! Created FAQ object for service: {service.name}")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in get function of AddServiceFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class ListServiceFaqView(ServiceFaqBaseView, ListView):
    model = ServiceFaq
    template_name = "service_company/faqs/list.html"
    queryset = model.objects.none()
    context_object_name = "faqs"

    def get_queryset(self):
        try:
            company_slug = self.kwargs.get(self.slug_url_kwarg)
            company = get_object_or_404(Company, slug = company_slug, type__name = "Service")
            return self.model.objects.filter(company = company)
            
        except Http404:
            messages.error(self.request, "Invalid service company")
            return redirect(self.redirect_url)


class UpdateServiceFaqView(ServiceFaqBaseView, UpdateView):
    model = ServiceFaq
    fields = ["service", "question", "answer", "dynamic_place_rendering"]
    template_name = "service_company/faqs/update.html"
    context_object_name = "faq"

    def get_service(self, service_slug):
        try:
            return get_object_or_404(Service, slug = service_slug)
        except Http404:
            return None
        
    def get_object(self):
        company_slug = self.kwargs.get('slug') 
        service_faq_slug = self.kwargs.get('service_faq_slug') 

        self.object = get_object_or_404(ServiceFaq, company__slug = company_slug, slug = service_faq_slug)

        return self.object
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["update_service_faq_page"] = True

        context["categories"] = ServiceCategory.objects.filter(company__slug = company_slug).order_by("name")
        context["sub_categories"] = ServiceSubCategory.objects.filter(company__slug = company_slug, category = self.object.service.category).order_by("name")
        context["services"] = Service.objects.filter(company__slug = company_slug, category = self.object.service.category, sub_category = self.object.service.sub_category).order_by("name")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            service_slug = self.request.POST.get('service')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Service": service_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            service = self.get_service(service_slug)

            if not service:
                messages.error(request, "Invalid Service")
                return redirect(self.get_redirect_url())

            dynamic_place_rendering = True if dynamic_place_rendering else False

            similar_faq = self.model.objects.filter(
                company = self.object.company, service = service, question = question, answer = answer, dynamic_place_rendering = dynamic_place_rendering
                ).first()

            if similar_faq:
                if similar_faq.slug == self.object.slug:
                    messages.warning(request, "No changes detected")
                else:
                    messages.warning(request, "Similar service FAQ already exists")
                return redirect(self.get_redirect_url())

            self.object.service = service
            self.object.question = question
            self.object.answer = answer
            self.object.dynamic_place_rendering = dynamic_place_rendering
            self.object.save()

            messages.success(request, f"Success! Updated FAQ")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid service FAQ object")

        except Exception as e:
            logger.exception(f"Error in get function of UpdateServiceFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteServiceFaqView(ServiceFaqBaseView, View):
    model = ServiceFaq
        
    def get_object(self):
        faq_slug = self.kwargs.get('service_faq_slug')
        company_slug = self.kwargs.get('slug')

        return get_object_or_404(self.model, slug = faq_slug, company__slug = company_slug)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            service_name = self.object.service.name
            self.object.delete()

            messages.success(request, f"Success! Removed service FAQ object of: {service_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Service FAQ")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteServiceFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class BaseServiceEnquiryView(BaseServiceCompanyView, View):
    model = ServiceEnquiry
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get(self.slug_url_kwarg))
        except Http404:
            messages.error(self.request, "Invalid Company")
            return self.redirect_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = self.get_current_company()
            context["service_enquiry_page"] = True

        except Exception as e:
            logger.exception(f"Error in getting context data of BaseServiceEnquiryView: {e}")

        return context

class ListServiceEnquiryView(BaseServiceEnquiryView, ListView):
    queryset = ServiceEnquiry.objects.none()
    context_object_name = "enquiries"
    template_name = "service_company/enquiries/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get(self.slug_url_kwarg))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListServiceEnquiryView of superadmin: {e}")
            return self.queryset


class DeleteServiceEnquiryView(BaseServiceEnquiryView, View):
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:service_enquiries', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of DeleteServiceEnquiryView of superadmin app: {e}")
            return self.success_url

    def get_redirect_url(self):
        return self.get_success_url()
            

    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(ServiceEnquiry, company__slug = self.kwargs.get(self.slug_url_kwarg), slug = self.kwargs.get('enquiry_slug'))
            self.object.delete()

            messages.success(request, "Success! Delete Service Enquiry")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid Service Enquiry")
            return redirect(self.get_redirect_url())


# Service Detail
class BaseServiceDetailView(BaseServiceCompanyView):
    model = ServiceDetail
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["service_detail_page"] = True
            
            current_company = self.get_current_company()

            context["current_company"] = current_company

        except Exception as e:
            logger.exception(f"Error in getting context data of BaseServiceDetailView of superadmin: {e}")
        
        return context    

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:service_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseServiceDetailView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseServiceDetailView of superadmin: {e}")
            return self.redirect_url
        
    def get_service(self, service_slug):
        try:
            return get_object_or_404(Service, slug = service_slug)
        except Http404:
            messages.error(self.request, "Invalid Service")
            return redirect(self.get_redirect_url())
        
    def get_current_service(self):
        try:
            service_slug = self.kwargs.get('service_slug')   
            service =  get_object_or_404(Service, slug = service_slug)
            return service
        except Http404:
            messages.error(self.request, "Failed! Invalid Service")
            return redirect(self.redirect_url)

    def get_object(self):
        try:
            current_company = self.get_current_company()
            current_service = self.get_current_service()
            return get_object_or_404(self.model, company = current_company, service = current_service)
        
        except Http404:
            messages.error(self.request, "Invalid service for this company")

        except Exception as e:
            logger.exception(f"Error in get_object function of BaseServiceDetailView of superadmin: {e}")

        return redirect(self.get_redirect_url())
        
    def handle_features(self, request, company, service):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    ServiceFeature.objects.filter(company = company, service = service).delete()

                    features = [ServiceFeature(company=company, service=service, feature=feature) for feature in features_list]
                    ServiceFeature.objects.bulk_create(features)

                    feature_objs = ServiceFeature.objects.filter(company = company, service = service)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of BaseServiceDetailView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, service):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")            
            
            initial = 0


            with transaction.atomic():
                ServiceVerticalTab.objects.filter(company = company, service = service).delete()
                ServiceVerticalBullet.objects.filter(company = company, service = service).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = ServiceVerticalTab.objects.create(
                            company = company,
                            service = service,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [ServiceVerticalBullet(
                                company = company, service = service, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                ServiceVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = ServiceVerticalBullet.objects.filter(company = company, service = service, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)

                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of BaseServiceDetailView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, service):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")                        
            
            initial = 0


            with transaction.atomic():
                ServiceHorizontalTab.objects.filter(company = company, service = service).delete()
                ServiceHorizontalBullet.objects.filter(company = company, service = service).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = ServiceHorizontalTab.objects.create(
                            company = company,
                            service = service,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:
                        
                            creating_horizontal_bullets = [ServiceHorizontalBullet(
                                company = company, service = service, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                ServiceHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = ServiceHorizontalBullet.objects.filter(company = company, service = service, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tabs function of BaseServiceDetailView: {e}")

        return []
    
    def handle_tables(self, request, company, service):
        try:
            service_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)


            with transaction.atomic():
                ServiceTableData.objects.filter(company = company, service = service).delete()
                ServiceTable.objects.filter(company = company, service = service).delete()

                for index, heading in enumerate(heading_list):
                    service_table = ServiceTable.objects.create(
                        company = company, service = service, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [ServiceTableData(
                            company = company, service = service,
                            heading = heading, data = data
                            ) for data in data_list_of_heading]

                    ServiceTableData.objects.bulk_create(table_data_objs )

                    service_table_data_objs = ServiceTableData.objects.filter(company = company, service = service, heading = heading)

                    service_table.datas.set(service_table_data_objs)

                    service_tables.append(service_table)

            return service_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_tables function of BaseServiceDetailView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, service):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                ServiceBulletPoint.objects.filter(company = company, service = service).delete()

                if bullet_point_list:
                    bullet_point_objects = [ServiceBulletPoint(
                        company = company, service = service,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    ServiceBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = ServiceBulletPoint.objects.filter(company = company, service = service)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of BaseServiceDetailView: {e}")

        return []

    def handle_tags(self, request, company, service):
        try:
            tag_list = [tag.strip() for tag in request.POST.getlist("tag")]            

            with transaction.atomic():
                ServiceTag.objects.filter(company = company, service = service).delete()

                if tag_list:
                    creating_tags = [ServiceTag(
                        company = company, service = service,
                        tag = tag
                        ) for tag in tag_list if tag]

                    ServiceTag.objects.bulk_create(creating_tags)

                    service_tags = ServiceTag.objects.filter(company = company, service = service)                

                    return service_tags

        except Exception as e:
            logger.exception(f"Error in handle_tags function of BaseServiceDetailView: {e}")

        return []

    def handle_timelines(self, request, company, service):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                ServiceTimeline.objects.filter(company = company, service = service).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [ServiceTimeline(
                        company = company, service = service,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    ServiceTimeline.objects.bulk_create(creating_timelines)

                    service_timelines = ServiceTimeline.objects.filter(company = company, service = service)                
                                            
                    return service_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of BaseServiceDetailView: {e}")

        return []


class AddServiceDetailView(BaseServiceDetailView, CreateView):
    form_class = ServiceDetailDescriptionForm
    template_name = "service_company/service_detail/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["add_service_detail_page"] = True

        current_company = self.get_current_company()        
        context["categories"] = ServiceCategory.objects.filter(company = current_company)
        context["tags"] = MetaTag.objects.all().order_by("name")
        
        return context

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_service_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddServiceDetailView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of AddServiceDetailView of superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            service_slug = request.POST.get('service')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_description = request.POST.get("meta_description")

            meta_tags = request.POST.getlist("meta_tag")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")
            
            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")

            summary = summary.strip() if summary else None
            
            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Service": service_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                }

            service = self.get_service(service_slug)

            with transaction.atomic():
                
                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                service_detail = self.model.objects.create(
                    company = company, service = service, summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    vertical_title = vertical_title, horizontal_title = horizontal_title,
                    table_title = table_title, bullet_title = bullet_title, tag_title = tag_title, 
                    timeline_title = timeline_title
                )
                
                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)

                service_detail.meta_tags.set(meta_tag_objs)

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(service_detail, key, True)

                service_detail.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, service)
                    getattr(service_detail, field).set(objects)

                messages.success(request, "Success! Created service detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddServiceDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class ServiceDetailsListView(BaseServiceDetailView, ListView):
    template_name = "service_company/service_detail/list.html"
    queryset = ServiceDetail.objects.none()
    success_url = redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "service_details"        
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company)
        except Exception as e:
            logger.exception(f"Error in getting queryset of ServiceDetailsListView of superadmin: {e}")
            return self.queryset


class ServiceDetailView(BaseServiceDetailView, DetailView):
    model = ServiceDetail
    template_name = "service_company/service_detail/detail.html"
    redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "service_detail"

    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:service_details', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url function of ServiceDetailView: {e}")
            return self.redirect_url


class UpdateServiceDetailView(BaseServiceDetailView, UpdateView):    
    form_class = ServiceDetailDescriptionForm
    template_name = "service_company/service_detail/update.html"
    context_object_name = "service_detail"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object()
        current_company = self.get_current_company()        
        context["categories"] = ServiceCategory.objects.filter(company = current_company)
        context["sub_categories"] = ServiceSubCategory.objects.filter(company = current_company, category = self.object.service.category)
        context["services"] = Service.objects.filter(company = current_company, category = self.object.service.category, sub_category = self.object.service.sub_category)
        context["tags"] = MetaTag.objects.all().order_by("name")
        
        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:update_service_details', kwargs = {"slug": self.kwargs.get('slug'), "service_slug": self.kwargs.get('service_slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateServiceDetailView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateServiceDetailView of superadmin: {e}")
            return self.redirect_url


    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            service_slug = request.POST.get('service')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_description = request.POST.get("meta_description")

            meta_tags = request.POST.getlist("meta_tag")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")   

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")

            # Fetch current company
            company = self.get_current_company()

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Service": service_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                }

            service = self.get_service(service_slug)

            with transaction.atomic():

                service_detail = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                service_detail.service = service
                service_detail.summary = summary

                service_detail.description = description

                service_detail.meta_title = meta_title
                service_detail.meta_description = meta_description

                service_detail.vertical_title = vertical_title
                service_detail.horizontal_title = horizontal_title
                service_detail.table_title = table_title
                service_detail.bullet_title = bullet_title
                service_detail.tag_title = tag_title
                service_detail.timeline_title = timeline_title

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)
                
                service_detail.meta_tags.set(meta_tag_objs)  

                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:                    
                        assigning_value = True

                    setattr(service_detail, key, assigning_value)
                
                service_detail.save()                             

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, service)
                    getattr(service_detail, field).set(objects)

                service_detail.save()

                messages.success(request, "Success! Updated service detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateServiceDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteServiceDetailPageView(BaseServiceDetailView, View):
    def get_object(self, **kwargs):
        company_slug = self.kwargs.get('slug')
        detail_page_slug = self.kwargs.get('detail_page_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = detail_page_slug)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            service_name = self.object.service.name
            self.object.delete()

            messages.success(request, f"Success! Removed service detail page of: {service_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Service Detail")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteServiceDetailPageView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class BaseServiceMultiPageView(BaseServiceCompanyView, View):
    model = ServiceMultiPage
    success_url = redirect_url = reverse_lazy('superadmin:home')        
        
    def get_categories(self):
        return ServiceCategory.objects.filter(company = self.current_company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["service_multipage"] = True
            
            self.current_company = self.get_current_company()
            
            context["current_company"] = self.current_company            
        except Exception as e:
            logger.exception(f"Error in getting context data of BaseServiceMultiPageView of superadmin: {e}")
        
        return context    
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:service_multipages', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseServiceMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseServiceMultiPageView of superadmin: {e}")
            return self.redirect_url
        
    def get_service(self, service_slug):
        try:
            return get_object_or_404(Service, slug = service_slug)
        except Http404:
            messages.error(self.request, "Invalid Service")
            return redirect(self.get_redirect_url())
        
    def handle_features(self, request, company, service):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    ServiceMultiPageFeature.objects.filter(company = company, service = service).delete()

                    features = [ServiceMultiPageFeature(company=company, service=service, feature=feature) for feature in features_list]
                    ServiceMultiPageFeature.objects.bulk_create(features)

                    feature_objs = ServiceMultiPageFeature.objects.filter(company = company, service = service)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of BaseServiceMultiPageView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, service):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")            
            
            initial = 0


            with transaction.atomic():
                ServiceMultiPageVerticalTab.objects.filter(company = company, service = service).delete()
                ServiceMultiPageVerticalBullet.objects.filter(company = company, service = service).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = ServiceMultiPageVerticalTab.objects.create(
                            company = company,
                            service = service,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [ServiceMultiPageVerticalBullet(
                                company = company, service = service, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                ServiceMultiPageVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = ServiceMultiPageVerticalBullet.objects.filter(company = company, service = service, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)


                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of BaseServiceMultiPageView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, service):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")                        
            
            initial = 0


            with transaction.atomic():
                ServiceMultiPageHorizontalTab.objects.filter(company = company, service = service).delete()
                ServiceMultiPageHorizontalBullet.objects.filter(company = company, service = service).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = ServiceMultiPageHorizontalTab.objects.create(
                            company = company,
                            service = service,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:
                        
                            creating_horizontal_bullets = [ServiceMultiPageHorizontalBullet(
                                company = company, service = service, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                ServiceMultiPageHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = ServiceMultiPageHorizontalBullet.objects.filter(company = company, service = service, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tabs function of BaseServiceMultiPageView: {e}")

        return []
    
    def handle_tables(self, request, company, service):
        try:
            service_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)


            with transaction.atomic():
                ServiceMultiPageTableData.objects.filter(company = company, service = service).delete()
                ServiceMultiPageTable.objects.filter(company = company, service = service).delete()

                for index, heading in enumerate(heading_list):
                    service_table = ServiceMultiPageTable.objects.create(
                        company = company, service = service, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [ServiceMultiPageTableData(
                            company = company, service = service,
                            heading = heading, data = data
                            ) for data in data_list_of_heading if data]

                    ServiceMultiPageTableData.objects.bulk_create(table_data_objs )

                    service_table_data_objs = ServiceMultiPageTableData.objects.filter(company = company, service = service, heading = heading)

                    service_table.datas.set(service_table_data_objs)
                    service_tables.append(service_table)

            return service_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_tables function of BaseServiceMultiPageView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, service):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                ServiceMultiPageBulletPoint.objects.filter(company = company, service = service).delete()

                if bullet_point_list:
                    bullet_point_objects = [ServiceMultiPageBulletPoint(
                        company = company, service = service,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    ServiceMultiPageBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = ServiceMultiPageBulletPoint.objects.filter(company = company, service = service)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of BaseServiceMultiPageView: {e}")

        return []

    def handle_tags(self, request, company, service):
        try:
            tag_list = [tag.strip() for tag in request.POST.getlist("tag")]            

            with transaction.atomic():
                ServiceMultiPageTag.objects.filter(company = company, service = service).delete()

                if tag_list:                
                    creating_tags = [ServiceMultiPageTag(
                        company = company, service = service,
                        tag = tag
                        ) for tag in tag_list if tag]

                    ServiceMultiPageTag.objects.bulk_create(creating_tags)

                    service_tags = ServiceMultiPageTag.objects.filter(company = company, service = service)                

                    return service_tags

        except Exception as e:
            logger.exception(f"Error in handle_tags function of BaseServiceMultiPageView: {e}")

        return []

    def handle_timelines(self, request, company, service):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                ServiceMultiPageTimeline.objects.filter(company = company, service = service).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [ServiceMultiPageTimeline(
                        company = company, service = service,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    ServiceMultiPageTimeline.objects.bulk_create(creating_timelines)

                    service_timelines = ServiceMultiPageTimeline.objects.filter(company = company, service = service)                
                                            
                    return service_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of BaseServiceMultiPageView: {e}")

        return []

    def handle_faqs(self, request, company, service):
        try:
            question_list = [question.strip() for question in request.POST.getlist("faq_question")]
            answer_list = [answer.strip() for answer in request.POST.getlist("faq_answer")]                        

            if len(question_list) != len(answer_list):
                raise ValueError("The number of questions does not match the number of summaries.")

            with transaction.atomic():
                ServiceMultiPageFaq.objects.filter(company = company, service = service).delete()
                
                if question_list and answer_list:
                    creating_faqs = [ServiceMultiPageFaq(
                        company = company, service = service,
                        question = question, answer = answer
                        ) for question, answer in zip(question_list, answer_list) if question and answer]

                    ServiceMultiPageFaq.objects.bulk_create(creating_faqs)

                    service_faqs = ServiceMultiPageFaq.objects.filter(company = company, service = service)                
                                            
                    return service_faqs
        except Exception as e:
            logger.exception(f"Error in handle_faqs function of BaseServiceMultiPageView: {e}")

        return []


class AddServiceMultiPageView(BaseServiceMultiPageView, CreateView):
    form_class = ServiceMultiPageDescriptionForm
    template_name = "service_company/multipage/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["categories"] = self.get_categories()
        context["tags"] = MetaTag.objects.all().order_by("name")

        return context

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_service_multipage', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddServiceMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of AddServiceMultiPageView of superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            current_company = self.get_current_company()

            form = self.get_form()

            service_slug = request.POST.get('service')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_description = request.POST.get("meta_description")

            meta_tags = request.POST.getlist("meta_tag")

            url_type = request.POST.get("url_type")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = current_company

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Service": service_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }

            service = self.get_service(service_slug)

            with transaction.atomic():
                if self.model.objects.filter(company = company, service = service).exists():
                    messages.error(request, "Multipage for this service already exists")
                    return redirect(self.get_redirect_url())
                
                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                service_multi_page = self.model.objects.create(
                    company = company, service = service, summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    url_type = url_type,
                    vertical_title = vertical_title, horizontal_title = horizontal_title,
                    table_title = table_title, bullet_title = bullet_title, tag_title = tag_title, 
                    timeline_title = timeline_title
                )

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)

                service_multi_page.meta_tags.set(meta_tag_objs)

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(service_multi_page, key, True)
                
                service_multi_page.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, service)
                    getattr(service_multi_page, field).set(objects)

                messages.success(request, "Success! Created service multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddServiceMultiPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class ServiceMultiPageListView(BaseServiceMultiPageView, ListView):
    template_name = "service_company/multipage/list.html"
    queryset = ServiceMultiPage.objects.none()
    context_object_name = "multipages"    
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company)
        except Exception as e:
            logger.exception(f"Error in getting queryset of ServiceMultiPageListView of superadmin: {e}")
            return self.queryset
        
class ServiceMultiPageDetailView(BaseServiceMultiPageView, DetailView):
    template_name = "service_company/multipage/detail.html"
    context_object_name = "multipage"

    def get_object(self):
        try:
            current_company = self.get_current_company()
            current_service = self.get_current_service()
            return get_object_or_404(self.model, company = current_company, service = current_service)
        
        except Http404:
            messages.error(self.request, "Invalid service for this company")

        except Exception as e:
            logger.exception(f"Error in get_object function of ServiceMultipageDetailView of superadmin: {e}")

        return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object
        
        context[self.context_object_name] = self.object
        return context
        
    def get_current_service(self):
        try:
            service_slug = self.kwargs.get('service_slug')
            return get_object_or_404(Service, slug = service_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Service")
            return redirect(self.redirect_url)        
    

class UpdateServiceMultiPageView(BaseServiceMultiPageView, UpdateView):    
    form_class = ServiceMultiPageDescriptionForm
    template_name = "service_company/multipage/update.html"
    context_object_name = "multipage"    

    def get_object(self):
        try:
            company_slug = self.kwargs.get('slug')
            multipage_slug = self.kwargs.get('multipage_slug')            
            
            return get_object_or_404(self.model, company__slug = company_slug, slug = multipage_slug)
        
        except Http404:
            messages.error(self.request, "Invalid service multipage object")
            return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_current_company()
            self.object = self.get_object()
            context[self.context_object_name] = self.object

            context["categories"] = ServiceCategory.objects.filter(company = current_company)
            context["sub_categories"] = ServiceSubCategory.objects.filter(company = current_company, category = self.object.service.category)
            context["services"] = Service.objects.filter(company = current_company, sub_category = self.object.service.sub_category)
            context["tags"] = MetaTag.objects.all().order_by("name")
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateMultiPageView of superadmin: {e}")
        
        return context    
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:update_service_multipage', kwargs = {"slug": self.kwargs.get('slug'), "multipage_slug": self.kwargs.get('multipage_slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateMultiPageView of superadmin: {e}")
            return self.redirect_url
        
        
    def post(self, request, *args, **kwargs):
        try:            
            form = self.get_form()

            service_slug = request.POST.get('service')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Service": service_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
                
            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }

            service = self.get_service(service_slug)

            with transaction.atomic():

                multipage = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                multipage.service = service
                multipage.summary = summary

                multipage.description = description

                multipage.meta_title = meta_title
                multipage.meta_description = meta_description

                multipage.url_type = url_type

                multipage.vertical_title = vertical_title
                multipage.horizontal_title = horizontal_title
                multipage.table_title = table_title
                multipage.bullet_title = bullet_title
                multipage.tag_title = tag_title
                multipage.timeline_title = timeline_title
                
                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)
                
                multipage.meta_tags.set(meta_tag_objs)

                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:
                        assigning_value = True

                    setattr(multipage, key, assigning_value)
                
                multipage.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, service)
                    getattr(multipage, field).set(objects)

                multipage.save()

                messages.success(request, "Success! Updated service multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateCompanyDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteServiceMultiPageView(BaseServiceMultiPageView, View):
    def get_object(self, **kwargs):
        company_slug = self.kwargs.get('slug')
        multipage_slug = self.kwargs.get('multipage_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = multipage_slug)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            service_name = self.object.service.name
            self.object.delete()

            messages.success(request, f"Success! Removed service multipage of: {service_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Service Multipage")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteServiceMultiPageView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


# Registration Company
class BaseRegistrationCompanyView(AdminBaseView, View):
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get('slug'), type__name = "Registration")
        except Http404:
            messages.error(self.request, "Invalid Company")
            return redirect(self.redirect_url)
    
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
            context["types"] = RegistrationType.objects.filter(company = self.get_current_company()).order_by("name")
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
            messages.error(request, "An unexpected error occurred")

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
            messages.error(request, "An unexpected error occurred")

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
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

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
            messages.error(request, "An unexpected error occurred")
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
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())


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
            context["types"] = RegistrationType.objects.filter(company = self.get_current_company()).order_by('name')

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
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())


# Registration FAQ
class RegistrationFaqBaseView(BaseRegistrationCompanyView):
    model = RegistrationFaq
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:registration_faqs', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseRegistrationFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_current_company(self):
        try:
            company_slug = self.kwargs.get(self.slug_url_kwarg)            
            self.company = get_object_or_404(Company, slug = company_slug, type__name = "Registration")
            return self.company
        except Http404:
            return None
        
    def get_registration_sub_type(self, registration_SUb_type_slug):
        try:            
            return get_object_or_404(RegistrationSubType, slug = registration_SUb_type_slug)
        except Http404:
            return None
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context["registration_faq_page"] = True

        return context


class AddRegistrationFaqView(RegistrationFaqBaseView, CreateView):    
    fields = ["company", "registration_sub_type", "question", "answer", "dynamic_place_rendering"]
    template_name = "registration_company/faqs/add.html"    

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_registration_faq', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddRegistrationFaqView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        return self.get_success_url()        
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["add_registration_faq_page"] = True
        context["types"] = RegistrationType.objects.filter(company__slug = company_slug).order_by("name")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            registration_sub_type_slug = self.request.POST.get('sub_type')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

            registration_sub_type_slug = registration_sub_type_slug.strip() if registration_sub_type_slug else None
            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Registration Sub Type": registration_sub_type_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            company = self.get_current_company()
            registration_sub_type = self.get_registration_sub_type(registration_sub_type_slug)

            if not company or not registration_sub_type:
                invalid_msg = ""
                
                if not company:
                    invalid_msg = "Invalid Registration Company"
                else:
                    invalid_msg = "Invalid Registration Sub Type"

                messages.error(request, invalid_msg)
                return redirect(self.get_redirect_url())
            
            dynamic_place_rendering = True if dynamic_place_rendering else False

            RegistrationFaq.objects.update_or_create(
                company = company, registration_sub_type = registration_sub_type, question = question, dynamic_place_rendering = dynamic_place_rendering, 
                defaults={"answer": answer}
                )

            messages.success(request, f"Success! Created FAQ object for registration sub type: {registration_sub_type.name}")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in get function of AddRegistrationFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class ListRegistrationFaqView(RegistrationFaqBaseView, ListView):
    model = RegistrationFaq
    template_name = "registration_company/faqs/list.html"
    queryset = model.objects.none()
    context_object_name = "faqs"

    def get_queryset(self):
        try:
            company_slug = self.kwargs.get(self.slug_url_kwarg)
            company = get_object_or_404(Company, slug = company_slug, type__name = "Registration")
            return self.model.objects.filter(company = company)
            
        except Http404:
            messages.error(self.request, "Invalid registration company")
            return redirect(self.redirect_url)


class UpdateRegistrationFaqView(RegistrationFaqBaseView, UpdateView):
    model = RegistrationFaq
    fields = ["registration_sub_type", "question", "answer", "dynamic_place_rendering"]
    template_name = "registration_company/faqs/update.html"
    context_object_name = "faq"    
        
    def get_object(self):
        company_slug = self.kwargs.get('slug') 
        registration_faq_slug = self.kwargs.get('registration_faq_slug') 

        self.object = get_object_or_404(RegistrationFaq, company__slug = company_slug, slug = registration_faq_slug)

        return self.object
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        company_slug = self.kwargs.get('slug')

        context["update_registration_faq_page"] = True

        context["types"] = RegistrationType.objects.filter(company__slug = company_slug).order_by("name")
        context["sub_types"] = RegistrationSubType.objects.filter(company__slug = company_slug, type = self.object.registration_sub_type.type).order_by("name")

        return context
        
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            registration_sub_type_slug = self.request.POST.get('sub_type')
            question = request.POST.get("question")
            answer = request.POST.get("answer")
            dynamic_place_rendering = request.POST.get("dynamic_place_rendering")

            question = question.strip() if question else None
            answer = answer.strip() if answer else None

            required_fields = {
                "Registration Sub Type": registration_sub_type_slug,
                "Question": question,
                "Answer": answer
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            registration_sub_type = self.get_registration_sub_type(registration_sub_type_slug)

            if not registration_sub_type:
                messages.error(request, "Invalid Registration Sub Type")
                return redirect(self.get_redirect_url())

            dynamic_place_rendering = True if dynamic_place_rendering else False

            similar_faq = self.model.objects.filter(
                company = self.object.company, registration_sub_type = registration_sub_type, question = question, answer = answer, dynamic_place_rendering = dynamic_place_rendering
                ).first()

            if similar_faq:
                if similar_faq.slug == self.object.slug:
                    messages.warning(request, "No changes detected")
                else:
                    messages.warning(request, "Similar registration FAQ already exists")
                return redirect(self.get_redirect_url())

            self.object.registration_sub_type = registration_sub_type
            self.object.question = question
            self.object.answer = answer
            self.object.dynamic_place_rendering = dynamic_place_rendering
            self.object.save()

            messages.success(request, f"Success! Updated FAQ")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid registration FAQ object")

        except Exception as e:
            logger.exception(f"Error in get function of UpdateRegistrationFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteRegistrationFaqView(RegistrationFaqBaseView, View):
    model = RegistrationFaq
        
    def get_object(self):
        faq_slug = self.kwargs.get('registration_faq_slug')
        company_slug = self.kwargs.get('slug')

        return get_object_or_404(self.model, slug = faq_slug, company__slug = company_slug)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            registration_sub_type_name = self.object.registration_sub_type.name
            self.object.delete()

            messages.success(request, f"Success! Removed registration FAQ object of: {registration_sub_type_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Registration FAQ")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteRegistrationFaqView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class BaseRegistrationEnquiryView(BaseRegistrationCompanyView, View):
    model = RegistrationEnquiry
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get(self.slug_url_kwarg))
        except Http404:
            messages.error(self.request, "Invalid Company")
            return self.redirect_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["current_company"] = self.get_current_company()
            context["registration_enquiry_page"] = True

        except Exception as e:
            logger.exception(f"Error in getting context data of BaseRegistrationEnquiryView: {e}")

        return context


class ListRegistrationEnquiryView(BaseRegistrationEnquiryView, ListView):
    queryset = RegistrationEnquiry.objects.none()
    context_object_name = "enquiries"
    template_name = "registration_company/enquiries/list.html"

    def get_queryset(self):
        try:
            return self.model.objects.filter(company__slug = self.kwargs.get(self.slug_url_kwarg))
        except Exception as e:
            logger.exception(f"Error in fetching queryset of ListRegistrationEnquiryView of superadmin: {e}")
            return self.queryset


class DeleteRegistrationEnquiryView(BaseRegistrationEnquiryView, View):
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:registration_enquiries', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of DeleteRegistrationEnquiryView of superadmin app: {e}")
            return self.success_url

    def get_redirect_url(self):
        return self.get_success_url()
            

    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(RegistrationEnquiry, company__slug = self.kwargs.get(self.slug_url_kwarg), slug = self.kwargs.get('enquiry_slug'))
            self.object.delete()

            messages.success(request, "Success! Delete Registration Enquiry")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Failed! Invalid Registration Enquiry")
            return redirect(self.get_redirect_url())


class BaseRegistrationDetailPageView(BaseRegistrationCompanyView):
    model = RegistrationDetailPage
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["registration_detail_page"] = True
            
            current_company = self.get_current_company()

            context["current_company"] = current_company

        except Exception as e:
            logger.exception(f"Error in getting context data of BaseRegistrationDetailPageView of superadmin: {e}")
        
        return context    
        
    def get_registration_sub_type(self, registration_sub_type_slug):
        try:
            return get_object_or_404(RegistrationSubType, slug = registration_sub_type_slug)
        except Http404:
            messages.error(self.request, "Invalid Registration Sub Type")
            return redirect(self.get_redirect_url())
        
    def get_current_registration_sub_type(self):
        try:
            registration_sub_type_slug = self.kwargs.get('registration_sub_type_slug')   
            registration = get_object_or_404(RegistrationSubType, slug = registration_sub_type_slug)
            return registration
        except Http404:
            messages.error(self.request, "Failed! Invalid Registration Sub Type")
            return redirect(self.redirect_url)

    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:registration_detail_pages', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url function of RegistrationDetailPageView: {e}")
            return self.redirect_url

    def get_success_url(self):
        return self.get_redirect_url()

    def get_object(self):
        try:
            current_company = self.get_current_company()
            current_registration_sub_type = self.get_current_registration_sub_type()
            return get_object_or_404(self.model, company = current_company, registration_sub_type = current_registration_sub_type)
        
        except Http404:
            messages.error(self.request, "Invalid registration sub type")

        except Exception as e:
            logger.exception(f"Error in get_object function of BaseRegistrationDetailPageView of superadmin: {e}")

        return redirect(self.get_redirect_url())
        
    def handle_features(self, request, company, registration_sub_type):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    RegistrationFeature.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()

                    features = [RegistrationFeature(company=company, registration_sub_type=registration_sub_type, feature=feature) for feature in features_list]
                    RegistrationFeature.objects.bulk_create(features)

                    feature_objs = RegistrationFeature.objects.filter(company = company, registration_sub_type = registration_sub_type)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of BaseRegistrationDetailPageView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, registration_sub_type):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")            
            
            initial = 0


            with transaction.atomic():
                RegistrationVerticalTab.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()
                RegistrationVerticalBullet.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = RegistrationVerticalTab.objects.create(
                            company = company,
                            registration_sub_type = registration_sub_type,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [RegistrationVerticalBullet(
                                company = company, registration_sub_type = registration_sub_type, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                RegistrationVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = RegistrationVerticalBullet.objects.filter(company = company, registration_sub_type = registration_sub_type, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)

                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of BaseRegistrationDetailPageView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, registration_sub_type):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")                        
            
            initial = 0


            with transaction.atomic():
                RegistrationHorizontalTab.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()
                RegistrationHorizontalBullet.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = RegistrationHorizontalTab.objects.create(
                            company = company,
                            registration_sub_type = registration_sub_type,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:
                        
                            creating_horizontal_bullets = [RegistrationHorizontalBullet(
                                company = company, registration_sub_type = registration_sub_type, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                RegistrationHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = RegistrationHorizontalBullet.objects.filter(company = company, registration_sub_type = registration_sub_type, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tabs function of BaseRegistrationDetailPageView: {e}")

        return []
    
    def handle_tables(self, request, company, registration_sub_type):
        try:
            registration_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)


            with transaction.atomic():
                RegistrationTableData.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()
                RegistrationTable.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()

                for index, heading in enumerate(heading_list):
                    registration_table = RegistrationTable.objects.create(
                        company = company, registration_sub_type = registration_sub_type, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [RegistrationTableData(
                            company = company, registration_sub_type = registration_sub_type,
                            heading = heading, data = data
                            ) for data in data_list_of_heading]

                    RegistrationTableData.objects.bulk_create(table_data_objs )

                    registration_table_data_objs = RegistrationTableData.objects.filter(company = company, registration_sub_type = registration_sub_type, heading = heading)

                    registration_table.datas.set(registration_table_data_objs)

                    registration_tables.append(registration_table)

            return registration_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_tables function of BaseRegistrationDetailPageView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, registration_sub_type):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                RegistrationBulletPoint.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()

                if bullet_point_list:
                    bullet_point_objects = [RegistrationBulletPoint(
                        company = company, registration_sub_type = registration_sub_type,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    RegistrationBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = RegistrationBulletPoint.objects.filter(company = company, registration_sub_type = registration_sub_type)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of BaseRegistrationDetailPageView: {e}")

        return []

    def handle_tags(self, request, company, registration_sub_type):
        try:
            tag_list = [tag.strip() for tag in request.POST.getlist("tag")]            

            with transaction.atomic():
                RegistrationTag.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()

                if tag_list:
                    creating_tags = [RegistrationTag(
                        company = company, registration_sub_type = registration_sub_type,
                        tag = tag
                        ) for tag in tag_list if tag]

                    RegistrationTag.objects.bulk_create(creating_tags)

                    registration_tags = RegistrationTag.objects.filter(company = company, registration_sub_type = registration_sub_type)                

                    return registration_tags

        except Exception as e:
            logger.exception(f"Error in handle_tags function of BaseRegistrationDetailPageView: {e}")

        return []

    def handle_timelines(self, request, company, registration_sub_type):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                RegistrationTimeline.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [RegistrationTimeline(
                        company = company, registration_sub_type = registration_sub_type,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    RegistrationTimeline.objects.bulk_create(creating_timelines)

                    registration_timelines = RegistrationTimeline.objects.filter(company = company, registration_sub_type = registration_sub_type)                
                                            
                    return registration_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of BaseRegistrationDetailPageView: {e}")

        return []


class AddRegistrationDetailPageView(BaseRegistrationDetailPageView, CreateView):
    form_class = RegistrationDetailPageDescriptionForm
    template_name = "registration_company/detail_page/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["add_registration_detail_page"] = True

        current_company = self.get_current_company()        
        context["types"] = RegistrationType.objects.filter(company = current_company)
        context["tags"] = MetaTag.objects.all().order_by("name")
        
        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_registration_detail_page', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseRegistrationDetailPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseRegistrationDetailPageView of superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            registration_sub_type_slug = request.POST.get('sub_type')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")
            
            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")

            summary = summary.strip() if summary else None
            
            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None
            
            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company :
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Registration": registration_sub_type_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                }

            registration_sub_type = self.get_registration_sub_type(registration_sub_type_slug)

            with transaction.atomic():
                
                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                registration_detail = self.model.objects.create(
                    company = company, registration_sub_type = registration_sub_type, summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    vertical_title = vertical_title, horizontal_title = horizontal_title,
                    table_title = table_title, bullet_title = bullet_title, tag_title = tag_title, 
                    timeline_title = timeline_title
                )                

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)

                registration_detail.meta_tags.set(meta_tag_objs)

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(registration_detail, key, True)

                registration_detail.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, registration_sub_type)
                    getattr(registration_detail, field).set(objects)

                messages.success(request, "Success! Created registration detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddRegistrationDetailPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class RegistrationDetailPageListView(BaseRegistrationDetailPageView, ListView):
    template_name = "registration_company/detail_page/list.html"
    queryset = RegistrationDetail.objects.none()
    success_url = redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "detail_pages"        
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company)
        except Exception as e:
            logger.exception(f"Error in getting queryset of RegistrationDetailsListView of superadmin: {e}")
            return self.queryset


class RegistrationDetailPageView(BaseRegistrationDetailPageView, DetailView):
    template_name = "registration_company/detail_page/detail.html"
    redirect_url = reverse_lazy('superadmin:home')
    context_object_name = "detail_page"    


class UpdateRegistrationDetailPageView(BaseRegistrationDetailPageView, UpdateView):    
    form_class = RegistrationDetailPageDescriptionForm
    template_name = "registration_company/detail_page/update.html"
    context_object_name = "detail_page"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object()
        current_company = self.get_current_company()        
        context["types"] = RegistrationType.objects.filter(company = current_company)
        context["sub_types"] = RegistrationSubType.objects.filter(company = current_company, type = self.object.registration_sub_type.type)
        context["tags"] = MetaTag.objects.all().order_by("name")
        
        return context
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:update_registration_detail_page', kwargs = {"slug": self.kwargs.get('slug'), "registration_sub_type_slug": self.kwargs.get('registration_sub_type_slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateRegistrationDetailPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateRegistrationDetailPageView of superadmin: {e}")
            return self.redirect_url


    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            registration_sub_type_slug = request.POST.get('sub_type')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")   

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None
            
            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")

            # Fetch current company
            company = self.get_current_company()

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Registration": registration_sub_type_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                }

            registration_sub_type = self.get_registration_sub_type(registration_sub_type_slug)

            with transaction.atomic():

                registration_detail = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                registration_detail.registration_sub_type = registration_sub_type
                registration_detail.summary = summary

                registration_detail.description = description

                registration_detail.meta_title = meta_title
                registration_detail.meta_description = meta_description

                registration_detail.vertical_title = vertical_title
                registration_detail.horizontal_title = horizontal_title
                registration_detail.table_title = table_title
                registration_detail.bullet_title = bullet_title
                registration_detail.tag_title = tag_title
                registration_detail.timeline_title = timeline_title

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)
                
                registration_detail.meta_tags.set(meta_tag_objs) 

                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:                    
                        assigning_value = True

                    setattr(registration_detail, key, assigning_value)
                
                registration_detail.save()                             

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, registration_sub_type)
                    getattr(registration_detail, field).set(objects)

                registration_detail.save()

                messages.success(request, "Success! Updated registration detail page")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateRegistrationDetailPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteRegistrationDetailPageView(BaseRegistrationDetailPageView, View):
    def get_object(self, **kwargs):
        company_slug = self.kwargs.get('slug')
        detail_page_slug = self.kwargs.get('detail_page_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = detail_page_slug)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            registration_sub_type_name = self.object.registration_sub_type.name
            self.object.delete()

            messages.success(request, f"Success! Removed registration detail page of: {registration_sub_type_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Registration Detail")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteRegistrationDetailPageView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class BaseRegistrationMultiPageView(BaseRegistrationCompanyView, View):
    model = RegistrationMultiPage
    success_url = redirect_url = reverse_lazy('superadmin:home')    
        
    def get_registration_types(self):
        return RegistrationType.objects.filter(company = self.current_company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["registration_multipage"] = True
            
            self.current_company = self.get_current_company()
            
            context["current_company"] = self.current_company            
        except Exception as e:
            logger.exception(f"Error in getting context data of BaseRegistrationMultiPageView of superadmin: {e}")
        
        return context    
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:registration_multipages', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of BaseRegistrationMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of BaseRegistrationMultiPageView of superadmin: {e}")
            return self.redirect_url
        
    def get_registration_sub_type(self, registration_sub_type_slug):
        try:
            return get_object_or_404(RegistrationSubType, slug = registration_sub_type_slug)
        except Http404:
            messages.error(self.request, "Invalid Registration Sub Type")
            return redirect(self.get_redirect_url())
        
    def handle_features(self, request, company, registration_sub_type):
        try:

            features_list = request.POST.getlist("feature")

            features_list = list({feature.strip() for feature in features_list})
            if features_list:
                with transaction.atomic():

                    RegistrationMultiPageFeature.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()

                    features = [RegistrationMultiPageFeature(company=company, registration_sub_type=registration_sub_type, feature=feature) for feature in features_list]
                    RegistrationMultiPageFeature.objects.bulk_create(features)

                    feature_objs = RegistrationMultiPageFeature.objects.filter(company = company, registration_sub_type = registration_sub_type)

                    return feature_objs
        
        except Exception as e:
            logger.exception(f"Error in handle_features function of BaseRegistrationMultiPageView: {e}")
        
        return []

    def handle_vertical_tabs(self, request, company, registration_sub_type):
        try:
            vertical_tab_objects = []

            vertical_heading_list = [heading.strip() for heading in request.POST.getlist("vertical_heading")]
            vertical_sub_heading_list = [sub_heading.strip() for sub_heading in request.POST.getlist("vertical_sub_heading")]
            vertical_summary_list = [summary.strip() for summary in request.POST.getlist("vertical_summary")]
            vertical_bullet_list = [bullet.strip() for bullet in request.POST.getlist("vertical_bullet")]
            vertical_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("vertical_bullet_count")]

            if not (len(vertical_heading_list) == len(vertical_sub_heading_list) == len(vertical_summary_list) == len(vertical_bullet_count_list)):
                raise ValueError("Mismatch in the number of vertical fields.")            
            
            initial = 0


            with transaction.atomic():
                RegistrationMultiPageVerticalTab.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()
                RegistrationMultiPageVerticalBullet.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()

                for i in range(len(vertical_bullet_count_list)):
                    heading = vertical_heading_list[i]
                    sub_heading = vertical_sub_heading_list[i]

                    if heading:
                        vertical_tab_obj = RegistrationMultiPageVerticalTab.objects.create(
                            company = company,
                            registration_sub_type = registration_sub_type,
                            heading = heading,
                            sub_heading = sub_heading,
                            summary = vertical_summary_list[i]
                        )

                        final = initial + vertical_bullet_count_list[i]
                        vertical_bullets = vertical_bullet_list[initial:final]
                        initial = final

                        if vertical_bullet_count_list[i] != 0:

                            creating_vertical_bullets = [RegistrationMultiPageVerticalBullet(
                                company = company, registration_sub_type = registration_sub_type, heading = heading,
                                sub_heading = sub_heading, bullet = bullet
                            ) for bullet in vertical_bullets if bullet]

                            if creating_vertical_bullets:
                                RegistrationMultiPageVerticalBullet.objects.bulk_create(creating_vertical_bullets)  

                            created_vertical_bullets = RegistrationMultiPageVerticalBullet.objects.filter(company = company, registration_sub_type = registration_sub_type, heading = heading, sub_heading = sub_heading)

                            vertical_tab_obj.bullets.set(created_vertical_bullets)


                        vertical_tab_objects.append(vertical_tab_obj)

            return vertical_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_vertical_tabs function of BaseRegistrationMultiPageView: {e}")

        return []
    
    def handle_horizontal_tabs(self, request, company, registration_sub_type):
        try:
            horizontal_tab_objects = []

            horizontal_heading_list = [heading.strip() for heading in request.POST.getlist("horizontal_heading")]
            horizontal_summary_list = [summary.strip() for summary in request.POST.getlist("horizontal_summary")]
            horizontal_bullet_list = [bullet.strip() for bullet in request.POST.getlist("horizontal_bullet")]
            horizontal_bullet_count_list = [int(count) if count != '' else 0 for count in request.POST.getlist("horizontal_bullet_count")] 

            if not (len(horizontal_heading_list) == len(horizontal_summary_list) == len(horizontal_bullet_count_list)):
                raise ValueError("Mismatch in the number of horizontal fields.")                        
            
            initial = 0


            with transaction.atomic():
                RegistrationMultiPageHorizontalTab.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()
                RegistrationMultiPageHorizontalBullet.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()

                for i in range(len(horizontal_bullet_count_list)):
                    heading = horizontal_heading_list[i]

                    if heading:
                        horizontal_tab_obj = RegistrationMultiPageHorizontalTab.objects.create(
                            company = company,
                            registration_sub_type = registration_sub_type,
                            heading = heading,
                            summary = horizontal_summary_list[i]
                        )

                        final = initial + horizontal_bullet_count_list[i]
                        horizontal_bullets = horizontal_bullet_list[initial:final]
                        initial = final
                        
                        if horizontal_bullet_count_list[i] != 0:
                        
                            creating_horizontal_bullets = [RegistrationMultiPageHorizontalBullet(
                                company = company, registration_sub_type = registration_sub_type, heading = heading,
                                bullet = bullet
                            ) for bullet in horizontal_bullets if bullet]

                            if creating_horizontal_bullets:
                                RegistrationMultiPageHorizontalBullet.objects.bulk_create(creating_horizontal_bullets)

                            created_horizontal_bullets = RegistrationMultiPageHorizontalBullet.objects.filter(company = company, registration_sub_type = registration_sub_type, heading = heading)

                            horizontal_tab_obj.bullets.set(created_horizontal_bullets)

                        horizontal_tab_objects.append(horizontal_tab_obj)

            return horizontal_tab_objects

        except (IntegrityError, IndexError, ValueError) as e:
            logger.exception(f"Error in handle_horizontal_tabs function of BaseRegistrationMultiPageView: {e}")

        return []
    
    def handle_tables(self, request, company, registration_sub_type):
        try:
            registration_tables = []

            heading_list = [heading.strip() for heading in request.POST.getlist("table_heading")]
            data_list = [data.strip() for data in request.POST.getlist("table_data")]

            heading_length = len(heading_list)
            data_length = len(data_list)


            with transaction.atomic():
                RegistrationMultiPageTableData.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()
                RegistrationMultiPageTable.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()

                for index, heading in enumerate(heading_list):
                    registration_table = RegistrationMultiPageTable.objects.create(
                        company = company, registration_sub_type = registration_sub_type, heading = heading
                    )

                    data_positions  = list(range(index, data_length, heading_length))
                    data_list_of_heading = [data_list[i] for i in data_positions ]

                    table_data_objs  = [RegistrationMultiPageTableData(
                            company = company, registration_sub_type = registration_sub_type,
                            heading = heading, data = data
                            ) for data in data_list_of_heading if data]

                    RegistrationMultiPageTableData.objects.bulk_create(table_data_objs )

                    registration_table_data_objs = RegistrationMultiPageTableData.objects.filter(company = company, registration_sub_type = registration_sub_type, heading = heading)

                    registration_table.datas.set(registration_table_data_objs)
                    registration_tables.append(registration_table)

            return registration_tables
        
        except Exception as e:
            logger.exception(f"Error in handle_tables function of BaseRegistrationMultiPageView: {e}")

        return []
    
    def handle_bullet_points(self, request, company, registration_sub_type):
        try:
            bullet_point_list = [bullet_point.strip() for bullet_point in request.POST.getlist("bullet")]

            with transaction.atomic():
                RegistrationMultiPageBulletPoint.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()

                if bullet_point_list:
                    bullet_point_objects = [RegistrationMultiPageBulletPoint(
                        company = company, registration_sub_type = registration_sub_type,
                        bullet_point = bullet_point
                    ) for bullet_point in bullet_point_list if bullet_point]

                    RegistrationMultiPageBulletPoint.objects.bulk_create(bullet_point_objects)

                    bullet_points = RegistrationMultiPageBulletPoint.objects.filter(company = company, registration_sub_type = registration_sub_type)                

                    return bullet_points

        except Exception as e:
            logger.exception(f"Error in handle_bullet_points function of BaseRegistrationMultiPageView: {e}")

        return []

    def handle_tags(self, request, company, registration_sub_type):
        try:
            tag_list = [tag.strip() for tag in request.POST.getlist("tag")]            

            with transaction.atomic():
                RegistrationMultiPageTag.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()

                if tag_list:                
                    creating_tags = [RegistrationMultiPageTag(
                        company = company, registration_sub_type = registration_sub_type,
                        tag = tag
                        ) for tag in tag_list if tag]

                    RegistrationMultiPageTag.objects.bulk_create(creating_tags)

                    registration_tags = RegistrationMultiPageTag.objects.filter(company = company, registration_sub_type = registration_sub_type)                

                    return registration_tags

        except Exception as e:
            logger.exception(f"Error in handle_tags function of BaseRegistrationMultiPageView: {e}")

        return []

    def handle_timelines(self, request, company, registration_sub_type):
        try:
            heading_list = [heading.strip() for heading in request.POST.getlist("timeline_heading")]
            summary_list = [summary.strip() for summary in request.POST.getlist("timeline_summary")]                        

            if len(heading_list) != len(summary_list):
                raise ValueError("The number of headings does not match the number of summaries.")

            with transaction.atomic():
                RegistrationMultiPageTimeline.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()
                
                if heading_list and summary_list:
                    creating_timelines = [RegistrationMultiPageTimeline(
                        company = company, registration_sub_type = registration_sub_type,
                        heading = heading, summary = summary
                        ) for heading, summary in zip(heading_list, summary_list)]

                    RegistrationMultiPageTimeline.objects.bulk_create(creating_timelines)

                    registration_timelines = RegistrationMultiPageTimeline.objects.filter(company = company, registration_sub_type = registration_sub_type)                
                                            
                    return registration_timelines
        except Exception as e:
            logger.exception(f"Error in handle_timelines function of BaseRegistrationMultiPageView: {e}")

        return []

    def handle_faqs(self, request, company, registration_sub_type):
        try:
            question_list = [question.strip() for question in request.POST.getlist("faq_question")]
            answer_list = [answer.strip() for answer in request.POST.getlist("faq_answer")]                        

            if len(question_list) != len(answer_list):
                raise ValueError("The number of questions does not match the number of summaries.")

            with transaction.atomic():
                RegistrationMultiPageFaq.objects.filter(company = company, registration_sub_type = registration_sub_type).delete()
                
                if question_list and answer_list:
                    creating_faqs = [RegistrationMultiPageFaq(
                        company = company, registration_sub_type = registration_sub_type,
                        question = question, answer = answer
                        ) for question, answer in zip(question_list, answer_list) if question and answer]

                    RegistrationMultiPageFaq.objects.bulk_create(creating_faqs)

                    registration_faqs = RegistrationMultiPageFaq.objects.filter(company = company, registration_sub_type = registration_sub_type)                
                                            
                    return registration_faqs
        except Exception as e:
            logger.exception(f"Error in handle_faqs function of BaseRegistrationMultiPageView: {e}")

        return []


class AddRegistrationMultiPageView(BaseRegistrationMultiPageView, CreateView):
    form_class = RegistrationMultiPageDescriptionForm
    template_name = "registration_company/multipage/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["types"] = self.get_registration_types()
        context["tags"] = MetaTag.objects.all().order_by("name")

        return context

    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:add_registration_multipage', kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of AddRegistrationMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of AddRegistrationMultiPageView of superadmin: {e}")
            return self.redirect_url

    def post(self, request, *args, **kwargs):
        try:
            current_company = self.get_current_company()

            form = self.get_form()

            registration_sub_type_slug = request.POST.get('sub_type')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = current_company

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Registration Sub Type": registration_sub_type_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }

            registration_sub_type = self.get_registration_sub_type(registration_sub_type_slug)

            with transaction.atomic():
                if self.model.objects.filter(company = company, registration_sub_type = registration_sub_type).exists():
                    messages.error(request, "Multipage for this registration sub type already exists")
                    return redirect(self.get_redirect_url())
                
                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                registration_multi_page = self.model.objects.create(
                    company = company, registration_sub_type = registration_sub_type, summary = summary, description = description,
                    meta_title = meta_title, meta_description = meta_description,
                    url_type = url_type,
                    vertical_title = vertical_title, horizontal_title = horizontal_title,
                    table_title = table_title, bullet_title = bullet_title, tag_title = tag_title, 
                    timeline_title = timeline_title
                )

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)

                registration_multi_page.meta_tags.set(meta_tag_objs)  

                for key, value in checkbox_fields.items():
                    if value:
                        setattr(registration_multi_page, key, True)
                
                registration_multi_page.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, registration_sub_type)
                    getattr(registration_multi_page, field).set(objects)

                messages.success(request, "Success! Created registration multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddRegistrationMultiPageView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class RegistrationMultiPageListView(BaseRegistrationMultiPageView, ListView):
    template_name = "registration_company/multipage/list.html"
    queryset = RegistrationMultiPage.objects.none()
    context_object_name = "multipages"    
    
    def get_queryset(self):
        try:
            current_company = self.get_current_company()
            return self.model.objects.filter(company = current_company)
        except Exception as e:
            logger.exception(f"Error in getting queryset of RegistrationMultiPageListView of superadmin: {e}")
            return self.queryset
        
class RegistrationMultiPageDetailView(BaseRegistrationMultiPageView, DetailView):
    template_name = "registration_company/multipage/detail.html"
    context_object_name = "multipage"

    def get_current_registration_sub_type(self):
        try:
            registration_sub_type_slug = self.kwargs.get('registration_sub_type_slug')
            return get_object_or_404(RegistrationSubType, slug = registration_sub_type_slug)
        except Http404:
            messages.error(self.request, "Failed! Invalid Registration Sub Type")
            return redirect(self.redirect_url)   

    def get_object(self):
        try:
            current_company = self.get_current_company()
            current_registration_sub_type = self.get_current_registration_sub_type()
            return get_object_or_404(self.model, company = current_company, registration_sub_type = current_registration_sub_type)
        
        except Http404:
            messages.error(self.request, "Invalid registration for this company")

        except Exception as e:
            logger.exception(f"Error in get_object function of RegistrationMultipageDetailView of superadmin: {e}")

        return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object
        
        context[self.context_object_name] = self.object
        return context     
    

class UpdateRegistrationMultiPageView(BaseRegistrationMultiPageView, UpdateView):    
    form_class = RegistrationMultiPageDescriptionForm
    template_name = "registration_company/multipage/update.html"
    context_object_name = "multipage"    

    def get_object(self):
        try:
            company_slug = self.kwargs.get('slug')
            multipage_slug = self.kwargs.get('multipage_slug')            
            
            return get_object_or_404(self.model, company__slug = company_slug, slug = multipage_slug)
        
        except Http404:
            messages.error(self.request, "Invalid registration multipage object")
            return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            current_company = self.get_current_company()
            self.object = self.get_object()
            context[self.context_object_name] = self.object

            context["types"] = RegistrationType.objects.filter(company = current_company)
            context["sub_types"] = RegistrationSubType.objects.filter(company = current_company, type = self.object.registration_sub_type.type)
            context["tags"] = MetaTag.objects.all().order_by("name")
        except Exception as e:
            logger.exception(f"Error in getting context data of UpdateMultiPageView of superadmin: {e}")
        
        return context    
    
    def get_success_url(self):
        try:
            return reverse_lazy('superadmin:update_registration_multipage', kwargs = {"slug": self.kwargs.get('slug'), "multipage_slug": self.kwargs.get('multipage_slug')})
        except Exception as e:
            logger.exception(f"Error in fetching success url of UpdateMultiPageView of superadmin: {e}")
            return self.success_url
        
    def get_redirect_url(self):
        try:
            return self.get_success_url()
        except Exception as e:
            logger.exception(f"Error in fetching redirect url of UpdateMultiPageView of superadmin: {e}")
            return self.redirect_url
        
        
    def post(self, request, *args, **kwargs):
        try:            
            form = self.get_form()

            registration_sub_type_slug = request.POST.get('sub_type')

            summary = request.POST.get("summary")

            meta_title = request.POST.get("meta_title")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")

            url_type = request.POST.get("url_type")

            vertical_title = request.POST.get("vertical_title")
            horizontal_title = request.POST.get("horizontal_title")
            table_title = request.POST.get("table_title")
            bullet_title = request.POST.get("bullet_title")
            tag_title = request.POST.get("tag_title")
            timeline_title = request.POST.get("timeline_title")

            hide_features = request.POST.get("hide_features")
            hide_vertical_tab = request.POST.get("hide_vertical_tab")
            hide_horizontal_tab = request.POST.get("hide_horizontal_tab")
            hide_table = request.POST.get("hide_table")
            hide_bullets = request.POST.get("hide_bullets")
            hide_tags = request.POST.get("hide_tags")
            hide_timeline = request.POST.get("hide_timeline")
            hide_faqs = request.POST.get("hide_faqs")

            summary = summary.strip() if summary else None

            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]

            url_type = url_type.strip() if url_type else None

            vertical_title = vertical_title.strip() if vertical_title else None
            horizontal_title = horizontal_title.strip() if horizontal_title else None
            table_title = table_title.strip() if table_title else None
            bullet_title = bullet_title.strip() if bullet_title else None
            tag_title = tag_title.strip() if tag_title else None
            timeline_title = timeline_title.strip() if timeline_title else None

            # Fetch current company
            company = self.get_current_company()

            if not company:
                messages.error(request, "Invalid company")
                return redirect(self.redirect_url)
            
            required_fields = {
                "Registration Sub Type": registration_sub_type_slug,
                "summary": summary,                
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
                }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
                
            checkbox_fields = {
                "hide_features": hide_features,
                "hide_vertical_tab": hide_vertical_tab,
                "hide_horizontal_tab": hide_horizontal_tab,
                "hide_table": hide_table,
                "hide_bullets": hide_bullets,
                "hide_tags": hide_tags,
                "hide_timeline": hide_timeline,
                "hide_faqs": hide_faqs
                }

            registration_sub_type = self.get_registration_sub_type(registration_sub_type_slug)

            with transaction.atomic():

                multipage = self.get_object()

                if not form.is_valid():                    
                    messages.error(request, "Description is required")
                    return redirect(self.get_redirect_url())
                
                cleaned_form = form.cleaned_data
                description = cleaned_form.get("description")

                multipage.registration_sub_type = registration_sub_type
                multipage.summary = summary

                multipage.description = description

                multipage.meta_title = meta_title
                multipage.meta_description = meta_description

                multipage.url_type = url_type

                multipage.vertical_title = vertical_title
                multipage.horizontal_title = horizontal_title
                multipage.table_title = table_title
                multipage.bullet_title = bullet_title
                multipage.tag_title = tag_title
                multipage.timeline_title = timeline_title

                meta_tag_objs = MetaTag.objects.filter(slug__in = meta_tags)
                
                multipage.meta_tags.set(meta_tag_objs)            

                for key, value in checkbox_fields.items():
                    assigning_value = False

                    if value:
                        assigning_value = True

                    setattr(multipage, key, assigning_value)
                
                multipage.save()

                relationship_handlers = {
                    "features": self.handle_features,
                    "vertical_tabs": self.handle_vertical_tabs,
                    "horizontal_tabs": self.handle_horizontal_tabs,
                    "tables": self.handle_tables,
                    "bullet_points": self.handle_bullet_points,
                    "tags": self.handle_tags,
                    "timelines": self.handle_timelines,
                    "faqs": self.handle_faqs,
                }

                for field, handler in relationship_handlers.items():
                    objects = handler(request, company, registration_sub_type)
                    getattr(multipage, field).set(objects)

                multipage.save()

                messages.success(request, "Success! Updated registration multipage")
                return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of UpdateCompanyDetailView of superadmin: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


class DeleteRegistrationMultiPageView(BaseRegistrationMultiPageView, View):
    def get_object(self, **kwargs):
        company_slug = self.kwargs.get('slug')
        multipage_slug = self.kwargs.get('multipage_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = multipage_slug)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            registration_sub_type_name = self.object.registration_sub_type.name
            self.object.delete()

            messages.success(request, f"Success! Removed registration multipage of: {registration_sub_type_name}")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Registration Multipage")

        except Exception as e:
            logger.exception(f"Error in post function of DeleteRegistrationMultiPageView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())


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
            messages.error(request, "An unexpected error occurred")
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
            messages.error(request, "An unexpected error occurred.")

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
            messages.error(request, "An unexpected error occurred.")

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
            messages.error(request, "An unexpected error occurred.")

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
            messages.error(request, "An unexpected error occurred.")

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
            messages.error(request, "An unexpected error occurred.")

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
            messages.error(request, "An unexpected error occurred.")

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
            messages.error(request, "An unexpected error occurred.")

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


# Clients
class BaseClientView(BaseCompanyView):
    model = Client
    success_url = redirect_url = reverse_lazy('superadmin:home')

    def get_current_company(self):
        try:
            return get_object_or_404(Company, slug = self.kwargs.get(self.slug_url_kwarg))
        except Http404:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["client_page"] = context["company_page"] = True
        context["current_company"] = self.get_current_company()
        context["company_type_page"] = False
        return context
    
    def get_success_url(self):
        try:
            if self.slug_url_kwarg:
                return reverse_lazy("superadmin:clients", kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of BaseClientView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_object(self):
        company_slug = self.kwargs.get(self.slug_url_kwarg)
        client_slug = self.kwargs.get('client_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = client_slug)
    

class AddClientView(BaseClientView, CreateView):    
    template_name = "clients/add.html"
    fields = ["company", "name", "image", "order"]

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:add_client", kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of AddClientView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["add_client_page"] = True        
        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()

            name = request.POST.get("name")
            image = request.FILES.get("image")
            order = request.POST.get("order", 0)

            name = name.strip() if name else None

            if not name or not image:
                message = "Failed! Name is required"
                if name:
                    message = "Failed! Image is required"
                
                messages.error(request, message)
                return redirect(self.get_redirect_url())
            
            if self.model.objects.filter(company = company, name = name).exists():
                messages.warning(request, "Similar client already exists")
                return redirect(self.get_redirect_url())
            
            self.model.objects.create(company = company, name = name, image = image, order = order)
            messages.success(request, "Success! Client Created")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddClientView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
            return redirect(self.get_redirect_url())
        

class ClientListView(BaseClientView, ListView):
    template_name = "clients/list.html"
    context_object_name = "clients"
    queryset = Client.objects.none()
    
    def get_queryset(self):
        company_slug = self.kwargs.get('slug')
        if company_slug:
            return self.model.objects.filter(company__slug = company_slug).order_by("order")
        
        return self.queryset


class UpdateClientView(BaseClientView, UpdateView):    
    fields = ["name", "image", "order"]
    slug_url_kwarg = 'slug'        

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            name = request.POST.get("name")
            image = request.FILES.get("image")
            order = request.POST.get("order", 0)

            name = name.strip() if name else None

            if not name:
                messages.error(request, "Failed! Name is required")
                return redirect(self.get_redirect_url())

            if not image and not self.object.image:
                messages.error(request, "Failed! Image is required")
                return redirect(self.get_redirect_url())     
            
            similar_client = self.model.objects.filter(company = self.object.company, name = name).first()

            if similar_client:
                dublicate_error_msg = ""

                if similar_client.slug == self.object.slug:
                    if not image and not order:
                        dublicate_error_msg = "No changes detected"
                else:
                    dublicate_error_msg = "Similar client already exists"

                if dublicate_error_msg:
                    messages.warning(request, dublicate_error_msg)
                    return redirect(self.get_redirect_url())
            
            self.object.name = name
            self.object.order = order

            if image:
                self.object.image = image

            self.object.save()

            messages.success(request, "Success! Client Updated")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid Client")

        except Exception as e:
            logger.exception(f"Error in post function of UpdateClientView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
        

class DeleteClientView(BaseClientView, DeleteView):
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Client Deleted")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid client")

        except Exception as e:
            logger.exception(f"Error in delete function of DeleteClientView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

# Student Testimonials
class BaseStudentTestimonialView(BaseEducationCompanyView):
    model = StudentTestimonial
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_current_company(self):
        try:
            self.company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            return self.company
        except Http404:
            messages.error(self.request, "Invalid company")
            return redirect(self.redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["testimonial_page"] = context["company_page"] = True
        context["current_company"] = self.get_current_company()
        context["company_type_page"] = False
        return context
    
    def get_success_url(self):
        try:
            if self.slug_url_kwarg:
                return reverse_lazy("superadmin:student_testimonials", kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of BaseStudentTestimonialView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_object(self):
        company_slug = self.kwargs.get(self.slug_url_kwarg)
        testimonial_slug = self.kwargs.get('testimonial_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = testimonial_slug)
    
    def get_course(self, course_slug):
        try:
            company = self.get_current_company()
            return get_object_or_404(Course, company = company, slug = course_slug)
        except Http404:
            return None
        
    def get_place(self, place_slug):
        try:
            return get_object_or_404(UniquePlace, slug = place_slug)
        except Http404:
            return None
    

class AddStudentTestimonialView(BaseStudentTestimonialView, CreateView):    
    template_name = "admin_student_testimonials/add.html"
    fields = ["company", "name", "image", "course", "place", "text", "rating", "order"]

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:add_student_testimonial", kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of AddStudentTestimonialView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["add_testimonial_page"] = True
        context["ratings"] = list(range(1,6))

        context["programs"] = Program.objects.filter(company__slug = self.kwargs.get(self.slug_url_kwarg))
        context["states"] = UniqueState.objects.all().order_by('name')
        
        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()

            name = request.POST.get("name")
            image = request.FILES.get("image")
            course_slug = request.POST.get("course")
            place_slug = request.POST.get("place")
            text = request.POST.get("testimonial")
            rating = request.POST.get("rating", 5)
            order = request.POST.get("order", 0)

            name = name.strip() if name else None
            course_slug = course_slug.strip() if course_slug else None
            place_slug = place_slug.strip() if place_slug else None
            text = text.strip() if text else None
            rating = rating.strip() if rating else None
            order = order.strip() if order else None

            required_fields = {
                "Name": name,
                "Image": image,
                "Course": course_slug,
                "Place": place_slug,
                "Testimonal Text": text,
                "Rating": rating,
                "Order": order 
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
                

            course = self.get_course(course_slug)
            place = self.get_place(place_slug)

            if not course or not place:
                invalid_msg = ""
                if not course:
                    invalid_msg = "Invalid Course"
                else:
                    invalid_msg = "Invalid Place"

                messages.error(request, invalid_msg)
                return redirect(self.get_redirect_url())
                        
            if self.model.objects.filter(
                company = company, name = name, course = course, place = place
                ).exists():

                messages.warning(request, "Similar testimonial already exists")
                return redirect(self.get_redirect_url())
            
            self.model.objects.create(
                company = company, name = name, image = image, course = course, place = place,
                text = text, rating = rating, order = order
            )

            messages.success(request, "Success! Testimonial Created")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddStudentTestimonialView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
            return redirect(self.get_redirect_url())


class StudentTestimonialListView(BaseStudentTestimonialView, ListView):
    template_name = "admin_student_testimonials/list.html"
    context_object_name = "testimonials"
    queryset = StudentTestimonial.objects.none()
    
    def get_queryset(self):
        company_slug = self.kwargs.get('slug')
        if company_slug:
            return self.model.objects.filter(company__slug = company_slug).order_by("order")
        
        return self.queryset
    

class UpdateStudentTestimonialView(BaseStudentTestimonialView, UpdateView):    
    fields = ["name", "image", "course", "place", "text", "rating", "order"]
    template_name = "admin_student_testimonials/update.html"
    slug_url_kwarg = 'slug'
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["update_testimonial_page"] = True
        context["ratings"] = list(range(1,6))

        context["programs"] = Program.objects.filter(company = self.company).order_by("name")
        context["courses"] = Course.objects.filter(program = self.object.course.program).order_by("name")
        context["states"] = UniqueState.objects.all().order_by('name')
        context["districts"] = UniqueDistrict.objects.filter(state = self.object.place.state).order_by('name')
        context["places"] = UniquePlace.objects.filter(district = self.object.place.district).order_by('name')
        
        return context    

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            name = request.POST.get("name")
            image = request.FILES.get("image")
            course_slug = request.POST.get("course")
            place_slug = request.POST.get("place")
            text = request.POST.get("testimonial")
            rating = request.POST.get("rating", 5)
            order = request.POST.get("order", 0)

            name = name.strip() if name else None
            course_slug = course_slug.strip() if course_slug else None
            place_slug = place_slug.strip() if place_slug else None
            text = text.strip() if text else None
            rating = rating.strip() if rating else None
            order = order.strip() if order else None

            required_fields = {
                "Name": name,
                "Image": image,
                "Course": course_slug,
                "Place": place_slug,
                "Testimonal Text": text,
                "Rating": rating,
                "Order": order 
            }

            for key, value in required_fields.items():
                if key == "Image" and self.object.image:
                    continue
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            course = self.get_course(course_slug)
            place = self.get_place(place_slug)

            if not course or not place:
                invalid_msg = ""
                if not course:
                    invalid_msg = "Invalid Course"
                else:
                    invalid_msg = "Invalid Place"

                messages.error(request, invalid_msg)
                return redirect(self.get_redirect_url())
            
            similar_client = self.model.objects.filter(
                company = self.object.company, name = name, course = course, place = place
                ).first()

            if similar_client:
                dublicate_error_msg = ""

                if similar_client.slug == self.object.slug:
                    if not (image or order or text or rating):
                        dublicate_error_msg = "No changes detected"
                else:
                    dublicate_error_msg = "Similar testimonial already exists"

                if dublicate_error_msg:
                    messages.warning(request, dublicate_error_msg)
                    return redirect(self.get_redirect_url())
            
            self.object.name = name
            self.object.course = course
            self.object.place = place
            self.object.text = text
            self.object.rating = rating
            self.object.order = order

            if image:
                self.object.image = image

            self.object.save()

            messages.success(request, "Success! Testimonial Updated")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid Testimonial")

        except Exception as e:
            logger.exception(f"Error in post function of UpdateStudentTestimonialView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class DeleteStudentTestimonialView(BaseStudentTestimonialView, DeleteView):
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Testimonial Deleted")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Testimonial")

        except Exception as e:
            logger.exception(f"Error in delete function of DeleteStudentTestimonialView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    
# General Testimonial
class BaseTestimonialView(BaseCompanyView):
    model = Testimonial
    success_url = redirect_url = reverse_lazy('superadmin:home')
    slug_url_kwarg = 'slug'

    def get_current_company(self):
        try:
            self.company = get_object_or_404(Company, slug = self.kwargs.get('slug'))
            return self.company
        except Http404:
            messages.error(self.request, "Invalid company")
            return redirect(self.redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["testimonial_page"] = context["company_page"] = True
        context["current_company"] = self.get_current_company()
        context["company_type_page"] = False
        return context
    
    def get_success_url(self):
        try:
            if self.slug_url_kwarg:
                return reverse_lazy("superadmin:testimonials", kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of BaseTestimonialView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()
    
    def get_object(self):
        company_slug = self.kwargs.get(self.slug_url_kwarg)
        testimonial_slug = self.kwargs.get('testimonial_slug')

        return get_object_or_404(self.model, company__slug = company_slug, slug = testimonial_slug)    
        
    def get_place(self, place_slug):
        try:
            return get_object_or_404(UniquePlace, slug = place_slug)
        except Http404:
            return None
    

class AddTestimonialView(BaseTestimonialView, CreateView):    
    template_name = "admin_testimonials/add.html"
    fields = ["company", "name", "image", "company", "place", "text", "rating", "order"]

    def get_success_url(self):
        try:
            return reverse_lazy("superadmin:add_testimonial", kwargs = {"slug": self.kwargs.get('slug')})
        except Exception as e:
            logger.exception(f"Error in get_success_url function of AddTestimonialView of superadmin app: {e}")
        
        return self.success_url
    
    def get_redirect_url(self):
        return self.get_success_url()    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["add_testimonial_page"] = True
        context["ratings"] = list(range(1,6))

        context["states"] = UniqueState.objects.all().order_by('name')
        
        return context

    def post(self, request, *args, **kwargs):
        try:
            company = self.get_current_company()

            name = request.POST.get("name")
            image = request.FILES.get("image")
            client_company = request.POST.get("company")
            place_slug = request.POST.get("place")
            text = request.POST.get("testimonial")
            rating = request.POST.get("rating", 5)
            order = request.POST.get("order", 0)

            name = name.strip() if name else None
            client_company = client_company.strip() if client_company else None
            place_slug = place_slug.strip() if place_slug else None
            text = text.strip() if text else None
            rating = rating.strip() if rating else None
            order = order.strip() if order else None

            required_fields = {
                "Name": name,
                "Image": image,
                "Company": client_company,
                "Place": place_slug,
                "Testimonal Text": text,
                "Rating": rating,
                "Order": order 
            }

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())
                
            place = self.get_place(place_slug)

            if not place:                
                messages.error(request, "Invalid Place")
                return redirect(self.get_redirect_url())
                        
            if self.model.objects.filter(
                company = company, name = name, client_company = client_company, place = place
                ).exists():

                messages.warning(request, "Similar testimonial already exists")
                return redirect(self.get_redirect_url())
            
            self.model.objects.create(
                company = company, name = name, image = image, client_company = client_company, place = place,
                text = text, rating = rating, order = order
            )

            messages.success(request, "Success! Testimonial Created")
            return redirect(self.get_success_url())

        except Exception as e:
            logger.exception(f"Error in post function of AddTestimonialView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
            return redirect(self.get_redirect_url())


class TestimonialListView(BaseTestimonialView, ListView):
    template_name = "admin_testimonials/list.html"
    context_object_name = "testimonials"
    queryset = Testimonial.objects.none()
    
    def get_queryset(self):
        company_slug = self.kwargs.get('slug')

        if company_slug:
            return self.model.objects.filter(company = self.get_current_company()).order_by("order")        
        
        return self.queryset
    

class UpdateTestimonialView(BaseTestimonialView, UpdateView):    
    fields = ["name", "image", "company", "place", "text", "rating", "order"]
    template_name = "admin_testimonials/update.html"
    slug_url_kwarg = 'slug'
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["update_testimonial_page"] = True
        context["ratings"] = list(range(1,6))
        
        context["states"] = UniqueState.objects.all().order_by('name')
        context["districts"] = UniqueDistrict.objects.filter(state = self.object.place.state).order_by('name')
        context["places"] = UniquePlace.objects.filter(district = self.object.place.district).order_by('name')
        
        return context    

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            name = request.POST.get("name")
            image = request.FILES.get("image")
            client_company = request.POST.get("company")
            place_slug = request.POST.get("place")
            text = request.POST.get("testimonial")
            rating = request.POST.get("rating", 5)
            order = request.POST.get("order", 0)

            name = name.strip() if name else None
            client_company = client_company.strip() if client_company else None
            place_slug = place_slug.strip() if place_slug else None
            text = text.strip() if text else None
            rating = rating.strip() if rating else None
            order = order.strip() if order else None

            required_fields = {
                "Name": name,
                "Image": image,
                "Company": client_company,
                "Place": place_slug,
                "Testimonal Text": text,
                "Rating": rating,
                "Order": order 
            }

            for key, value in required_fields.items():
                if key == "Image" and self.object.image:
                    continue
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())

            place = self.get_place(place_slug)

            if not place:
                messages.error(request, "Invalid Place")
                return redirect(self.get_redirect_url())
            
            similar_client = self.model.objects.filter(
                company = self.object.company, name = name, client_company = client_company, place = place
                ).first()

            if similar_client:
                dublicate_error_msg = ""

                if similar_client.slug == self.object.slug:
                    if not (image or order or text or rating):
                        dublicate_error_msg = "No changes detected"
                else:
                    dublicate_error_msg = "Similar testimonial already exists"

                if dublicate_error_msg:
                    messages.warning(request, dublicate_error_msg)
                    return redirect(self.get_redirect_url())
            
            self.object.name = name
            self.object.client_company = client_company
            self.object.place = place
            self.object.text = text
            self.object.rating = rating
            self.object.order = order

            if image:
                self.object.image = image

            self.object.save()

            messages.success(request, "Success! Testimonial Updated")
            return redirect(self.get_success_url())
        
        except Http404:
            messages.error(request, "Invalid Testimonial")

        except Exception as e:
            logger.exception(f"Error in post function of UpdateTestimonialView of superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

class DeleteTestimonialView(BaseTestimonialView, DeleteView):
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Success! Testimonial Deleted")
            return redirect(self.get_success_url())

        except Http404:
            messages.error(request, "Invalid Testimonial")

        except Exception as e:
            logger.exception(f"Error in delete function of DeleteTestimonialView of superadmin app: {e}")
            messages.error(request, "An unexpected error occurred")

        return redirect(self.get_redirect_url())
    

# Blogs
class BaseBlogView(AdminBaseView):
    model = Blog
    success_url = redirect_url = reverse_lazy('superadmin:blogs')
    slug_url_kwarg = 'slug'    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["blog_page"] = True
        return context    

    def get_company(self, company_slug, company_type):
        try:
            return get_object_or_404(Company, slug = company_slug, type__name = company_type)
        except Http404:
            return None       


class AddBlogView(BaseBlogView, CreateView):
    template_name = "admin_blogs/add.html"
    success_url = redirect_url = reverse_lazy('superadmin:add_blogs')
    form_class = BlogContentForm

    def get_courses(self, course_slugs):
        return Course.objects.filter(slug__in = course_slugs)

    def get_products(self, product_slugs):
        return Product.objects.filter(slug__in = product_slugs)

    def get_services(self, service_slugs):
        return Service.objects.filter(slug__in = service_slugs)
        
    def get_registration_sub_types(self, registration_sub_type_slugs):
        return RegistrationSubType.objects.filter(slug__in = registration_sub_type_slugs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["add_blog_page"] = True
        context["types"] = ("General", "Education", "Product", "Registration", "Service")
        context["tags"] = MetaTag.objects.all().order_by("name")

        return context

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            title = request.POST.get("title")
            image = request.FILES.get("image")
            blog_type = request.POST.get("type")

            company_slug = request.POST.get("company")
            course_slugs = request.POST.getlist("course")
            product_slugs = request.POST.getlist("product")
            service_slugs = request.POST.getlist("service")
            registration_sub_type_slugs = request.POST.getlist("registration_sub_type")
            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")
            summary = request.POST.get("summary")
            
            content = None

            if form.is_valid():
                cleaned_form = form.cleaned_data
                content = cleaned_form.get("content")

            title = title.strip() if title else None        
            blog_type = blog_type.strip() if blog_type else None            
            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]
            meta_description = meta_description.strip() if meta_description else None
            summary = summary.strip() if summary else None
            content = content.strip() if content else None

            required_fields = {
                "Title": title,
                "Type": blog_type,
                "Content": content,
                "Summary": summary,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
            }

            if blog_type != "General":
                required_fields["Company"] = company_slug

            if blog_type == "Education":
                required_fields["Course"] = course_slugs
            elif blog_type == "Product":
                required_fields["Product"] = product_slugs
            elif blog_type == "Service":
                required_fields["Service"] = service_slugs
            elif blog_type == "Registration":
                required_fields["Registration"] = registration_sub_type_slugs

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.redirect_url)


            company = self.get_company(company_slug, blog_type) if blog_type != "General" else None

            updating_meta_tags = []
            with transaction.atomic():
                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                if blog_type != "General" and not company:
                    messages.error(request, "Invalid Company")
                    return redirect(self.redirect_url)
                
                courses = self.get_courses(course_slugs) if blog_type == "Education" else []
                products = self.get_products(product_slugs) if blog_type == "Product" else []
                services = self.get_services(service_slugs) if blog_type == "Service" else []
                registration_sub_types = self.get_registration_sub_types(registration_sub_type_slugs) if blog_type == "Registration" else []

                blog = None

                if blog_type == "Education":
                    for course in courses:
                        if Blog.objects.filter(
                            title = title, blog_type = blog_type, company = company, course = course
                        ).exists():
                            messages.warning(request, "Similar blog already exists")
                            return redirect(self.redirect_url)
                        blog = Blog.objects.create(
                            title = title, image = image, blog_type = blog_type, company = company, course = course, content = content,
                            summary = summary, meta_description = meta_description
                        )

                elif blog_type == "Product":
                    for product in products:
                        if Blog.objects.filter(
                            title = title, blog_type = blog_type, company = company, product = product
                        ).exists():
                            messages.warning(request, "Similar blog already exists")
                            return redirect(self.redirect_url)
                        blog = Blog.objects.create(
                            title = title, image = image, blog_type = blog_type, company = company, product = product, content = content,
                            summary = summary, meta_description = meta_description
                        )

                elif blog_type == "Service":
                    for service in services:
                        if Blog.objects.filter(
                            title = title, blog_type = blog_type, company = company, service = service
                        ).exists():
                            messages.warning(request, "Similar blog already exists")
                            return redirect(self.redirect_url)
                        blog = Blog.objects.create(
                            title = title, image = image, blog_type = blog_type, company = company, service = service, content = content,
                            summary = summary, meta_description = meta_description
                        )

                elif blog_type == "Registration":
                    for registration_sub_type in registration_sub_types:
                        if Blog.objects.filter(
                            title = title, blog_type = blog_type, company = company, registration_sub_type = registration_sub_type
                        ).exists():
                            messages.warning(request, "Similar blog already exists")
                            return redirect(self.redirect_url)
                        blog = Blog.objects.create(
                            title = title, image = image, blog_type = blog_type, company = company, registration_sub_type = registration_sub_type, content = content,
                            summary = summary, meta_description = meta_description
                        )                

                else:
                    if Blog.objects.filter(
                        title = title, blog_type = blog_type
                    ).exists():
                        messages.warning(request, "Similar blog already exists")
                        return redirect(self.redirect_url)

                    blog = Blog.objects.create(
                        title = title, image = image, blog_type = blog_type, content = content,
                        summary = summary, meta_description = meta_description
                    )                

                if blog:
                    if meta_tags:
                        meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                        blog.meta_tags.set(meta_tag_objects)

                    messages.success(request, "Success! Created Blog")
                    return redirect(self.success_url)
        
        except Exception as e:
            logger.exception(f"Error in post function of AddBlogView in superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)


class ListBlogView(BaseBlogView, ListView):
    template_name = "admin_blogs/list.html"
    context_object_name = "blogs"
    queryset = Blog.objects.all()


class UpdateBlogView(BaseBlogView, UpdateView):
    template_name = "admin_blogs/update.html"
    success_url = redirect_url = reverse_lazy('superadmin:blogs')
    context_object_name = "blog"
    form_class = BlogContentForm

    def get_course(self, course_slug):
        try:
            return get_object_or_404(Course , slug = course_slug)
        except Http404:
            return None

    def get_product(self, product_slug):
        try:
            return get_object_or_404(Product, slug = product_slug)
        except Http404:
            return None

    def get_service(self, service_slug):
        try:
            return get_object_or_404(Service, slug = service_slug)
        except Http404:
            return None
        
    def get_registration_sub_type(self, registration_sub_type_slug):
        try:
            return get_object_or_404(RegistrationSubType, slug = registration_sub_type_slug)
        except Http404:
            return None

    def get_redirect_url(self):
        try:
            return reverse_lazy('superadmin:update_blog', kwargs = {"slug": self.kwargs.get(self.slug_url_kwarg)})
        except Exception as e:
            logger.exception(f"Error in get_redirect_url of UpdateBlogView in superadmin app: {e}")
            return self.redirect_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["types"] = ("General", "Education", "Product", "Registration", "Service")

        self.object = self.get_object()

        context["companies"] = Company.objects.filter(type__name = self.object.blog_type) if self.object.blog_type != "General" else None
        
        context["programs"] = Program.objects.filter(company = self.object.company) if self.object.blog_type == "Education" else None
        context["product_categories"] = ProductCategory.objects.filter(company = self.object.company) if self.object.blog_type == "Product" else None
        context["registration_types"] = RegistrationType.objects.filter(company = self.object.company) if self.object.blog_type == "Registration" else None
        context["service_categories"] = ServiceCategory.objects.filter(company = self.object.company) if self.object.blog_type == "Service" else None

        context["courses"] = Course.objects.filter(company = self.object.company, program = self.object.course.program) if self.object.blog_type == "Education" else None
        context["product_sub_categories"] = ProductSubCategory.objects.filter(company = self.object.company, category = self.object.product.category) if self.object.blog_type == "Product" else None
        context["registration_sub_types"] = RegistrationSubType.objects.filter(company = self.object.company, type = self.object.registration_sub_type.type) if self.object.blog_type == "Registration" else None
        context["service_sub_categories"] = ServiceSubCategory.objects.filter(company = self.object.company, category = self.object.service.category) if self.object.blog_type == "Service" else None

        context["services"] = Service.objects.filter(company = self.object.company, category = self.object.service.category, sub_category = self.object.service.sub_category) if self.object.blog_type == "Service" else None
        context["products"] = Product.objects.filter(company = self.object.company, category = self.object.product.category, sub_category = self.object.product.sub_category) if self.object.blog_type == "Product" else None

        context["tags"] = MetaTag.objects.all().order_by("name")
 
        return context

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()

            title = request.POST.get("title")
            image = request.FILES.get("image")
            blog_type = request.POST.get("type")

            company_slug = request.POST.get("company")
            course_slug = request.POST.get("course")
            product_slug = request.POST.get("product")
            service_slug = request.POST.get("service")
            registration_sub_type_slug = request.POST.get("registration_sub_type")

            meta_tags = request.POST.getlist("meta_tag")
            meta_description = request.POST.get("meta_description")
            summary = request.POST.get("summary")

            content = None

            if form.is_valid():
                cleaned_form = form.cleaned_data
                content = cleaned_form.get("content")

            title = title.strip() if title else None        
            blog_type = blog_type.strip() if blog_type else None            
            meta_tags = [tag.strip() for tag in meta_tags if tag.strip()]
            meta_description = meta_description.strip() if meta_description else None
            summary = summary.strip() if summary else None
            content = content.strip() if content else None

            required_fields = {
                "Title": title,
                "Type": blog_type,
                "Content": content,
                "Summary": summary,
                "Meta Tags": meta_tags,
                "Meta Description": meta_description
            }

            if blog_type != "General":
                required_fields["Company"] = company_slug

            if blog_type == "Education":
                required_fields["Course"] = course_slug
            elif blog_type == "Product":
                required_fields["Product"] = product_slug
            elif blog_type == "Service":
                required_fields["Service"] = service_slug
            elif blog_type == "Registration":
                required_fields["Registration"] = registration_sub_type_slug

            for key, value in required_fields.items():
                if not value:
                    messages.error(request, f"Failed! {key} is required")
                    return redirect(self.get_redirect_url())


            company = self.get_company(company_slug, blog_type) if blog_type != "General" else None

            if blog_type != "General" and not company:
                messages.error(request, "Invalid Company")
                return redirect(self.get_redirect_url())
            
            course = self.get_course(course_slug) if blog_type == "Education" else None
            product = self.get_product(product_slug) if blog_type == "Product" else None
            service = self.get_service(service_slug) if blog_type == "Service" else None
            registration_sub_type = self.get_registration_sub_type(registration_sub_type_slug) if blog_type == "Registration" else None

            if blog_type != "General":
                invalid_message = ""

                if blog_type == "Education" and not course:
                    invalid_message = "Failed! Invalid Course"

                elif blog_type == "Product" and not product:
                    invalid_message = "Failed! Invalid Product"

                elif blog_type == "Service" and not service:
                    invalid_message = "Failed! Invalid Service"

                elif blog_type == "Registration" and not registration_sub_type:
                    invalid_message = "Failed! Invalid Registration Sub Type"

                if invalid_message:
                    messages.error(request, invalid_message)
                    return redirect(self.get_redirect_url())
        

            self.object = self.get_object()

            updating_meta_tags = []
            with transaction.atomic():
                for tag in meta_tags:
                    if not MetaTag.objects.filter(slug = tag).exists():

                        new_tag, created = MetaTag.objects.get_or_create(name = tag.strip())

                        if not new_tag.slug in updating_meta_tags:
                            updating_meta_tags.append(new_tag.slug)

                    else:
                        if not tag in updating_meta_tags:
                            updating_meta_tags.append(tag)

                self.object.title = title
                self.object.blog_type = blog_type

                self.object.product = None
                self.object.course = None
                self.object.service = None
                self.object.registration_sub_type = None

                self.object.summary = summary
                self.object.content = content
                self.object.meta_description = meta_description
                self.object.company = company

                if image:
                    self.object.image = image                

                if Blog.objects.filter(
                    title = title, blog_type = blog_type, company = company, course = course, product = product, service = service, registration_sub_type = registration_sub_type
                    ).exclude(slug = self.object.slug).exists():
                    messages.warning(request, "Similar blog already exists")
                    return redirect(self.get_redirect_url())

                self.object.course = course
                self.object.product = product
                self.object.service = service 
                self.object.registration_sub_type = registration_sub_type    

                self.object.save()                

                meta_tag_objects = MetaTag.objects.filter(slug__in = updating_meta_tags)
                self.object.meta_tags.set(meta_tag_objects)

                messages.success(request, "Success! Blog Updated")
                return redirect(self.success_url)   

            raise Exception                

        except Http404:
            messages.error(request, "Invalid Blog")        
        
        except Exception as e:
            logger.exception(f"Error in post function of UpdateBlogView in superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")
        
        return redirect(self.get_redirect_url())


class DeleteBlogView(BaseBlogView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(Blog, slug = self.kwargs.get(self.slug_url_kwarg))
            self.object.delete()
            messages.success(request, "Success! Blog Deleted")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Blog")
            return redirect(self.redirect_url)
        

class PublishBlogView(BaseBlogView, UpdateView):
    fields = ["is_published"]

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.is_published = True
            self.object.save()

            messages.success(request, "Success! Blog Published")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Blog")

        except Exception as e:
            logger.exception(f"Error in post function of PublishBlogView in superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)


class UnPublishBlogView(BaseBlogView, UpdateView):
    fields = ["is_published"]

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.is_published = False
            self.object.save()

            messages.success(request, "Success! Blog Unpublished")
            return redirect(self.success_url)

        except Http404:
            messages.error(request, "Failed! Invalid Blog")

        except Exception as e:
            logger.exception(f"Error in post function of UnPublishBlogView in superadmin app: {e}")
            messages.error(request, "Failed! An unexpected error occurred")

        return redirect(self.redirect_url)
    

class BaseMetaTagView(AdminBaseView):
    model = MetaTag
    success_url = redirect_url = reverse_lazy("superadmin:meta_tags")
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["meta_tag_page"] = True

        return context


class AddMetaTagView(BaseMetaTagView, CreateView):
    template_name = "meta_tag/add.html"
    form_class = MetaTagDescriptionForm

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")            
            meta_title = request.POST.get("meta_title")
            meta_description = request.POST.get("meta_description")

            name = name.strip() if name else None
            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            if not name or not meta_description:
                required_field = "Meta Description" if "Name" else "Name"

                messages.error(request, f"Failed! {required_field} is required")
                return redirect(self.redirect_url)
            
            form = self.get_form()

            description = form.cleaned_data.get("description").strip() if form.is_valid() else None            

            with transaction.atomic():

                meta_tag, created = self.model.objects.get_or_create(name = name, defaults = {"description": description, "meta_title": meta_title, "meta_description": meta_description})

                if not created:
                    messages.warning(request, "Failed! Similar meta tag already exists")
                    return redirect(self.redirect_url)

                messages.success(request, "Success! Created Meta Tag")
                return redirect(self.success_url)
            
        except Exception as e:
            logger.exception(f"Error in post function of AddMetaTagView")
            
        messages.error(request, "Failed! An unexpected error occurred")
        return redirect(self.redirect_url)
    

class MetaTagListView(BaseMetaTagView, ListView):
    queryset = MetaTag.objects.all().order_by("name")
    template_name = "meta_tag/list.html"
    context_object_name = "meta_tags"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["list_meta_tag_page"] = True

        return context


class UpdateMetaTagView(BaseMetaTagView, UpdateView):
    template_name = "meta_tag/update.html"
    form_class = MetaTagDescriptionForm
    context_object_name = "meta_tag"

    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get("name")            
            meta_title = request.POST.get("meta_title")
            meta_description = request.POST.get("meta_description")

            name = name.strip() if name else None
            meta_title = meta_title.strip() if meta_title else None
            meta_description = meta_description.strip() if meta_description else None

            if not name or not meta_description:
                required_field = "Meta Description" if "Name" else "Name"

                messages.error(request, f"Failed! {required_field} is required")
                return redirect(self.redirect_url)

            form = self.get_form()
            description = form.cleaned_data.get("description").strip() if form.is_valid() else None            

            self.object = self.get_object()
            
            with transaction.atomic():
                if MetaTag.objects.filter(name = name).exclude(slug = self.object.slug).exists():
                    messages.warning(request, "Failed! Similar meta tag already exists")
                    return redirect(self.redirect_url)

                self.object.name = name
                self.object.meta_title = meta_title
                self.object.meta_description = meta_description
                self.object.description = description
                self.object.save()    

                messages.success(request, "Success! Updated Meta Tag")
                return redirect(self.success_url)
            
        except Exception as e:
            logger.exception(f"Error in post function of UpdateMetaTagView: {e}")

        messages.error(request, "Failed! An unexpected error occurred")
        return redirect(self.redirect_url)


class DeleteMetaTagView(BaseMetaTagView, UpdateView):
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()

            messages.success(request, "Success! Deleted Meta Tag")
            return redirect(self.success_url)
        
        except Http404:
            messages.error(request, "Failed! Invalid Meta Tag")
            return redirect(self.redirect_url)
    