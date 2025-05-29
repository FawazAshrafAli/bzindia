from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Enquiry
from .serializers import EnquirySerializer

class EnquiryViewSet(viewsets.ModelViewSet):
    queryset = Enquiry.objects.all()
    serializer_class = EnquirySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)

        data = {
            "success": False,
            "message": "Validation failed"
        }

        if serializer.is_valid():            
                
            serializer.save()

            data["success"] = True
            data["message"] = "Success! Enquiry Submitted"

            return Response(data, status=status.HTTP_201_CREATED)
        
        data["error"] = serializer.errors
        return Response(data, status=status.HTTP_400_BAD_REQUEST)