from rest_framework import serializers

from directory.models import CscCenter

class CscCenterSerializer(serializers.ModelSerializer):
    place_name = serializers.SerializerMethodField(source = "place.name", read_only=True)
    district_name = serializers.SerializerMethodField(source = "district.name", read_only=True)
    state_name = serializers.SerializerMethodField(source = "state.name", read_only=True)

    model = CscCenter
    fields = [
        "csc_id", "name", "slug", "place_name", "district_name",
        "state_name"
    ]