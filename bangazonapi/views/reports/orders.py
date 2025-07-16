from django.shortcuts import render
from bangazonapi.models import Order, Customer
from django.db.models import Sum

def orders_report(request):
    status = request.GET.get('status', '')

    if status == 'complete':
        paid_orders = Order.objects.filter(payment_type__isnull=False)

        orders_data = []

        for order in paid_orders:
            total = sum([li.product.price for li in order.lineitems.all()])
            orders_data.append({
                'id': order.id,
                'customer_name': f"{order.customer.user.first_name} {order.customer.user.last_name}",
                'total': total,
                'payment_type': order.payment_type.merchant_name
            })
        context = {
            'orders': orders_data
        }

        return render(request, 'reports/paid_orders.html', context)
    # return render(request, 'reports/paid_orders.html', {'orders': []})

    if status == 'incomplete':
        unpaid_orders = Order.objects.filter(payment_type__isnull=True)

        orders_data = []

        for order in unpaid_orders:
            total = sum([li.product.price for li in order.lineitems.all()])
            orders_data.append({
                'id': order.id,
                'customer_name': f"{order.customer.user.first_name} {order.customer.user.last_name}",
                'total': round(total, 2),
            })
        context = {
            'orders': orders_data
        }
        
        return render(request, 'reports/incomplete_orders.html', context)