from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View, CreateView, ListView, UpdateView
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

logger = logging.getLogger(__name__)

@method_decorator(never_cache, name="dispatch")
class AdminBaseView(LoginRequiredMixin, View):
    login_url = reverse_lazy("authentication:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            pass
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
    template_name = "admin_company/list.html"
    

class AddCompanyView(BaseCompanyView, CreateView):
    success_url = redirect_url = reverse_lazy('superadmin:add_company')
    fields = ["name", "type", "slug", "favicon", "logo", "phone1", "phone2", "whatsapp", "email"]
    template_name = "admin_company/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['company_types'] = CompanyType.objects.all()
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
    template_name = "admin_company/update.html"
    success_url = redirect_url = reverse_lazy('superadmin:companies')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['company_types'] = CompanyType.objects.all()
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
            
        return redirect(self.redirect_url)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Company Deletion Successfull.")
            return redirect(self.success_url)
        except Exception as e:
            logger.exception(f"Error in deleting company: {e}")
            return redirect(self.redirect_url)

# class AddCompanyView(BaseCompanyView, TemplateView):
#     template_name = "admin_company/add.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         try:
#             context['company_types'] = CompanyType.objects.all()
#         except Exception as e:
#             logger.exception(f"Error in fetching context data of admin add company view: {e}")
#         return context