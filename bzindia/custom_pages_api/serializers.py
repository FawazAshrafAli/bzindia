from rest_framework import serializers

from custom_pages.models import FAQ, AboutUs, ContactUs

class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            "question", "answer", "slug"
        ]


class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = [
            "content", "slug"
        ]

class ContactUsSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(source="place.name", read_only=True)
    district_name = serializers.CharField(source="district.name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)

    class Meta:
        model = ContactUs
        fields = [
            "email", "phone", "provide_query", "place_name", "district_name",
            "state_name", "pincode", "facebook", "x", "youtube", 
            "instagram", "lat", "lon", "slug", "address"
        ]