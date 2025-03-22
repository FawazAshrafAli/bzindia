from django.urls import path

from .views import GetRegistrationSubTypeView, GetRegistrationTypeView

app_name = "registration"

urlpatterns = [
    path('get_registration_sub_types/', GetRegistrationSubTypeView.as_view(), name="get_registration_sub_types"),
    path('get_types/', GetRegistrationTypeView.as_view(), name="get_types"),
]
