from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from bangazonapi.models import Recommendation, Customer, Product
from bangazonapi.views.profile import ProfileProductSerializer

class RecommendationSerializer(serializers.ModelSerializer):
    product = ProfileProductSerializer()

    class Meta:
        model = Recommendation
        fields = ('id', 'product', 'recommender')

class RecommendationViewSet(viewsets.ViewSet):
    serializer_class = RecommendationSerializer

    @action(detail=False, methods=['post'])
    def recommend(self, request):
        to_username = request.data.get('to_username')
        product_id = request.data.get('product_id')
        try:
            to_user = User.objects.get(username=to_username)
            to_customer = Customer.objects.get(user=to_user)
            product = Product.objects.get(pk=product_id)
            recommender = Customer.objects.get(user=request.user)
            Recommendation.objects.create(
                customer=to_customer,
                product=product,
                recommender=recommender
            )
            return Response({'message': 'Recommendation sent!'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)