"""
tests for tags api
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse("recipe:tag-list")


def detail_url(id):
    """create and return tag detail url"""
    return reverse("recipe:tag-detail", args=[id])


def create_user(email="user@example.com", password="testpass123"):
    """creates a returns a new user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTest(TestCase):
    """test unauthed api reqs"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """test auth is required"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """test authed api reqs"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()

        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """test gets tags"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """test list of tag is limited to list of authed user"""

        user2 = create_user(email="other@example.com", password="otherpass123")
        Tag.objects.create(user=user2, name="Fruity")
        tag = Tag.objects.create(user=self.user, name="Comfort Food")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """test updating a tag"""

        tag = Tag.objects.create(user=self.user, name="After dinner")
        payload = {
            "name": "Dessert",
        }

        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        """test deleting a tag"""

        tag = Tag.objects.create(user=self.user, name="breakfast")

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """test listing  ingredients by those assigned to recipes"""

        ing1 = Tag.objects.create(user=self.user, name="Apple")
        ing2 = Tag.objects.create(user=self.user, name="Turkey")

        recipe = Recipe.objects.create(
            title="Apply Crumble",
            time_minutes=5,
            price=Decimal("2.5"),
            user=self.user,
        )

        recipe.tags.add(ing1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        s1 = TagSerializer(ing1)
        s2 = TagSerializer(ing2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """test filtered tags are unique"""

        ing = Tag.objects.create(user=self.user, name="Eggs")
        Tag.objects.create(user=self.user, name="Lentils")

        recipe1 = Recipe.objects.create(
            title="Egg Crumble",
            time_minutes=5,
            price=Decimal("2.5"),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title="Crumble Egg",
            time_minutes=5,
            price=Decimal("2.5"),
            user=self.user,
        )

        recipe1.tags.add(ing)
        recipe2.tags.add(ing)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
