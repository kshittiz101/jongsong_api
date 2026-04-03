from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from apps.home.models import Feature, HeroImage, Services
from apps.pharmacy.models import Category


class HomeFeatureAPITests(APITestCase):
    def setUp(self):
        self.feature = Feature.objects.create(
            title="Fast Delivery",
            description="We deliver quickly.",
            icon_name="truck",
        )

    def test_feature_list(self):
        res = self.client.get("/api/v1/features/")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.data), 1)

    def test_feature_detail(self):
        res = self.client.get(f"/api/v1/features/{self.feature.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["id"], self.feature.id)
        self.assertEqual(res.data["title"], self.feature.title)

    def test_feature_post_not_allowed(self):
        res = self.client.post(
            "/api/v1/features/",
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
        res = self.client.get("/api/v1/services/")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.data), 1)

    def test_services_detail(self):
        res = self.client.get(f"/api/v1/services/{self.service.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["id"], self.service.id)
        self.assertEqual(res.data["title"], self.service.title)

    def test_services_post_not_allowed(self):
        res = self.client.post(
            "/api/v1/services/",
            data={"title": "x", "description": "y", "icon_name": "z"},
            format="json",
        )
        self.assertEqual(res.status_code, 405)


class HeroImageAPITests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Wellness",
            description="Wellness products and services.",
            is_active=True,
        )
        self.hero_image = HeroImage.objects.create(
            image=SimpleUploadedFile(
                "hero.jpg",
                b"not-a-real-image-but-ok-for-imagefield",
                content_type="image/jpeg",
            ),
            title="Balance",
            description="Modern wellness, naturally balanced.",
            category=self.category,
        )

    def test_hero_images_list(self):
        res = self.client.get("/api/v1/hero-images/")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.data), 1)

    def test_hero_images_detail(self):
        res = self.client.get(f"/api/v1/hero-images/{self.hero_image.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["id"], self.hero_image.id)
        self.assertEqual(res.data["title"], self.hero_image.title)
        self.assertEqual(res.data["category"], self.category.id)
        self.assertEqual(res.data["category_name"], self.category.name)

    def test_hero_images_post_not_allowed(self):
        res = self.client.post(
            "/api/v1/hero-images/",
            data={"title": "x", "description": "y"},
            format="json",
        )
        self.assertEqual(res.status_code, 405)
