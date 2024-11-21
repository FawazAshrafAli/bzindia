from django.urls import path
from .views import generate_location_csv

app_name = "locations"

urlpatterns = [
    path('', generate_location_csv, name="generate_csv")
]
