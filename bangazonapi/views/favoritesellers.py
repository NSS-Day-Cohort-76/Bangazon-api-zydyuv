from rest_framework.decorators import action
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from bangazonapi.models import Favorite, Customer



class SellerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name"]


class SellerSerializer(serializers.ModelSerializer):
    user = SellerUserSerializer()

    class Meta:
        model = Customer
        fields = ["id", "user", "store_name"]


class FavoriteSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(read_only=True)
    seller_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        source="seller",
        write_only=True
    )

    class Meta:
        model = Favorite
        fields = ["id", "seller", "seller_id"]


class FavoriteViewSet(viewsets.ViewSet):
    def get_customer(self, request):
        return Customer.objects.get(user=request.auth.user)

    def create(self, request):
        customer = self.get_customer(request)
        seller_id = request.data.get("store_id")

        if not seller_id:
            return Response({"message": "Missing store_id"}, status=status.HTTP_400_BAD_REQUEST)

        if int(seller_id) == customer.id:
            return Response({"message": "Cannot favorite yourself"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            seller = Customer.objects.get(pk=seller_id)
            favorite, created = Favorite.objects.get_or_create(customer=customer, seller=seller)
            if created:
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Already favorited"}, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({"message": "Seller not found"}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        customer = self.get_customer(request)
        favorites = Favorite.objects.filter(customer=customer)
        serializer = FavoriteSerializer(favorites, many=True, context={"request": request})
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        customer = self.get_customer(request)
        try:
            favorite = Favorite.objects.get(pk=pk, customer=customer)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response({"message": "Favorite not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["delete"], url_path="remove")
    def remove(self, request):
        """DELETE /favoritesellers/remove with store_id in body"""
        customer = self.get_customer(request)
        seller_id = request.data.get("store_id")

        if not seller_id:
            return Response({"message": "Missing store_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            seller = Customer.objects.get(pk=seller_id)
            favorite = Favorite.objects.get(customer=customer, seller=seller)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Customer.DoesNotExist:
            return Response({"message": "Seller not found"}, status=status.HTTP_404_NOT_FOUND)
        except Favorite.DoesNotExist:
            return Response({"message": "Favorite not found"}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=["post"], url_path="toggle")
    def toggle_favorite(self, request):
        customer = self.get_customer(request)
        store_id = request.data.get("store_id")

        if not store_id:
            return Response({"message": "Missing store_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from bangazonapi.models import Store
            store = Store.objects.get(pk=store_id)
            seller = Customer.objects.get(user=store.owner)

            favorite = Favorite.objects.filter(customer=customer, seller=seller).first()

            if favorite:
                favorite.delete()
                return Response({"message": "Unfavorited"}, status=status.HTTP_204_NO_CONTENT)
            else:
                Favorite.objects.create(customer=customer, seller=seller)
                return Response({"message": "Favorited"}, status=status.HTTP_201_CREATED)

        except Store.DoesNotExist:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        except Customer.DoesNotExist:
            return Response({"message": "Seller not found"}, status=status.HTTP_404_NOT_FOUND)