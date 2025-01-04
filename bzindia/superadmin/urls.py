from django.urls import path
from .views import (
    HomeView, CompanyListView, AddCompanyView, UpdateCompanyView, DeleteCompanyView,
    CompanyDetailView,
    CompanyTypeListView, AddCompanyTypeView, DeleteCompanyTypeView, UpdateCompanyTypeView,
    ListProductView, AddProductView,
    ListBrandView, AddBrandView,
    ListProductCategoryView, AddProductCategoryView,
    ListProductSubCategoryView, AddProductSubCategoryView,
    ListProductColorView, AddProductColorView,

    # Educational Company
    AddCourseView, CourseListView, RemoveCourseView, UpdateCourseView,
    CourseProgramListView, AddCourseProgramView, RemoveCourseProgramView, UpdateCourseProgramView,
    CourseSpecializationListView, AddCourseSpecializationView, RemoveCourseSpecializationView, UpdateCourseSpecializationView,

    # Service Company
    ListServiceView, AddServiceView, RemoveServiceView, UpdateServiceView,
    ListServiceCategoryView, AddServiceCategoryView, RemoveServiceCategoryView, UpdateServiceCategoryView,
    ListServiceSubCategoryView, AddServiceSubCategoryView, RemoveServiceSubCategoryView, UpdateServiceSubCategoryView,

    # Registration Company
    ListRegistrationView, AddRegistrationView, RemoveRegistrationView, UpdateRegistrationView,
    ListRegistrationTypeView, AddRegistrationTypeView, RemoveRegistrationTypeView, UpdateRegistrationTypeView,
    ListRegistrationSubTypeView, AddRegistrationSubTypeView, RemoveRegistrationSubTypeView, UpdateRegistrationSubTypeView,

    ListPostOfficeView, ListBankView, ListCourtView, ListPoliceStationView, ListTouristAttractionView,

    CompanyView
    )

app_name = "superadmin"

urlpatterns = [
    path('', HomeView.as_view(), name="home"),

    path('companies/', CompanyView.as_view(), name="companies"),

    # Company
    path('add_company/', AddCompanyView.as_view(), name="add_company"),
    path('update_company/<str:slug>', UpdateCompanyView.as_view(), name="update_company"),
    path('delete_company/<str:slug>', DeleteCompanyView.as_view(), name="delete_company"),
    # path('companies/', CompanyListView.as_view(), name="companies"),
    path('companies/<str:slug>', CompanyListView.as_view(), name="filtered_companies"),

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
    path('remove_course/<str:slug>/<str:course_slug>/', RemoveCourseView.as_view(), name="remove_course"),
    path('update_course/<str:slug>/<str:course_slug>/', UpdateCourseView.as_view(), name="update_course"),

    path('course_programs/<str:slug>', CourseProgramListView.as_view(), name="course_programs"),
    path('add_course_program/<str:slug>', AddCourseProgramView.as_view(), name="add_course_program"),
    path('remove_course_program/<str:slug>/<str:program_slug>/', RemoveCourseProgramView.as_view(), name="remove_course_program"),
    path('update_course_program/<str:slug>/<str:program_slug>/', UpdateCourseProgramView.as_view(), name="update_course_program"),

    path('course_specializations/<str:slug>', CourseSpecializationListView.as_view(), name="course_specializations"),
    path('add_course_specialization/<str:slug>', AddCourseSpecializationView.as_view(), name="add_course_specialization"),
    path('remove_course_specialization/<str:slug>/<str:specialization_slug>/', RemoveCourseSpecializationView.as_view(), name="remove_course_specialization"),
    path('update_course_specialization/<str:slug>/<str:specialization_slug>/', UpdateCourseSpecializationView.as_view(), name="update_course_specialization"),

    # Service Company
    path('companies/services/<str:slug>', ListServiceView.as_view(), name="services"),
    path('companies/add_service/<str:slug>', AddServiceView.as_view(), name="add_service"),
    path('remove_service/<str:slug>/<str:category_slug>/', RemoveServiceView.as_view(), name="remove_service"),
    path('update_service/<str:slug>/<str:service_slug>/', UpdateServiceView.as_view(), name="update_service"),
    
    path('companies/service_categories/<str:slug>', ListServiceCategoryView.as_view(), name="service_categories"),
    path('companies/add_service_category/<str:slug>', AddServiceCategoryView.as_view(), name="add_service_category"),
    path('remove_service_category/<str:slug>/<str:category_slug>/', RemoveServiceCategoryView.as_view(), name="remove_service_category"),
    path('update_service_category/<str:slug>/<str:category_slug>/', UpdateServiceCategoryView.as_view(), name="update_service_category"),

    path('companies/service_sub_categories/<str:slug>', ListServiceSubCategoryView.as_view(), name="service_sub_categories"),
    path('companies/add_service_sub_category/<str:slug>', AddServiceSubCategoryView.as_view(), name="add_service_sub_category"),
    path('remove_service_sub_category/<str:slug>/<str:sub_category_slug>/', RemoveServiceSubCategoryView.as_view(), name="remove_service_sub_category"),
    path('update_service_sub_category/<str:slug>/<str:sub_category_slug>/', UpdateServiceSubCategoryView.as_view(), name="update_service_sub_category"),

    # Registration Company
    path('companies/registrations/<str:slug>', ListRegistrationView.as_view(), name="registrations"),
    path('companies/add_registration/<str:slug>', AddRegistrationView.as_view(), name="add_registration"),
    path('companies/remove_registration/<str:slug>/<str:registration_slug>/', RemoveRegistrationView.as_view(), name="remove_registration"),
    path('update_registration/<str:slug>/<str:registration_slug>/', UpdateRegistrationView.as_view(), name="update_registration"),

    path('companies/registration_types/<str:slug>', ListRegistrationTypeView.as_view(), name="registration_types"),
    path('companies/add_registration_type/<str:slug>', AddRegistrationTypeView.as_view(), name="add_registration_type"),
    path('companies/remove_registration_type/<str:slug>/<str:registration_type_slug>/', RemoveRegistrationTypeView.as_view(), name="remove_registration_type"),
    path('update_registration_type/<str:slug>/<str:registration_type_slug>/', UpdateRegistrationTypeView.as_view(), name="update_registration_type"),

    path('companies/registration_sub_types/<str:slug>', ListRegistrationSubTypeView.as_view(), name="registration_sub_types"),
    path('companies/add_registration_sub_types/<str:slug>', AddRegistrationSubTypeView.as_view(), name="add_registration_sub_types"),
    path('companies/remove_registration_sub_type/<str:slug>/<str:registration_sub_type_slug>/', RemoveRegistrationSubTypeView.as_view(), name="remove_registration_sub_type"),
    path('update_registration_sub_type/<str:slug>/<str:registration_sub_type_slug>/', UpdateRegistrationSubTypeView.as_view(), name="update_registration_sub_type"),

    # Directory

    path('post_offices/', ListPostOfficeView.as_view(), name="post_offices"),

    path('banks/', ListBankView.as_view(), name="banks"),

    path('courts/', ListCourtView.as_view(), name="courts"),

    path('police_stations/', ListPoliceStationView.as_view(), name="police_stations"),

    path('tourist_attractions/', ListTouristAttractionView.as_view(), name="tourist_attractions"),
]
