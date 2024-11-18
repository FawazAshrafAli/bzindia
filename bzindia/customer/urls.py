from django.urls import path

from .views import (CustomerHomeView, 
                    AddProductCategoryView, DeleteProductCategoryView, UpdateProductCategoryView, ListProductCategoryView,
                    AddProductSubCategoryView, ListProductSubCategoryView, UpdateProductSubCategoryView, DeleteProductSubCategoryView,
                    AddBrandView, DeleteBrandView, UpdateBrandView, ListBrandView, 
                    AddSizeView, DeleteSizeView, UpdateSizeView, ListSizeView,
                    AddColorView, DeleteColorView, UpdateColorView, ListColorView, 
                    AddProductView, DeleteProductView, UpdateProductView, ListProductView,
                    CategoryFilteredSizesView)

app_name = "customer"

urlpatterns = [
    path('', CustomerHomeView.as_view(), name="home"),

    path('add_product_category/', AddProductCategoryView.as_view(), name="add_product_category"),
    path('product_categories/', ListProductCategoryView.as_view(), name="product_categories"),
    path('update_product_category/<str:slug>', UpdateProductCategoryView.as_view(), name="update_product_category"),
    path('delete_product_category/<str:slug>', DeleteProductCategoryView.as_view(), name="delete_product_category"),

    path('add_product_sub_category/', AddProductSubCategoryView.as_view(), name="add_product_sub_category"),
    path('product_sub_categories/', ListProductSubCategoryView.as_view(), name="product_sub_categories"),
    path('update_product_sub_category/<str:slug>', UpdateProductSubCategoryView.as_view(), name="update_product_sub_category"),
    path('delete_product_sub_category/<str:slug>', DeleteProductSubCategoryView.as_view(), name="delete_product_sub_category"),

    path('add_brand/', AddBrandView.as_view(), name="add_brand"),
    path('brands/', ListBrandView.as_view(), name="brands"),
    path('update_brand/<str:slug>', UpdateBrandView.as_view(), name="update_brand"),
    path('delete_brand/<str:slug>', DeleteBrandView.as_view(), name="delete_brand"),

    path('add_size/', AddSizeView.as_view(), name="add_size"),
    path('sizes/', ListSizeView.as_view(), name="sizes"),
    path('update_size/<str:slug>', UpdateSizeView.as_view(), name="update_size"),
    path('delete_size/<str:slug>', DeleteSizeView.as_view(), name="delete_size"),

    path('add_color/', AddColorView.as_view(), name="add_color"),
    path('colors/', ListColorView.as_view(), name="colors"),
    path('update_color/<str:slug>', UpdateColorView.as_view(), name="update_color"),
    path('delete_color/<str:slug>', DeleteColorView.as_view(), name="delete_color"),

    path('add_product/', AddProductView.as_view(), name="add_product"),
    path('products/', ListProductView.as_view(), name="products"),
    path('update_product/<str:slug>', UpdateProductView.as_view(), name="update_product"),
    path('delete_product/<str:slug>', DeleteProductView.as_view(), name="delete_product"),

    path('get_sizes/', CategoryFilteredSizesView.as_view(), name="get_sizes"),
]
