from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import (
    GetNearbyLocationsViewSet, StateViewset,
    StateCourseMultiPageViewSet, DistrictViewset, GetNearestLocationViewSet,
    StateRegistrationMultiPageViewSet, PlaceViewset, LocationMatchViewSet
    )

app_name = "location_api"

router = DefaultRouter()

# router.register(r'get_places', PlaceApiViewset, basename="places")
router.register(r'states', StateViewset, basename="state")
router.register(r'districts', DistrictViewset, basename="district")
router.register(r'places', PlaceViewset, basename="place")
router.register(r'nearby_locations', GetNearbyLocationsViewSet, basename="location")
router.register(r'get_location', LocationMatchViewSet, basename="get_location")

states_router = NestedDefaultRouter(router, r'states', lookup="state")

states_router.register(r'course_multipages', StateCourseMultiPageViewSet, basename="state-course_multipage")
states_router.register(r'registration_multipages', StateRegistrationMultiPageViewSet, basename="state-registration_multipage")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(states_router.urls)),
    path('nearest_place/', GetNearestLocationViewSet.as_view({"get":"get"}))
]
