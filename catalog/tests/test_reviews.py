from django.test import TestCase
from django.urls import reverse

from catalog.models import Review
from catalog.tests.helpers import create_review, create_title, create_user


class ReviewCreateTests(TestCase):
    def setUp(self):
        self.title = create_title()
        self.critic = create_user()
        self.url = reverse(
            "catalog:review-create",
            kwargs={"pk": self.title.pk},
        )
        self.data = {"score": 8, "text": "Great movie"}

    def test_anonymous_cannot_create_review(self):
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")
        self.assertFalse(Review.objects.exists())

    def test_user_creates_review_for_title(self):
        self.client.force_login(self.critic)
        response = self.client.post(self.url, data=self.data)

        review = Review.objects.get()
        self.assertEqual(review.critic, self.critic)
        self.assertEqual(review.title, self.title)
        self.assertRedirects(response, self.title.get_absolute_url())

    def test_second_review_on_same_title_is_not_created(self):
        create_review(self.critic, self.title)
        self.client.force_login(self.critic)
        response = self.client.post(self.url, data=self.data)

        self.assertRedirects(response, self.title.get_absolute_url())
        self.assertEqual(Review.objects.count(), 1)

    def test_invalid_score_is_rejected(self):
        self.client.force_login(self.critic)
        response = self.client.post(
            self.url,
            data={"score": 11, "text": "Text"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.exists())


class ReviewOwnershipTests(TestCase):
    def setUp(self):
        self.title = create_title()
        self.author = create_user(username="author")
        self.other = create_user(username="other")
        self.review = create_review(self.author, self.title, score=5)
        self.update_url = reverse(
            "catalog:review-update",
            kwargs={"pk": self.review.pk},
        )
        self.delete_url = reverse(
            "catalog:review-delete",
            kwargs={"pk": self.review.pk},
        )

    def test_author_can_update_review(self):
        self.client.force_login(self.author)
        self.client.post(
            self.update_url,
            data={"score": 9, "text": "Changed my mind"},
        )
        self.review.refresh_from_db()
        self.assertEqual(self.review.score, 9)

    def test_other_user_cannot_update_review(self):
        self.client.force_login(self.other)
        response = self.client.post(
            self.update_url,
            data={"score": 1, "text": "Hacked"},
        )
        self.assertEqual(response.status_code, 404)
        self.review.refresh_from_db()
        self.assertEqual(self.review.score, 5)

    def test_author_can_delete_review(self):
        self.client.force_login(self.author)
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, self.title.get_absolute_url())
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())

    def test_other_user_cannot_delete_review(self):
        self.client.force_login(self.other)
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Review.objects.filter(pk=self.review.pk).exists())


class RatingTests(TestCase):
    def setUp(self):
        self.title = create_title()
        self.first = create_user(username="first")
        create_review(self.first, self.title, score=6)
        create_review(create_user(username="second"), self.title, score=9)

    def test_title_detail_shows_average_score(self):
        response = self.client.get(self.title.get_absolute_url())
        title = response.context["title"]
        self.assertEqual(title.avg_score, 7.5)
        self.assertEqual(title.num_reviews, 2)

    def test_user_review_is_in_context_for_its_author(self):
        self.client.force_login(self.first)
        response = self.client.get(self.title.get_absolute_url())
        self.assertEqual(response.context["user_review"].score, 6)

    def test_user_review_is_empty_for_user_without_review(self):
        self.client.force_login(create_user(username="newcomer"))
        response = self.client.get(self.title.get_absolute_url())
        self.assertIsNone(response.context["user_review"])
