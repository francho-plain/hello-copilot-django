"""
Tests for the cats app.

This module contains comprehensive tests for the Cat model, serializers, and views.
"""

import json
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import NoReverseMatch
from django.urls import reverse as _django_reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cat
from .serializers import (AdoptCatSerializer, BreedStatisticsSerializer,
                          CatListSerializer, CatSerializer,
                          CatStatisticsSerializer)


def reverse(name, *args, **kwargs):
    """Try multiple reverse name variants to be tolerant to router basename/namespace.

    This lets tests work whether the router registered names like 'cat-list',
    'cats-list' or namespaced forms 'cats:cat-list'.
    """
    candidates = [
        name,
        name.replace("cat-", "cats-"),
        f"cats:{name}",
        f"cats:{name.replace('cat-', 'cats-')}",
    ]
    for candidate in candidates:
        try:
            return _django_reverse(candidate, *args, **kwargs)
        except NoReverseMatch:
            continue
    # fallback: raise the original exception for the primary name
    return _django_reverse(name, *args, **kwargs)


def _parse_response_data(response):
    """Normalize response payloads into a list of objects.

    Works with DRF paginated responses ({'results': [...]}) and with
    direct lists or single-object dicts.
    """
    try:
        data = response.data
    except Exception:
        # fallback to raw content JSON
        try:
            data = json.loads(response.content.decode())
        except Exception:
            return []

    if isinstance(data, dict):
        if "results" in data and isinstance(data["results"], (list, tuple)):
            return data["results"]
        # some endpoints use 'data' or 'items'
        for key in ("data", "items"):
            if key in data and isinstance(data[key], (list, tuple)):
                return data[key]
        # single-object dict -> wrap
        return [data]
    if isinstance(data, (list, tuple)):
        return data
    return []


def _get_single_object(response):
    """Return a single object (dict) from response.

    If the response contains a list, returns the first element.
    """
    try:
        data = response.data
    except Exception:
        try:
            data = json.loads(response.content.decode())
        except Exception:
            data = None

    if isinstance(data, dict):
        return data
    if isinstance(data, (list, tuple)) and data:
        return data[0]
    raise AssertionError("Response did not contain a JSON object")


class CatModelTest(TestCase):
    """Test cases for the Cat model."""

    def setUp(self):
        """Set up test data."""
        self.cat = Cat.objects.create(
            name="Whiskers",
            breed="Persian",
            age=3,
            color="White",
            weight=Decimal("4.5"),
            is_neutered=True,
            description="A friendly and calm cat",
        )

    def test_cat_creation(self):
        """Test basic cat creation."""
        self.assertEqual(self.cat.name, "Whiskers")
        self.assertEqual(self.cat.breed, "Persian")
        self.assertEqual(self.cat.age, 3)
        self.assertEqual(self.cat.color, "White")
        self.assertEqual(self.cat.weight, Decimal("4.5"))
        self.assertTrue(self.cat.is_neutered)
        self.assertFalse(self.cat.is_adopted)

    def test_cat_string_representation(self):
        """Test the string representation of a cat."""
        self.assertEqual(str(self.cat), "Whiskers (Persian)")

        # Test with no breed
        cat_no_breed = Cat.objects.create(name="Mittens")
        self.assertEqual(str(cat_no_breed), "Mittens (Mixed breed)")

    def test_cat_properties(self):
        """Test computed properties."""
        # Test age display
        self.assertEqual(self.cat.age_display, "3 years old")

        # Test weight display
        self.assertEqual(self.cat.weight_display, "4.5 kg")

        # Test status display for available cat
        self.assertEqual(self.cat.status_display, "Available for adoption")

        # Test is_adopted property
        self.assertFalse(self.cat.is_adopted)

    def test_adopted_cat_properties(self):
        """Test properties for adopted cats."""
        self.cat.adopt("John Doe", date.today())
        self.cat.refresh_from_db()

        self.assertTrue(self.cat.is_adopted)
        self.assertEqual(self.cat.status_display, "Adopted by John Doe")

    def test_cat_manager_methods(self):
        """Test custom manager methods."""
        # Create more cats
        Cat.objects.create(name="Fluffy", breed="Siamese", age=2)
        Cat.objects.create(
            name="Shadow",
            breed="Persian",
            age=1,
            owner_name="Jane",
            adoption_date=date.today(),
        )

        # Test available cats
        available = Cat.available_cats()
        self.assertEqual(available.count(), 2)

        # Test adopted cats
        adopted = Cat.adopted_cats()
        self.assertEqual(adopted.count(), 1)

        # Test breed filtering
        persians = Cat.by_breed("Persian")
        self.assertEqual(persians.count(), 2)

        # Test neutered cats
        neutered = Cat.neutered_cats()
        self.assertEqual(neutered.count(), 1)

    def test_adopt_method(self):
        """Test the adopt method."""
        adoption_date = date(2024, 1, 15)
        self.cat.adopt("Alice Smith", adoption_date)

        self.cat.refresh_from_db()
        self.assertEqual(self.cat.owner_name, "Alice Smith")
        self.assertEqual(self.cat.adoption_date, adoption_date)
        self.assertTrue(self.cat.is_adopted)

    def test_return_to_shelter_method(self):
        """Test the return_to_shelter method."""
        # First adopt the cat
        self.cat.adopt("Bob Johnson")
        self.assertTrue(self.cat.is_adopted)

        # Then return to shelter
        self.cat.return_to_shelter()
        self.cat.refresh_from_db()

        self.assertIsNone(self.cat.owner_name)
        self.assertIsNone(self.cat.adoption_date)
        self.assertFalse(self.cat.is_adopted)

    def test_clean_method_validation(self):
        """Test model validation in clean method."""
        # Test negative age
        cat = Cat(name="Test", age=-1)
        with self.assertRaises(ValueError):
            cat.clean()

        # Test negative weight
        cat = Cat(name="Test", weight=Decimal("-1.0"))
        with self.assertRaises(ValueError):
            cat.clean()

        # Test adoption inconsistency
        cat = Cat(name="Test", adoption_date=date.today())
        with self.assertRaises(ValueError):
            cat.clean()

        cat = Cat(name="Test", owner_name="Owner")
        with self.assertRaises(ValueError):
            cat.clean()


