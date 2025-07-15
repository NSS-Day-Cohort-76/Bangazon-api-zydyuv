# bangazonapi/views/store.py

from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework import status
from bangazonapi.models import Store
from django.contrib.auth.models import User
from .product import ProductSerializer


class StoreSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = ("id", "name", "description", "owner", "products")

    def get_products(self, store):
        products = store.products.filter(quantity__gt=0)
        return ProductSerializer(products, many=True, context=self.context).data


class StoreViewSet(viewsets.ViewSet):
    def list(self, request):
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True, context={"request": request})
        return Response(serializer.data)
