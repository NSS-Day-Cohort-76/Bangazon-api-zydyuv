import datetime
import json
from rest_framework import status
from rest_framework.test import APITestCase


class PaymentTests(APITestCase):
    def setUp(self) -> None:
        """
        Create a new account and create sample category
        """
        url = "/register"
        data = {
            "username": "steve",
            "password": "Admin8*",
            "email": "steve@stevebrownlee.com",
            "address": "100 Infinity Way",
            "phone_number": "555-1212",
            "first_name": "Steve",
            "last_name": "Brownlee",
        }
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)
        self.token = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("🧪 TEST TOKEN:", self.token)

    def test_create_payment_type(self):
        """
        Ensure we can add a payment type for a customer.
        """
        # Add product to order
        url = "/payment-types"
        data = {
            "merchant_name": "American Express",
            "account_number": "111-1111-1111",
            "expiration_date": "2024-12-31",
            "create_date": datetime.date.today(),
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["merchant_name"], "American Express")
        self.assertEqual(json_response["account_number"], "111-1111-1111")
        self.assertEqual(json_response["expiration_date"], "2024-12-31")
        self.assertEqual(json_response["create_date"], str(datetime.date.today()))

    def test_delete_payment_type(self):
        """
        Ensure we can Delete a payment type for a customer
        """
        payment_data = {
            "merchant_name": "Visa",
            "account_number": "123456789",
            "expiration_date": "2026-12-31",
            "create_date": "2025-07-17",
        }

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)  # ✅ Add this
        create_response = self.client.post(
            "/payment-types", payment_data, content_type="application/json"
        )
        self.assertEqual(create_response.status_code, 201)
        payment_id = create_response.json()["id"]

        delete_response = self.client.delete(f"/payment-types/{payment_id}")
        self.assertEqual(delete_response.status_code, 204)

        get_response = self.client.get(f"/payment-types/{payment_id}")
        self.assertEqual(get_response.status_code, 404)
