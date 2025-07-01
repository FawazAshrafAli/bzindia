from rest_framework import serializers
from utility.text import clean_string

from .models import Enquiry, UniqueState

class EnquirySerializer(serializers.ModelSerializer):    

    state = serializers.SlugRelatedField(
        queryset = UniqueState.objects.all(),
        slug_field = 'slug'
    )

    phone = serializers.RegexField(
        regex=r'^\+?1?\d{9,15}$',
        error_messages={
            'invalid': 'Phone number must be between 9 and 15 digits.'
        }
    )    

    class Meta:
        model = Enquiry
        fields = ["name", "phone", "email", "state", "comment", "company_sub_type"]

    def validate(self, data):
        cleaned_data = {}
        for field in ['name', 'phone', 'email', 'comment']:
            value = clean_string(data.get(field, ''))
            if not value:
                raise serializers.ValidationError({field: f"{field.capitalize()} is required"})
            cleaned_data[field] = value

        if not data.get("state"):
            raise serializers.ValidationError({"state": "State is required"})

        data.update(cleaned_data)
        return data