from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from catalog.models import Genre, Review, Studio, Title
from catalog.tests.helpers import create_review, create_title, create_user


class ModelStrTests(TestCase):
    def test_critic_str(self):
        critic = create_user(
            username="john",
            first_name="John",
            last_name="Smith",
        )
        self.assertEqual(str(critic), "john John Smith")

    def test_genre_str(self):
        genre = Genre.objects.create(name="RPG")
        self.assertEqual(str(genre), "RPG")

    def test_studio_str(self):
        studio = Studio.objects.create(name="Warner Bros.", country="USA")
        self.assertEqual(str(studio), "Warner Bros. | USA")

    def test_title_str_uses_media_type_label(self):
        movie = create_title(name="Dune")
        game = create_title(
            name="The Witcher 3",
            media_type=Title.MediaType.GAME,
        )
        self.assertEqual(str(movie), "Dune (Movie)")
        self.assertEqual(str(game), "The Witcher 3 (Video game)")

    def test_review_str(self):
        review = create_review(
            create_user(username="john"),
            create_title(name="Dune"),
            score=8,
        )
        self.assertEqual(str(review), "john - Dune: 8")


class ModelUrlTests(TestCase):
    def test_title_url(self):
        title = create_title()
        self.assertEqual(
            title.get_absolute_url(),
            reverse("catalog:title-detail", kwargs={"pk": title.pk}),
        )

    def test_studio_url(self):
        studio = Studio.objects.create(name="Studio", country="USA")
        self.assertEqual(
            studio.get_absolute_url(),
            reverse("catalog:studio-detail", kwargs={"pk": studio.pk}),
        )

    def test_genre_url(self):
        genre = Genre.objects.create(name="Drama")
        self.assertEqual(
            genre.get_absolute_url(),
            reverse("catalog:genre-detail", kwargs={"pk": genre.pk}),
        )

    def test_review_url_leads_to_title_page(self):
        title = create_title()
        review = create_review(create_user(), title)
        self.assertEqual(review.get_absolute_url(), title.get_absolute_url())


class ReviewConstraintTests(TestCase):
    def setUp(self):
        self.critic = create_user()
        self.title = create_title()

    def test_one_review_per_critic_and_title(self):
        create_review(self.critic, self.title)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_review(self.critic, self.title)

    def test_score_must_be_between_1_and_10(self):
        for score in (0, 11):
            with self.subTest(score=score):
                review = Review(
                    critic=self.critic,
                    title=self.title,
                    score=score,
                    text="Text",
                )
                with self.assertRaises(ValidationError):
                    review.full_clean()
