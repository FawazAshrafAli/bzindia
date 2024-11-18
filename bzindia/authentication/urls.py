from django.urls import path
from .views import LoginView, LogoutView, CustomerLoginView

app_name = "authentication"

urlpatterns = [
    path('', LoginView.as_view(), name="login"),
    path('customer_login', CustomerLoginView.as_view(), name="customer_login"),
    path('logout', LogoutView.as_view(), name="logout"),
]
