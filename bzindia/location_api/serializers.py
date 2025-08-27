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


class DistrictMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniqueDistrict
        fields = ["name", "slug", "updated"]


class StateSerializer(serializers.ModelSerializer):
    districts = DistrictMiniSerializer(many=True, read_only = True)

    class Meta:
        model = UniqueState
        fields = ["name", "slug", "districts", "updated"]


class PlaceMiniSerializer(serializers.ModelSerializer):    
    class Meta:
        model = UniquePlace
        fields = ["name", "slug", "updated"]

        
class DistrictSerializer(serializers.ModelSerializer):
    places = PlaceMiniSerializer(many=True, read_only = True)
    state = StateSerializer()
    slug = serializers.SlugField()

    class Meta:
        model = UniqueDistrict
        fields = ["name", "slug", "state", "places", "updated"]    


class PlaceSerializer(serializers.ModelSerializer):
    state = StateSerializer()
    district = DistrictSerializer()
    coordinates = PlaceCoordinateSerializer(many=True, read_only=True)
    pincodes = PlacePincodeSerializer(many=True, read_only=True)

    class Meta:
        model = UniquePlace
        fields = ["name", "pincodes", "coordinates", "slug", "state", "district", "updated"]



class SimplePlaceSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()
    coordinates = PlaceCoordinateSerializer(many=True, read_only=True)
    pincodes = PlacePincodeSerializer(many=True)

    class Meta:
        model = UniquePlace
        fields = ["name", "slug", "district", "coordinates", "pincodes", "updated"]
