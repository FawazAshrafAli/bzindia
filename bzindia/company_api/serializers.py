from rest_framework import serializers

from company.models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["name", "type", "slug", "favicon", "logo", "phone1", "phone2", "whatsapp", "email"]