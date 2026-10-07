from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import Genre, Studio
from catalog.tests.helpers import PASSWORD, create_title, create_user


class PublicPagesTests(TestCase):
    def test_public_pages_available_without_login(self):
        title = create_title()
        genre = Genre.objects.create(name="Drama")
        critic = create_user()
        urls = [
            reverse("catalog:index"),
            reverse("catalog:title-list"),
            reverse("catalog:title-detail", kwargs={"pk": title.pk}),
            reverse("catalog:studio-list"),
            reverse(
                "catalog:studio-detail",
                kwargs={"pk": title.studio.pk},
            ),
            reverse("catalog:genre-list"),
            reverse("catalog:genre-detail", kwargs={"pk": genre.pk}),
            reverse("catalog:critic-list"),
            reverse("catalog:critic-detail", kwargs={"pk": critic.pk}),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)


class StaffPagesTests(TestCase):
    def setUp(self):
        title = create_title()
        studio_pk = {"pk": title.studio.pk}
        genre_pk = {"pk": Genre.objects.create(name="Drama").pk}
        self.urls = [
            reverse("catalog:title-create"),
            reverse("catalog:title-update", kwargs={"pk": title.pk}),
            reverse("catalog:title-delete", kwargs={"pk": title.pk}),
            reverse("catalog:studio-create"),
            reverse("catalog:studio-update", kwargs=studio_pk),
            reverse("catalog:studio-delete", kwargs=studio_pk),
            reverse("catalog:genre-create"),
            reverse("catalog:genre-update", kwargs=genre_pk),
            reverse("catalog:genre-delete", kwargs=genre_pk),
        ]

    def test_anonymous_is_redirected_to_login(self):
        for url in self.urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f"{reverse('login')}?next={url}",
                )

    def test_regular_user_gets_forbidden(self):
        self.client.force_login(create_user())
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_staff_has_access(self):
        self.client.force_login(create_user(is_staff=True))
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)


class StudioDeleteTests(TestCase):
    def setUp(self):
        self.client.force_login(create_user(is_staff=True))

    def test_studio_with_titles_is_not_deleted(self):
        studio = create_title().studio
        response = self.client.post(
            reverse("catalog:studio-delete", kwargs={"pk": studio.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.context)
        self.assertTrue(Studio.objects.filter(pk=studio.pk).exists())

    def test_studio_without_titles_is_deleted(self):
        studio = Studio.objects.create(name="Empty", country="USA")
        response = self.client.post(
            reverse("catalog:studio-delete", kwargs={"pk": studio.pk})
        )
        self.assertRedirects(response, reverse("catalog:studio-list"))
        self.assertFalse(Studio.objects.filter(pk=studio.pk).exists())


class SignUpTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("catalog:signup"),
            data={
                "username": "newcritic",
                "password1": PASSWORD,
                "password2": PASSWORD,
                "bio": "I love movies",
            },
            follow=True,
        )
        self.assertTrue(
            get_user_model().objects.filter(username="newcritic").exists()
        )
        self.assertTrue(response.context["user"].is_authenticated)

    def test_logged_in_user_is_redirected_from_signup(self):
        self.client.force_login(create_user())
        response = self.client.get(reverse("catalog:signup"))
        self.assertRedirects(response, reverse("catalog:index"))
