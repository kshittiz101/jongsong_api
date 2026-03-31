from django.urls import reverse
from rest_framework.test import APITestCase

from home.models import Feature, Services


class HomeFeatureAPITests(APITestCase):
    def setUp(self):
        self.feature = Feature.objects.create(
            title="Fast Delivery",
            description="We deliver quickly.",
            icon_name="truck",
        )

    def test_feature_list(self):
        res = self.client.get("/api/features/")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.data), 1)

    def test_feature_detail(self):
        res = self.client.get(f"/api/features/{self.feature.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["id"], self.feature.id)
        self.assertEqual(res.data["title"], self.feature.title)

    def test_feature_post_not_allowed(self):
        res = self.client.post(
            "/api/features/",
            data={"title": "x", "description": "y", "icon_name": "z"},
            format="json",
        )
        self.assertEqual(res.status_code, 405)


class HomeServicesAPITests(APITestCase):
    def setUp(self):
        self.service = Services.objects.create(
            rank=1,
            title="Online Consultation",
            description="Talk to a professional.",
            icon_name="chat",
            color="primary",
        )

    def test_services_list(self):
        res = self.client.get("/api/services/")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.data), 1)

    def test_services_detail(self):
        res = self.client.get(f"/api/services/{self.service.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["id"], self.service.id)
        self.assertEqual(res.data["title"], self.service.title)

    def test_services_post_not_allowed(self):
        res = self.client.post(
            "/api/services/",
            data={"title": "x", "description": "y", "icon_name": "z"},
            format="json",
        )
        self.assertEqual(res.status_code, 405)
