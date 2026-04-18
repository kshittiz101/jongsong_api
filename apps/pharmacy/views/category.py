from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from ..models import Category
from ..serializers import CategorySerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["categories"])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
