"""View module for handling requests about customer order"""
import datetime
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import action
from bangazonapi.models import Order, Payment, Customer, Product, OrderProduct
from .product import ProductSerializer
from .paymenttype import PaymentSerializer


class OrderLineItemSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for line items """

    product = ProductSerializer(many=False)

    class Meta:
        model = OrderProduct
        url = serializers.HyperlinkedIdentityField(
            view_name='lineitem',
            lookup_field='id'
        )
        fields = ('id', 'product')
        depth = 1

class OrderSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for customer orders"""

    lineitems = OrderLineItemSerializer(many=True)
    payment_type = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        url = serializers.HyperlinkedIdentityField(
            view_name='order',
            lookup_field='id'
        )
        fields = ('id', 'url', 'created_date', 'payment_type', 'customer', 'lineitems')


class Orders(ViewSet):
    """View for interacting with customer orders"""

    def retrieve(self, request, pk=None):
        """
        @api {GET} /cart/:id GET single order
        @apiName GetOrder
        @apiGroup Orders

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611


        @apiSuccess (200) {id} id Order id
        @apiSuccess (200) {String} url Order URI
        @apiSuccess (200) {String} created_date Date order was created
        @apiSuccess (200) {String} payment_type Payment URI
        @apiSuccess (200) {String} customer Customer URI

        @apiSuccessExample {json} Success
            {
                "id": 1,
                "url": "http://localhost:8000/orders/1",
                "created_date": "2019-08-16",
                "payment_type": "http://localhost:8000/paymenttypes/1",
                "customer": "http://localhost:8000/customers/5"
            }
        """
        try:
            customer = Customer.objects.get(user=request.auth.user)
            order = Order.objects.get(pk=pk, customer=customer)
            serializer = OrderSerializer(order, context={'request': request})
            return Response(serializer.data)

        except Order.DoesNotExist as ex:
            return Response(
                {'message': 'The requested order does not exist, or you do not have permission to access it.'},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """
        Handle PUT request to assign payment type to an order
        """
        try:
            # Ensure this is a real user
            customer = Customer.objects.get(user=request.user)

            # Check that the order belongs to the user
            order = Order.objects.get(pk=pk, customer=customer)

            # Validate payment_type is provided
            payment_type_id = request.data.get("payment_type")
            if not payment_type_id:
                return Response(
                    {"message": "Missing payment_type"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Optional: validate that the payment type exists and belongs to the user
            try:
                payment = Payment.objects.get(pk=payment_type_id, customer=customer)
            except Payment.DoesNotExist:
                return Response(
                    {"message": "Invalid payment type"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Assign payment type to order and save
            order.payment_type = payment
            order.save()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Customer.DoesNotExist:
            return Response({"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({"message": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """
        @api {GET} /orders GET customer orders
        @apiName GetOrders
        @apiGroup Orders

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} payment_id Query param to filter by payment used

        @apiSuccess (200) {Object[]} orders Array of order objects
        @apiSuccess (200) {id} orders.id Order id
        @apiSuccess (200) {String} orders.url Order URI
        @apiSuccess (200) {String} orders.created_date Date order was created
        @apiSuccess (200) {String} orders.payment_type Payment URI
        @apiSuccess (200) {String} orders.customer Customer URI

        @apiSuccessExample {json} Success
            [
                {
                    "id": 1,
                    "url": "http://localhost:8000/orders/1",
                    "created_date": "2019-08-16",
                    "payment_type": "http://localhost:8000/paymenttypes/1",
                    "customer": "http://localhost:8000/customers/5"
                }
            ]
        """
        customer = Customer.objects.get(user=request.auth.user)
        orders = Order.objects.filter(customer=customer)
        print(f"Orders found for customer {customer.id}: {orders.count()}")

        payment = self.request.query_params.get('payment_id', None)
        if payment is not None:
            orders = orders.filter(payment__id=payment)

        json_orders = OrderSerializer(
            orders, many=True, context={'request': request})

        return Response(json_orders.data)

    
    def create(self, request):
        customer = Customer.objects.get(user=request.auth.user)
        product_id = request.data.get("product_id")

        if not product_id:
            return Response ({"message": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)
        order, created = Order.objects.get_or_create(customer=customer, payment_typ=None)

        product = Product.objects.get(pk=product_id)
        OrderProduct.objects.create(order=order, product=product)
        return Response({"message": f"Added {product.name} to your cart"}, status=status.HTTP_201_CREATED)