class CatSerializerTest(TestCase):
    """Test cases for Cat serializers."""

    def setUp(self):
        """Set up test data."""
        self.cat_data = {
            "name": "Luna",
            "breed": "Maine Coon",
            "age": 4,
            "color": "Gray",
            "weight": Decimal("6.2"),
            "is_neutered": False,
            "description": "A large and friendly Maine Coon cat",
        }
        self.cat = Cat.objects.create(**self.cat_data)

    def test_cat_serializer(self):
        """Test CatSerializer serialization."""
        serializer = CatSerializer(self.cat)
        data = serializer.data

        self.assertEqual(data["name"], "Luna")
        self.assertEqual(data["breed"], "Maine Coon")
        self.assertEqual(data["age"], 4)
        self.assertEqual(data["color"], "Gray")
        self.assertEqual(data["weight"], "6.20")  # Decimal serialized as string
        self.assertFalse(data["is_neutered"])
        self.assertEqual(data["is_adopted"], False)
        self.assertEqual(data["age_display"], "4 years old")
        self.assertEqual(data["weight_display"], "6.2 kg")
        self.assertEqual(data["status_display"], "Available for adoption")

    def test_cat_serializer_validation(self):
        """Test CatSerializer validation."""
        # Test empty name
        invalid_data = self.cat_data.copy()
        invalid_data["name"] = ""
        serializer = CatSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

        # Test short name
        invalid_data["name"] = "A"
        serializer = CatSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

        # Test negative age
        invalid_data = self.cat_data.copy()
        invalid_data["name"] = "Valid Name"
        invalid_data["age"] = -1
        serializer = CatSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("age", serializer.errors)

        # Test negative weight
        invalid_data["age"] = 2
        invalid_data["weight"] = Decimal("-1.0")
        serializer = CatSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("weight", serializer.errors)

    def test_cat_list_serializer(self):
        """Test CatListSerializer."""
        serializer = CatListSerializer(self.cat)
        data = serializer.data

        # Should have fewer fields than full serializer
        expected_fields = {
            "id",
            "name",
            "breed",
            "age",
            "color",
            "is_adopted",
            "status_display",
            "created_at",
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_adopt_cat_serializer(self):
        """Test AdoptCatSerializer."""
        valid_data = {"owner_name": "John Doe", "adoption_date": "2024-01-15"}
        serializer = AdoptCatSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

        # Test without adoption_date (should be valid)
        valid_data_no_date = {"owner_name": "Jane Smith"}
        serializer = AdoptCatSerializer(data=valid_data_no_date)
        self.assertTrue(serializer.is_valid())

        # Test empty owner name
        invalid_data = {"owner_name": ""}
        serializer = AdoptCatSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class CatAPITest(APITestCase):
    """Test cases for Cat API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.cat1 = Cat.objects.create(
            name="Whiskers",
            breed="Persian",
            age=3,
            color="White",
            weight=Decimal("4.5"),
            is_neutered=True,
            description="A friendly Persian cat",
        )
        self.cat2 = Cat.objects.create(
            name="Mittens",
            breed="Siamese",
            age=2,
            color="Brown",
            weight=Decimal("3.8"),
            is_neutered=False,
            description="An energetic Siamese cat",
        )
        self.cat3 = Cat.objects.create(
            name="Shadow",
            breed="Persian",
            age=1,
            color="Black",
            weight=Decimal("4.0"),
            is_neutered=True,
            owner_name="Alice",
            adoption_date=date.today(),
            description="A shy black cat",
        )

    def test_list_cats(self):
        """Test GET /api/cats/"""
        url = reverse("cat-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = _parse_response_data(response)
        self.assertEqual(len(data), 3)

        # Check that we get CatListSerializer format
        cat_data = data[0]
        self.assertIn("id", cat_data)
        self.assertIn("name", cat_data)
        self.assertIn("is_adopted", cat_data)
        self.assertIn("status_display", cat_data)

    def test_create_cat(self):
        """Test POST /api/cats/"""
        url = reverse("cat-list")
        data = {
            "name": "Luna",
            "breed": "Maine Coon",
            "age": 4,
            "color": "Gray",
            "weight": "6.2",
            "is_neutered": False,
            "description": "A large and friendly Maine Coon cat",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check response structure
        self.assertIn("status", response.data)
        self.assertIn("message", response.data)
        self.assertIn("cat", response.data)
        self.assertEqual(response.data["status"], "success")

        # Verify cat was created
        luna = Cat.objects.get(name="Luna")
        self.assertEqual(luna.breed, "Maine Coon")
        self.assertEqual(luna.age, 4)

    def test_create_cat_invalid_data(self):
        """Test POST /api/cats/ with invalid data"""
        url = reverse("cat-list")
        data = {
            "name": "",  # Invalid empty name
            "breed": "Maine Coon",
            "age": 4,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
        self.assertEqual(response.data["status"], "error")
        self.assertIn("errors", response.data)

    def test_retrieve_cat(self):
        """Test GET /api/cats/{id}/"""
        url = reverse("cat-detail", kwargs={"pk": self.cat1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Whiskers")
        self.assertEqual(response.data["breed"], "Persian")

    def test_update_cat(self):
        """Test PUT /api/cats/{id}/"""
        url = reverse("cat-detail", kwargs={"pk": self.cat1.pk})
        data = {
            "name": "Whiskers Updated",
            "breed": "Persian",
            "age": 4,
            "color": "White",
            "weight": "4.5",
            "is_neutered": True,
            "description": "An updated description",
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify update
        self.cat1.refresh_from_db()
        self.assertEqual(self.cat1.name, "Whiskers Updated")
        self.assertEqual(self.cat1.age, 4)

    def test_delete_cat(self):
        """Test DELETE /api/cats/{id}/"""
        url = reverse("cat-detail", kwargs={"pk": self.cat1.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify deletion
        with self.assertRaises(Cat.DoesNotExist):
            Cat.objects.get(pk=self.cat1.pk)

    def test_adopt_cat(self):
        """Test POST /api/cats/{id}/adopt/"""
        url = reverse("cat-adopt", kwargs={"pk": self.cat1.pk})
        data = {"owner_name": "John Doe", "adoption_date": "2024-01-15"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify adoption
        self.cat1.refresh_from_db()
        self.assertEqual(self.cat1.owner_name, "John Doe")
        self.assertEqual(self.cat1.adoption_date, date(2024, 1, 15))
        self.assertTrue(self.cat1.is_adopted)

    def test_adopt_already_adopted_cat(self):
        """Test adopting a cat that's already adopted."""
        url = reverse(
            "cat-adopt", kwargs={"pk": self.cat3.pk}
        )  # cat3 is already adopted
        data = {"owner_name": "New Owner"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_return_to_shelter(self):
        """Test POST /api/cats/{id}/return_to_shelter/"""
        url = reverse("cat-return-to-shelter", kwargs={"pk": self.cat3.pk})

        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify return
        self.cat3.refresh_from_db()
        self.assertIsNone(self.cat3.owner_name)
        self.assertIsNone(self.cat3.adoption_date)
        self.assertFalse(self.cat3.is_adopted)

    def test_return_available_cat_to_shelter(self):
        """Test returning a cat that's not adopted."""
        url = reverse("cat-return-to-shelter", kwargs={"pk": self.cat1.pk})

        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_available_cats(self):
        """Test GET /api/cats/available/"""
        url = reverse("cat-available")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return cat1 and cat2 (not cat3 which is adopted)
        data = _parse_response_data(response)
        self.assertEqual(len(data), 2)

        cat_names = [cat["name"] for cat in data]
        self.assertIn("Whiskers", cat_names)
        self.assertIn("Mittens", cat_names)
        self.assertNotIn("Shadow", cat_names)

    def test_adopted_cats(self):
        """Test GET /api/cats/adopted/"""
        url = reverse("cat-adopted")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return only cat3
        data = _parse_response_data(response)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Shadow")

    def test_statistics(self):
        """Test GET /api/cats/statistics/"""
        url = reverse("cat-statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        stats = response.data
        self.assertEqual(stats["total_cats"], 3)
        self.assertEqual(stats["adopted_cats"], 1)
        self.assertEqual(stats["available_cats"], 2)
        self.assertEqual(stats["adoption_rate"], 33.33)
        self.assertEqual(stats["neutered_cats"], 2)
        self.assertEqual(stats["breeds_count"], 2)  # Persian and Siamese

    def test_breeds_statistics(self):
        """Test GET /api/cats/breeds/"""
        url = reverse("cat-breeds")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should have statistics for Persian and Siamese
        breeds = _parse_response_data(response)
        self.assertEqual(len(breeds), 2)

        # Find Persian stats
        persian_stats = next(b for b in breeds if b["breed"] == "Persian")
        self.assertEqual(persian_stats["count"], 2)  # Whiskers and Shadow
        self.assertEqual(persian_stats["adoption_rate"], 50.0)  # Shadow is adopted

    def test_search_cats(self):
        """Test GET /api/cats/search/"""
        url = reverse("cat-search")
        # Search by name
        response = self.client.get(url, {"name": "Whiskers"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = _parse_response_data(response)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Whiskers")

        # Search by breed
        response = self.client.get(url, {"breed": "Persian"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = _parse_response_data(response)
        self.assertEqual(len(results), 2)

        # Search available only
        response = self.client.get(url, {"available": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = _parse_response_data(response)
        self.assertEqual(len(results), 2)

    def test_filtering(self):
        """Test query parameter filtering."""
        url = reverse("cat-list")
        # Filter by status
        response = self.client.get(url, {"status": "available"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = _parse_response_data(response)
        self.assertEqual(len(data), 2)

        response = self.client.get(url, {"status": "adopted"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = _parse_response_data(response)
        self.assertEqual(len(data), 1)

        # Filter by breed
        response = self.client.get(url, {"breed": "persian"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = _parse_response_data(response)
        self.assertEqual(len(data), 2)

        # Filter by neutered status
        response = self.client.get(url, {"neutered": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = _parse_response_data(response)
        self.assertEqual(len(data), 2)

        # Filter by age range
        response = self.client.get(url, {"min_age": "2", "max_age": "3"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = _parse_response_data(response)
        self.assertEqual(len(data), 2)  # Whiskers (3) and Mittens (2)

    def test_search_filtering(self):
        """Test search endpoint filtering."""
        url = reverse("cat-list")

        # Test search functionality
        response = self.client.get(url, {"search": "Whiskers"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = _parse_response_data(response)
        self.assertEqual(len(data), 1)

        response = self.client.get(url, {"search": "Persian"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = _parse_response_data(response)
        self.assertEqual(len(data), 2)

    def test_ordering(self):
        """Test ordering functionality."""
        url = reverse("cat-list")

        # Order by name
        response = self.client.get(url, {"ordering": "name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = _parse_response_data(response)
        names = [cat["name"] for cat in data]
        self.assertEqual(names, ["Mittens", "Shadow", "Whiskers"])

        # Order by age
        response = self.client.get(url, {"ordering": "age"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = _parse_response_data(response)
        ages = [cat["age"] for cat in data]
        self.assertEqual(ages, [1, 2, 3])
