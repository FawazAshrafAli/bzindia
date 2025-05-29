from rest_framework import viewsets, status
from rest_framework.response import  Response
from rest_framework.decorators import action

from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import Sqrt
from django.shortcuts import get_object_or_404

# from locations.trie_loader import place_trie, district_trie, state_trie
from locations.trie_cache import get_place_trie, get_district_trie, get_state_trie

from .serializers import PlaceSerializer, StateSerializer, DistrictSerializer, SimplePlaceSerializer
from course_api.serializers import MultiPageSerializer
from registration_api.serializers import MultipageSerializer as RegistrationMultipageSerializer

from educational.models import MultiPage
from registration.models import MultiPage as RegistrationMultiPage
from locations.models import Place, UniqueState, UniqueDistrict, PlaceCoordinate, UniquePlace


import logging

logger = logging.getLogger(__name__)

# class PlaceApiViewset(viewsets.ModelViewSet):
#     serializer_class = PlaceSerializer
#     queryset = Place.objects.all()


class GetNearbyLocationsViewSet(viewsets.ModelViewSet):
    serializer_class = PlaceSerializer
    queryset = PlaceCoordinate.objects.none()

    def get_queryset(self):
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')

        if lat and lon:
            try:
                lat = float(lat)
                lon = float(lon)
            except (TypeError, ValueError):
                return PlaceCoordinate.objects.none()

            difference = 0.05

            start_lat = lat - difference
            start_lon = lon - difference

            end_lat = lat + difference
            end_lon = lon + difference

            starting_point = [start_lat, start_lon]
            ending_point = [end_lat, end_lon]

            unfiltered_places = PlaceCoordinate.objects.filter(
                latitude__range=(starting_point[0], ending_point[0]),
                longitude__range=(starting_point[1], ending_point[1])
            )

            unique_places_dict = dict()
            for place_obj in unfiltered_places:
                unique_places_dict[place_obj.place.name] = place_obj.place.slug

            return UniquePlace.objects.filter(slug__in = unique_places_dict.values())
        
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

class DistrictViewset(viewsets.ReadOnlyModelViewSet):
    queryset = UniqueDistrict.objects.all().order_by("name")
    serializer_class = DistrictSerializer
    lookup_field = "slug"

class PlaceViewset(viewsets.ReadOnlyModelViewSet):
    queryset = UniquePlace.objects.all().order_by("name")
    serializer_class = SimplePlaceSerializer
    lookup_field = "slug"

class StateCourseMultiPageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MultiPageSerializer
    lookup_field = "slug"

    def get_queryset(self):
        slug = self.kwargs.get("state_slug")

        if not slug:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Slug was not provided"})

        state = get_object_or_404(UniqueState, slug=slug)

        return MultiPage.objects.filter(available_states=state)
    

class StateRegistrationMultiPageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegistrationMultipageSerializer
    lookup_field = "slug"

    def get_queryset(self):
        slug = self.kwargs.get("state_slug")

        if not slug:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Slug was not provided"})

        state = get_object_or_404(UniqueState, slug=slug)

        return RegistrationMultiPage.objects.filter(available_states=state)


# MATCH_ORDER = [
#     ("state", state_trie, UniqueState, StateSerializer),
#     ("district", district_trie, UniqueDistrict, DistrictSerializer),
#     ("place", place_trie, UniquePlace, PlaceSerializer),
# ]

MATCH_ORDER = [
    ("state", get_state_trie, UniqueState, StateSerializer),
    ("district", get_district_trie, UniqueDistrict, DistrictSerializer),
    ("place", get_place_trie, UniquePlace, PlaceSerializer),
]

class LocationMatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UniquePlace.objects.none()
    serializer_class = PlaceSerializer

    def retrieve(self, request, pk=None):        
        slug = pk 

        # for model_type, trie, model, serializer_class in MATCH_ORDER:
        for model_type, get_trie_fn, model, serializer_class in MATCH_ORDER:
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