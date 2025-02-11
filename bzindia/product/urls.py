from django.urls import path
from .views import ProductListView, GetSubCategoriesView, GetProductsView

app_name = "product"

urlpatterns = [
    path('', ProductListView.as_view(), name="products"),
    path('get_sub_categories/', GetSubCategoriesView.as_view(), name = "get_sub_categories"),
    path('get_products/', GetProductsView.as_view(), name = "get_products"),
]
