from rest_framework import serializers

from locations.models import UniquePlace, UniqueState, UniqueDistrict, PlaceCoordinate, PlacePincode

class PlaceCoordinateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceCoordinate
        fields = ["latitude", "longitude"]


class PlacePincodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacePincode
        fields = ["pincode"]


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniqueState
        fields = ["name", "slug"]

class DistrictSerializer(serializers.ModelSerializer):
    state = StateSerializer()
    slug = serializers.SlugField()

    class Meta:
        model = UniqueDistrict
        fields = ["name", "slug", "state"]

class PlaceSerializer(serializers.ModelSerializer):
    state = StateSerializer()
    district = DistrictSerializer()
    coordinates = PlaceCoordinateSerializer(many=True, read_only=True)
    pincodes = PlacePincodeSerializer(many=True, read_only=True)

    class Meta:
        model = UniquePlace
        fields = ["name", "pincodes", "coordinates", "slug", "state", "district"]


class SimplePlaceSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()    

    class Meta:
        model = UniquePlace
        fields = ["name", "slug", "district"]