from django.urls import path
from .views import LoginView, LogoutView, CustomerLoginView, SendEmailVerificationOtpView, VerifyEmailView

app_name = "authentication"

urlpatterns = [
    path('', LoginView.as_view(), name="login"),
    path('customer_login/', CustomerLoginView.as_view(), name="customer_login"),
    path('logout/', LogoutView.as_view(), name="logout"),

    path('send_email_verification_otp/', SendEmailVerificationOtpView.as_view(), name="send_email_verification_otp"),
    path('verify_email/', VerifyEmailView.as_view(), name="verify_email"),
]
