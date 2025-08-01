# bangazonapi/views/store.py

from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework import status
from bangazonapi.models import Store, Customer, Favorite
from django.contrib.auth.models import User
from .product import ProductSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action


class StoreSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    products = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = ("id", "name", "description", "owner", "products", "is_favorited")

    def get_products(self, store):
        products = store.products.filter(quantity__gt=0)
        return ProductSerializer(products, many=True, context=self.context).data
    
    def get_is_favorited(self, store):
        user = self.context['request'].user
        try:
            customer = Customer.objects.get(user=user)
            seller = Customer.objects.get(user=store.owner)
            return Favorite.objects.filter(customer=customer, seller=seller).exists()
        except Customer.DoesNotExist:
            return False



class StoreViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request):
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True, context={"request": request})
        return Response(serializer.data)

    def create(self, request):
        user = request.auth.user

        if Store.objects.filter(owner=user).exists():
            return Response(
                {"message": "User already has a store."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        new_store = Store.objects.create(
            name=request.data["name"],
            description=request.data["description"],
            owner=user,
        )

        serializer = StoreSerializer(new_store, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            store = Store.objects.get(pk=pk)
            serializer = StoreSerializer(store, context={"request": request})
            return Response(serializer.data)
        except Store.DoesNotExist:
            return Response(
                {"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_store(self, request):
        """Returns current user's store with Selling and Sold product lists"""

        user = request.auth.user
        try:
            store = Store.objects.get(owner=user)
        except Store.DoesNotExist:
            return Response(
                {"message": "No store found for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        selling = store.products.filter(quantity__gt=0)
        sold = store.products.filter(
            lineitems__order__payment_type__isnull=False
        ).distinct()

        selling_serialized = ProductSerializer(
            selling, many=True, context={"request": request}
        ).data
        sold_serialized = ProductSerializer(
            sold, many=True, context={"request": request}
        ).data

        return Response(
            {
                "store": {
                    "id": store.id,
                    "name": store.name,
                    "description": store.description,
                },
                "selling": selling_serialized,
                "sold": sold_serialized,
            }
        )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        user = request.user
        try:
            customer = Customer.objects.get(user=user)
        except Customer.DoesNotExist:
            return Response({"message": "Customer not found"}, status=404)

        try:
            store = Store.objects.get(pk=pk)
            seller_user = store.owner
            seller = Customer.objects.get(user=seller_user)
            Favorite.objects.create(customer=customer, seller=seller)
            return Response({"message": "Store favorited"}, status=201)
        except Store.DoesNotExist:
            return Response({"message": "Store not found"}, status=404)
        except Customer.DoesNotExist:
            return Response({"message": "Seller not found"}, status=404)


    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def unfavorite(self, request, pk=None):
        user = request.user
        try:
            customer = Customer.objects.get(user=user)
        except Customer.DoesNotExist:
            return Response({"message": "Customer not found"}, status=404)

        try:
            store = Store.objects.get(pk=pk)
            seller_user = store.owner
            seller = Customer.objects.get(user=seller_user)
            
            favorite = Favorite.objects.get(customer=customer, seller=seller)
            favorite.delete()
            
            return Response({"message": "Store unfavorited"}, status=204)
        except Store.DoesNotExist:
            return Response({"message": "Store not found"}, status=404)
        except Customer.DoesNotExist:
            return Response({"message": "Seller not found"}, status=404)
        except Favorite.DoesNotExist:
            return Response({"message": "Favorite not found"}, status=404)
