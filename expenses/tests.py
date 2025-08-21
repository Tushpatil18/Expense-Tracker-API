from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import date, timedelta


class AuthAndExpenseTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.expenses_url = reverse("expense-list")  

        self.user_data = {
            "email": "testuser@example.com",
            "name": "Test User",
            "password": "testpass123",
        }
        self.login_data = {
            "email": "testuser@example.com",
            "password": "testpass123",
        }

    def _register(self):
        res = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def _login(self):
        res = self.client.post(self.login_url, self.login_data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_register_and_login(self):
        self._register()
        self._login()

    def test_expenses_filters_pagination_sort(self):
        self._register()
        self._login()

        base = date(2025, 8, 1)
        payloads = [
            {"amount": 100, "category": "FOOD", "description": "A", "date": str(base)},
            {"amount": 50,  "category": "FOOD", "description": "B", "date": str(base + timedelta(days=1))},
            {"amount": 500, "category": "RENT", "description": "C", "date": str(base)},
            {"amount": 75,  "category": "BILLS","description": "D", "date": str(base + timedelta(days=2))},
            {"amount": 25,  "category": "OTHER","description": "E", "date": str(base + timedelta(days=3))},
        ]
        for p in payloads:
            r = self.client.post(self.expenses_url, p, format="json")
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        # pagination
        r = self.client.get(self.expenses_url + "?page=1&page_size=2")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("results", r.data)
        self.assertEqual(len(r.data["results"]), 2)

        # filters: category + minAmount + ordering
        r = self.client.get(self.expenses_url + "?category=FOOD&minAmount=60&ordering=-amount")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(float(r.data["results"][0]["amount"]), 100.0)

        # date range
        start = str(base + timedelta(days=1))
        end = str(base + timedelta(days=2))
        r = self.client.get(self.expenses_url + f"?startDate={start}&endDate={end}")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(r.data["count"], 2)

        # ordering by amount desc (use results page)
        r = self.client.get(self.expenses_url + "?ordering=-amount")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        amounts = [float(x["amount"]) for x in r.data["results"]]
        self.assertEqual(amounts, sorted(amounts, reverse=True))

    def test_update_delete_and_monthly_summary(self):
        self._register()
        self._login()

        # create
        r = self.client.post(self.expenses_url, {
            "amount": 123.45, "category": "FOOD", "description": "Original", "date": "2025-08-01"
        }, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        exp_id = r.data["id"]

        # update (PUT)
        detail_url = reverse("expense-detail", args=[exp_id])
        r = self.client.put(detail_url, {
            "amount": 150.00, "category": "FOOD", "description": "Updated", "date": "2025-08-02"
        }, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(float(r.data["amount"]), 150.00)

        
        r = self.client.get(reverse("monthly-summary"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("2025-08", r.data)
        self.assertIn("FOOD", r.data["2025-08"])

        # delete
        r = self.client.delete(detail_url)
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
