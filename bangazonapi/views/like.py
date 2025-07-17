from rest_framework import serializers
from bangazonapi.models import Like, Product
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class LikeSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Like
        fields = ['id', 'user', 'product', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class Likes(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(methods=['post'], detail=True)
    def like(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, product=product)
        if created:
            return Response({'message': 'Product liked'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Already liked'}, status=status.HTTP_200_OK)
    
    @action(methods=['delete'], detail=True)
    def del_like(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        try:
            like = Like.objects.get(user=request.user, product=product)
            like.delete()
            return Response({'message': 'Like removed'}, status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response({'message': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(methods=['get'], detail=False, url_path='liked')
    def liked(self, request):
        """GET /products/liked"""
        likes = Like.objects.filter(user=request.user)
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)