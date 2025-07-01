from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import (
    GetNearbyLocationsViewSet, StateViewset,
    StateCourseMultiPageViewSet, DistrictViewset, GetNearestLocationViewSet,
    StateRegistrationMultiPageViewSet, PlaceViewset, LocationMatchViewSet,
    StateProductMultiPageViewSet, StateServiceMultiPageViewSet,
    StateDistrictsViewSet, DistrictPlacesViewset, GetNearbyCscCentersViewSet,
    PopularCityViewSet
    )

app_name = "location_api"

router = DefaultRouter()

# router.register(r'get_places', PlaceApiViewset, basename="places")
router.register(r'states', StateViewset, basename="state")
router.register(r'districts', DistrictViewset, basename="district")
router.register(r'places', PlaceViewset, basename="place")
router.register(r'nearby_locations', GetNearbyLocationsViewSet, basename="location")
router.register(r'nearby_csc_centers', GetNearbyCscCentersViewSet, basename="csc_center")
router.register(r'get_location', LocationMatchViewSet, basename="get_location")
router.register(r'popular_cities', PopularCityViewSet, basename="popular_city")

states_router = NestedDefaultRouter(router, r'states', lookup="state")

states_router.register(r'course_multipages', StateCourseMultiPageViewSet, basename="state-course_multipage")
states_router.register(r'registration_multipages', StateRegistrationMultiPageViewSet, basename="state-registration_multipage")
states_router.register(r'product_multipages', StateProductMultiPageViewSet, basename="state-product_multipage")
states_router.register(r'service_multipages', StateServiceMultiPageViewSet, basename="state-service_multipage")
states_router.register(r'districts', StateDistrictsViewSet, basename="state-district")

districts_router = NestedDefaultRouter(router, r'districts', lookup="district")

districts_router.register(r'places', DistrictPlacesViewset, basename="district-place")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(states_router.urls)),
    path('', include(districts_router.urls)),
    path('nearest_place/', GetNearestLocationViewSet.as_view({"get":"get"}))
]
