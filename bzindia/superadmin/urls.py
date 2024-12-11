from django.urls import path
from .views import (
    HomeView, CompanyListView, AddCompanyView, UpdateCompanyView, DeleteCompanyView,
    FitleredCompanyListView, CompanyDetailView,
    CompanyTypeListView, AddCompanyTypeView, DeleteCompanyTypeView, UpdateCompanyTypeView,
    ListProductView, AddProductView,
    ListBrandView, AddBrandView,
    ListProductCategoryView, AddProductCategoryView,
    ListProductSubCategoryView, AddProductSubCategoryView,
    ListProductColorView, AddProductColorView,

    AddCourseView, CourseListView,
    CourseProgramListView, 

    ListPostOfficeView, ListBankView, ListCourtView, ListPoliceStationView,
    )

app_name = "superadmin"

urlpatterns = [
    path('', HomeView.as_view(), name="home"),

    # Company
    path('add_company/', AddCompanyView.as_view(), name="add_company"),
    path('update_company/<str:slug>', UpdateCompanyView.as_view(), name="update_company"),
    path('delete_company/<str:slug>', DeleteCompanyView.as_view(), name="delete_company"),
    path('companies/', CompanyListView.as_view(), name="companies"),
    path('companies/<str:slug>', FitleredCompanyListView.as_view(), name="filtered_companies"),

    path('company/<str:slug>', CompanyDetailView.as_view(), name="company"),

    path('add_company_type/', AddCompanyTypeView.as_view(), name="add_company_type"),
    path('update_company_type/<str:slug>', UpdateCompanyTypeView.as_view(), name="update_company_type"),
    path('company_types/', CompanyTypeListView.as_view(), name="company_types"),
    path('delete_company_type/<str:slug>', DeleteCompanyTypeView.as_view(), name="delete_company_type"),

    # Product Company
    path('add_product/<str:slug>', AddProductView.as_view(), name="add_product"),
    path('products/<str:slug>', ListProductView.as_view(), name="products"),

    path('add_brand/<str:slug>', AddBrandView.as_view(), name="add_brand"),
    path('brands/<str:slug>', ListBrandView.as_view(), name="brands"),

    path('add_category/<str:slug>', AddProductCategoryView.as_view(), name="add_category"),
    path('categories/<str:slug>', ListProductCategoryView.as_view(), name="categories"),

    path('add_sub_category/<str:slug>', AddProductSubCategoryView.as_view(), name="add_sub_category"),
    path('sub_categories/<str:slug>', ListProductSubCategoryView.as_view(), name="sub_categories"),

    path('add_color/<str:slug>', AddProductColorView.as_view(), name="add_color"),
    path('colors/<str:slug>', ListProductColorView.as_view(), name="colors"),

    # Education Company
    path('add_course/<str:slug>', AddCourseView.as_view(), name="add_course"),
    path('courses/<str:slug>', CourseListView.as_view(), name="courses"),

    path('course_programs/<str:slug>', CourseProgramListView.as_view(), name="course_programs"),

    # Directory

    path('post_offices/', ListPostOfficeView.as_view(), name="post_offices"),

    path('banks/', ListBankView.as_view(), name="banks"),

    path('courts/', ListCourtView.as_view(), name="courts"),

    path('police_stations/', ListPoliceStationView.as_view(), name="police_stations"),
]
