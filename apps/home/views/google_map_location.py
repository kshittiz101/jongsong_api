# views.py
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from ..models import Location
from ..serializers import LocationSerializer


class LocationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Location.objects.all().order_by('-created_at')
    serializer_class = LocationSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class LocationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
