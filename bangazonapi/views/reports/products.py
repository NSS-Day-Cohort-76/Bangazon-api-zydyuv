from django.shortcuts import render
from bangazonapi.models import Product

def inexpensive_products_report(request):

    products = Product.objects.filter(price__lte=999)

    context = {
        'products': products
    }

    return render(request, 'reports/inexpensive_products.html', context)

def expensive_products_report(request):

    products = Product.objects.filter(price__gte=1000)

    context = {
        'products': products
    }

    return render(request, 'reports/expensive_products.html', context)