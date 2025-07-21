from django.shortcuts import render
from bangazonapi.models import Favorite, Customer


def favorite_sellers_report(request):
    customer_id = request.GET.get("customer")

    try:
        customer = Customer.objects.get(pk=customer_id)
        favorites = Favorite.objects.filter(customer=customer)
        sellers = [fav.seller for fav in favorites]

        context = {"customer": customer, "favorite_sellers": sellers}

        return render(request, "reports/favorite_sellers.html", context)
    except Customer.DoesNotExist:
        return render(
            request,
            "reports/favorite_sellers.html",
            {"customer": None, "favorite_sellers": []},
        )
