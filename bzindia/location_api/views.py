from rest_framework import viewsets, status
from rest_framework.response import  Response
from rest_framework.decorators import action

from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import Sqrt
from django.shortcuts import get_object_or_404
from django.http import Http404

from locations.trie_cache import get_place_trie, get_district_trie, get_state_trie

from .serializers import (
    PlaceSerializer, StateSerializer, DistrictSerializer, SimplePlaceSerializer, 
    PlaceCoordinateSerializer, PlacePincodeSerializer
    )
from course_api.serializers import MultiPageSerializer
from registration_api.serializers import MultipageSerializer as RegistrationMultipageSerializer
from product_api.serializers import MultiPageSerializer as ProductMultipageSerializer
from service_api.serializers import MultipageSerializer as ServiceMultipageSerializer
from directory_api.serializers import CscCenterSerializer

from educational.models import MultiPage
from registration.models import MultiPage as RegistrationMultiPage
from product.models import MultiPage as ProductMultiPage
from service.models import MultiPage as ServiceMultiPage
from directory.models import CscCenter
from locations.models import (
    UniqueState, UniqueDistrict, PlaceCoordinate, UniquePlace, PlacePincode
)

from service_api.paginations import ServiceMultipagePagination
from product_api.paginations import ProductMultipagePagination
from course_api.paginations import CourseMultipagePagination
from registration_api.paginations import RegistrationMultipagePagination

from rest_framework.decorators import action

from utility.location import get_nearby_locations

import logging

logger = logging.getLogger(__name__)

class GetNearbyLocationsViewSet(viewsets.ModelViewSet):
    serializer_class = PlaceSerializer
    queryset = UniquePlace.objects.none()

    def get_queryset(self):
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')

        if lat and lon:
            locations = get_nearby_locations(lat, lon)

            return locations if locations else UniquePlace.objects.none()

            # try:
            #     lat = float(lat)
            #     lon = float(lon)
            # except (TypeError, ValueError):
            #     return PlaceCoordinate.objects.none()

            # difference = 0.05

            # start_lat = lat - difference
            # start_lon = lon - difference

            # end_lat = lat + difference
            # end_lon = lon + difference

            # starting_point = [start_lat, start_lon]
            # ending_point = [end_lat, end_lon]

            # unfiltered_places = PlaceCoordinate.objects.filter(
            #     latitude__range=(starting_point[0], ending_point[0]),
            #     longitude__range=(starting_point[1], ending_point[1])
            # )

            # unique_places_dict = dict()
            # for place_obj in unfiltered_places:
            #     unique_places_dict[place_obj.place.name] = place_obj.place.slug

            # return UniquePlace.objects.filter(slug__in = unique_places_dict.values())
        
        return UniquePlace.objects.none()
    

class GetNearestLocationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlaceSerializer
    queryset = PlaceCoordinate.objects.none()

    def get(self, request, *args, **kwargs):
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')

        if not lat or not lon:
            return Response({"place": "Not provided latitude and longitude"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            return Response({"place": "Provided values are not coordinates"}, status=status.HTTP_400_BAD_REQUEST)
            
        nearest_place = PlaceCoordinate.objects.annotate(
            distance=ExpressionWrapper(
                Sqrt((F('latitude') - lat) ** 2 + (F('longitude') - lon) ** 2),
                output_field=FloatField()
                )
            ).order_by('distance').first()
        
        place = nearest_place.place
        
        serializer = self.get_serializer(place)

        return Response(serializer.data, status=status.HTTP_200_OK)


class StateViewset(viewsets.ReadOnlyModelViewSet):
    queryset = UniqueState.objects.all().order_by("name")
    serializer_class = StateSerializer
    lookup_field = "slug"

    @action(methods=["GET"], detail=True)
    def get_center(self, request, slug=None):
        state = self.get_object()

        if not state:
            return Response({"center": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

        coordinates = list(
            PlaceCoordinate.objects.filter(place__state=state)
            .order_by("id")
            .values("latitude", "longitude", "id")
        )

        if not coordinates:
            return Response({"center": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        index_of_center_obj = len(coordinates) // 2
        center_point = coordinates[index_of_center_obj]

        center_obj = PlaceCoordinate.objects.filter(
            latitude=center_point["latitude"], longitude=center_point["longitude"]
        ).first()

        if not center_obj:
            return Response({"center": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PlaceCoordinateSerializer(center_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=True)
    def get_pincode(self, request, slug=None):
        state = self.get_object()

        if not state:
            return Response({"pincode": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

        coordinates = list(
            PlaceCoordinate.objects.filter(place__state=state)
            .order_by("id")
            .values("latitude", "longitude", "id")
        )

        if not coordinates:
            return Response({"pincode": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        index_of_center_obj = len(coordinates) // 2
        center_point = coordinates[index_of_center_obj]

        center_obj = PlaceCoordinate.objects.filter(
            latitude=center_point["latitude"], longitude=center_point["longitude"]
        ).first()

        pincode_obj = PlacePincode.objects.filter(place = center_obj.place).first()

        if not center_obj and not pincode_obj:
            return Response({"center": "Not found"}, status=status.HTTP_404_NOT_FOUND)        

        serializer = PlacePincodeSerializer(pincode_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DistrictViewset(viewsets.ReadOnlyModelViewSet):
    queryset = UniqueDistrict.objects.all().order_by("name")
    serializer_class = DistrictSerializer
    lookup_field = "slug"

    @action(methods=["GET"], detail=True)
    def get_center(self, request, slug=None):
        district = self.get_object()

        if not district:
            return Response({"center": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

        coordinates = list(
            PlaceCoordinate.objects.filter(place__district=district)
            .order_by("latitude", "longitude")
            .values("latitude", "longitude", "id")
        )

        if not coordinates:
            return Response({"center": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        index_of_center_obj = len(coordinates) // 2
        center_point = coordinates[index_of_center_obj]

        center_obj = PlaceCoordinate.objects.filter(
            latitude=center_point["latitude"], longitude=center_point["longitude"]
        ).first()

        if not center_obj:
            return Response({"center": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PlaceCoordinateSerializer(center_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=["GET"], detail=True)
    def get_pincode(self, request, slug=None):
        district = self.get_object()

        if not district:
            return Response({"pincode": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
        
        pincode_obj = PlacePincode.objects.filter(place__name = district.name).first()

        if pincode_obj:
            serializer = PlacePincodeSerializer(pincode_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        coordinates = list(
            PlaceCoordinate.objects.filter(place__district=district)
            .order_by("latitude", "longitude")
            .values("latitude", "longitude", "id")
        )

        if not coordinates:
            return Response({"pincode": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        index_of_center_obj = len(coordinates) // 2
        center_point = coordinates[index_of_center_obj]

        center_obj = PlaceCoordinate.objects.filter(
            latitude=center_point["latitude"], longitude=center_point["longitude"]
        ).first()

        pincode_obj = PlacePincode.objects.filter(place = center_obj.place).first()

        if not center_obj and not pincode_obj:
            return Response({"center": "Not found"}, status=status.HTTP_404_NOT_FOUND) 

        serializer = PlacePincodeSerializer(pincode_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StateDistrictsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DistrictSerializer

    def get_queryset(self):
        state_slug = self.kwargs.get("state_slug")

        if state_slug:
            return UniqueDistrict.objects.filter(state__slug = state_slug)
        
        return UniqueDistrict.objects.none()


class PlaceViewset(viewsets.ReadOnlyModelViewSet):
    queryset = UniquePlace.objects.all().order_by("name")
    serializer_class = SimplePlaceSerializer
    lookup_field = "slug"

    @action(methods=["GET"], detail=True)
    def get_center(self, request, slug=None):
        place = self.get_object()

        if not place:
            return Response({"center": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

        coordinates = list(
            PlaceCoordinate.objects.filter(place=place)
            .order_by("id")
            .values("latitude", "longitude", "id")
        )

        if not coordinates:
            return Response({"center": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        index_of_center_obj = len(coordinates) // 2
        center_point = coordinates[index_of_center_obj]



        center_obj = PlaceCoordinate.objects.filter(
            latitude=center_point["latitude"], longitude=center_point["longitude"]
        ).first()

        if not center_obj:
            return Response({"center": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PlaceCoordinateSerializer(center_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DistrictPlacesViewset(viewsets.ReadOnlyModelViewSet):
    queryset = UniquePlace.objects.all().order_by("name")
    serializer_class = SimplePlaceSerializer

    def get_queryset(self):
        district_slug = self.kwargs.get("district_slug")

        if district_slug:
            return UniquePlace.objects.filter(district__slug = district_slug)
        
        return UniquePlace.objects.none()


class StateCourseMultiPageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MultiPageSerializer
    lookup_field = "slug"
    pagination_class = CourseMultipagePagination

    def get_queryset(self):
        slug = self.kwargs.get("state_slug")

        if not slug:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Slug was not provided"})
        
        if slug == "all" or slug == "india":
            return MultiPage.objects.all()

        state = get_object_or_404(UniqueState, slug=slug)

        return MultiPage.objects.filter(available_states=state)
    

class StateRegistrationMultiPageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegistrationMultipageSerializer
    lookup_field = "slug"
    pagination_class = RegistrationMultipagePagination

    def get_queryset(self):
        slug = self.kwargs.get("state_slug")

        if not slug:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Slug was not provided"})
        
        if slug == "all" or slug == "india":
            return RegistrationMultiPage.objects.all()

        state = get_object_or_404(UniqueState, slug=slug)

        return RegistrationMultiPage.objects.filter(available_states=state)
    

class StateProductMultiPageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductMultipageSerializer
    lookup_field = "slug"
    pagination_class = ProductMultipagePagination

    def get_queryset(self):
        slug = self.kwargs.get("state_slug")
        category = self.request.query_params.get("category")

        if not slug:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Slug was not provided"})
        
        if slug == "all" or slug == "india":
            return ProductMultiPage.objects.all()

        state = get_object_or_404(UniqueState, slug=slug)

        return ProductMultiPage.objects.filter(available_states=state)


MATCH_ORDER = [
    ("state", get_state_trie, UniqueState, StateSerializer),
    ("district", get_district_trie, UniqueDistrict, DistrictSerializer),
    ("place", get_place_trie, UniquePlace, PlaceSerializer),
]

class LocationMatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UniquePlace.objects.none()
    serializer_class = PlaceSerializer

    def retrieve(self, request, *args, **kwargs):        
        slug = self.kwargs.get("slug")
        location_type = self.kwargs.get("location_type")        

        for model_type, get_trie_fn, model, serializer_class in MATCH_ORDER:
            if location_type and location_type != "undefined" and model_type != location_type:
                continue
            trie = get_trie_fn()
            matched_slug = trie.match_suffix(slug)
            if matched_slug:
                try:
                    instance = model.objects.get(slug=matched_slug)
                    serializer = serializer_class(instance)
                    return Response({
                        "match_type": model_type,
                        "data": serializer.data
                    })
                except model.DoesNotExist:
                    return Response({
                        "match_type": model_type,
                        "matched_slug": matched_slug,
                        "warning": "Slug matched in trie but not found in DB."
                    })                                            

        return Response({"match_type": None, "matched_slug": None})
    

class StateServiceMultiPageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ServiceMultipageSerializer
    lookup_field = "slug"
    pagination_class = ServiceMultipagePagination

    def get_queryset(self):
        slug = self.kwargs.get("state_slug")

        if not slug:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Slug was not provided"})

        if slug == "all" or slug == "india":
            return ServiceMultiPage.objects.all()

        state = get_object_or_404(UniqueState, slug=slug)

        return ServiceMultiPage.objects.filter(available_states=state)
    

class GetNearbyCscCentersViewSet(viewsets.ModelViewSet):
    serializer_class = CscCenterSerializer
    queryset = CscCenter.objects.none()

    def get_queryset(self):
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')

        if lat and lon:
            try:
                lat = float(lat)
                lon = float(lon)
            except (TypeError, ValueError):
                return CscCenter.objects.none()

            difference = 0.05

            start_lat = lat - difference
            start_lon = lon - difference

            end_lat = lat + difference
            end_lon = lon + difference

            starting_point = [start_lat, start_lon]
            ending_point = [end_lat, end_lon]

            centers = CscCenter.objects.filter(
                latitude__range=(starting_point[0], ending_point[0]),
                longitude__range=(starting_point[1], ending_point[1])
            )

            # unique_centers_dict = dict()
            # for center_obj in unfiltered_centers:
            #     unique_centers_dict[center_obj.center.name] = center_obj.center.slug

            # return UniquePlace.objects.filter(slug__in = unique_centers_dict.values())
        
        return CscCenter.objects.none()


class PopularCityViewSet(viewsets.ModelViewSet):
    serializer_class = PlaceSerializer 

    def get_queryset(self):

        popular_cities = [
            "Mumbai", "Bengaluru", "Hyderabad", "Kolkata", "Chennai", "Pune", "Ahmedabad", "Surat", 
            "Jaipur", "Lucknow", "Kanpur", "Indore", "Patna", "Nagpur", "Visakhapatnam", "Meerut", 
            "Bhopal", "Varanasi", "Agra", "Nashik", "Vijayawada", "Guwahati", "Rajkot", "Warangal", 
            "Coimbatore", "Thiruvananthapuram", "Faridabad", "Ghaziabad", "Chandigarh", "Ludhiana", 
            "Vadodara", "Raipur", "Jodhpur", "Mangalore", "Gwalior", "Tiruchirappalli", "Jamshedpur", 
            "Ranchi", "Prayagraj", "Jalandhar", "Jabalpur", "Chhatrapati Sambhaji Nagar", "Bhubaneswar", 
            "Asansol", "Gurugram", "Mysuru", "Noida", "Kochi", "Amritsar", "Saharanpur"
            ]

        place_objs = []
        for place in popular_cities:
            place_obj = None

            try:
                place_obj = UniquePlace.objects.get(name=place)
            except UniquePlace.MultipleObjectsReturned:
                place_obj = UniquePlace.objects.filter(name=place, district__name=place).order_by('created').first()
                if not place_obj:
                    place_obj = UniquePlace.objects.filter(name=place).order_by('created').first()
            except UniquePlace.DoesNotExist:
                pass

            if place_obj:
                place_objs.append(place_obj)        


        return place_objs


