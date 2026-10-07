from django.test import TestCase
from django.urls import reverse

from catalog.tests.helpers import create_title, create_user


class FavoriteToggleTests(TestCase):
    def setUp(self):
        self.title = create_title()
        self.critic = create_user()
        self.url = reverse(
            "catalog:title-favorite",
            kwargs={"pk": self.title.pk},
        )

    def test_user_adds_title_to_favorites(self):
        self.client.force_login(self.critic)
        response = self.client.post(self.url)

        self.assertIn(self.critic, self.title.favorited_by.all())
        self.assertRedirects(response, self.title.get_absolute_url())

    def test_user_removes_title_from_favorites(self):
        self.title.favorited_by.add(self.critic)
        self.client.force_login(self.critic)
        self.client.post(self.url)

        self.assertNotIn(self.critic, self.title.favorited_by.all())

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.post(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")
        self.assertFalse(self.title.favorited_by.exists())

    def test_get_request_is_not_allowed(self):
        self.client.force_login(self.critic)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)
        self.assertFalse(self.title.favorited_by.exists())

    def test_favorite_state_in_title_context(self):
        self.title.favorited_by.add(self.critic)
        self.client.force_login(self.critic)
        response = self.client.get(self.title.get_absolute_url())

        self.assertTrue(response.context["is_favorite"])
