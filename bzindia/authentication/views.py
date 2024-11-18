from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView, View, RedirectView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

class LoginView(TemplateView):
    template_name = 'superadmin/login.html'
    success_url = reverse_lazy("superadmin:home")
    redirect_url = reverse_lazy("authentication:login")    

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_authenticated:
                if request.user.is_superuser:
                    return redirect(self.success_url)
                else:
                    return redirect(reverse_lazy("company:home"))
        
            return render(request, self.template_name)
        except Exception as e:
            logger.exception(f"Error in get method of login view: {e}")

        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        url = self.redirect_url
        error_message = None

        try:
            username = request.POST.get("username")
            password = request.POST.get("password")

            if not username or not password:
                error_message = "Please provide both username and password."
            else:  
                user = authenticate(request, username = username.strip(), password = password)

                if user is not None and user.is_superuser:
                    login(request, user)
                    url = self.success_url
                else:
                    error_message = "Failed! Invalid credentials."
                
        except Exception as e:
            error_message = "Login Failed."
            logger.error(f"Error in post method of login view: {e}")
        
        if error_message:
            messages.error(request, error_message)
        return redirect(url)
    

class CustomerLoginView(TemplateView):
    template_name = 'customer/login.html'
    success_url = reverse_lazy("customer:home")
    redirect_url = reverse_lazy("authentication:customer_login")    

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_authenticated:
                if not request.user.is_superuser:
                    return redirect(self.success_url)
                else:
                    return redirect(reverse_lazy("superadmin:home"))
        
            return render(request, self.template_name)
        except Exception as e:
            logger.exception(f"Error in get method of login view: {e}")

        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        url = self.redirect_url
        error_message = None

        try:
            username = request.POST.get("username")
            password = request.POST.get("password")

            print(username)
            print(password)

            if not username or not password:
                error_message = "Please provide both username and password."
            else:  
                user = authenticate(request, username = username.strip(), password = password)

                if user is not None and not user.is_superuser:
                    login(request, user)
                    url = self.success_url
                else:
                    error_message = "Failed! Invalid credentials."
                
        except Exception as e:
            error_message = "Login Failed."
            logger.error(f"Error in post method of login view: {e}")
        
        if error_message:
            messages.error(request, error_message)
        return redirect(url)
    

class LogoutView(RedirectView):
    redirect_url = reverse_lazy("authentication:login")

    def get(self, request, *args, **kwargs):
        try:
            logout(request)

        except Exception as e:
            logger.error(f"Error occured during logout: {e}")
            messages.error(request, "Logout Failed.")
        
        return redirect(self.redirect_url)



        
    
        
        
        
