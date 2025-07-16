"""View module for handling requests about line items"""

from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from bangazonapi.models import OrderProduct, Order, Product, Customer


class LineItemSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for line items"""

    class Meta:
        model = OrderProduct
        url = serializers.HyperlinkedIdentityField(
            view_name="lineitem", lookup_field="id"
        )
        fields = ("id", "url", "order", "product")


class LineItems(ViewSet):
    """Line items for Bangazon orders"""

    # TIP: By setting this class attribute, then a `basename` parameter
    #      does not need to be set on the route in urls.py:11 and allow
    #      the serializer (see above) use the `view_name='lineitem'`
    #      argument for the HyperlinkedIdentityField. If this is NOT set
    #      then the following exception gets thrown.
    #
    # ImproperlyConfigured at /lineitems/4
    #   Could not resolve URL for hyperlinked relationship using view name
    #   "orderproduct-detail". You may have failed to include the related
    #   model in your API, or incorrectly configured the `lookup_field`
    #   attribute on this field.
    # queryset = OrderProduct.objects.all()
    def create(self, request):
        """Add a product to the customer's open order (cart)"""
        customer = Customer.objects.get(user=request.auth.user)
        product_id = request.data.get("product_id")

        if product_id is None:
            return Response({"message": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.get(pk=product_id)

        # Find or create the open order
        open_order, created = Order.objects.get_or_create(
            customer=customer,
            payment_type=None  # This means it's still in cart
        )

        # Create the line item
        OrderProduct.objects.create(order=open_order, product=product)

        return Response({"message": "Product added to order."}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        @api {GET} /cart/:id DELETE line item from cart
        @apiName RemoveLineItem
        @apiGroup ShoppingCart

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Product Id to remove from cart
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            # line_item = OrderProduct.objects.get(pk=pk)
            customer = Customer.objects.get(user=request.auth.user)
            line_item = OrderProduct.objects.get(pk=pk, order__customer=customer)

            serializer = LineItemSerializer(line_item, context={"request": request})

            return Response(serializer.data)

        except OrderProduct.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /cart/:id DELETE line item from cart
        @apiName RemoveLineItem
        @apiGroup ShoppingCart

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Product Id to remove from cart
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            customer = Customer.objects.get(user=request.auth.user)
            order_product = OrderProduct.objects.get(pk=pk, order__customer=customer)

            order_product.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except OrderProduct.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
