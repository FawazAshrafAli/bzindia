from django.urls import path

from .views import GetRegistrationSubTypeView

app_name = "registration"

urlpatterns = [
    path('get_registration_sub_types/', GetRegistrationSubTypeView.as_view(), name="get_registration_sub_types")
]
