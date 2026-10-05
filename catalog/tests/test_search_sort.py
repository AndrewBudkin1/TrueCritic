from django.test import TestCase
from django.urls import reverse

from catalog.models import Title
from catalog.tests.helpers import create_review, create_title, create_user


class TitleListFilterTests(TestCase):
    def setUp(self):
        self.url = reverse("catalog:title-list")
        self.dune = create_title(name="Dune", release_year=2021)
        self.witcher = create_title(
            name="The Witcher 3",
            media_type=Title.MediaType.GAME,
            release_year=2015,
        )
        self.alien = create_title(name="Alien", release_year=1979)
        critic = create_user()
        create_review(critic, self.dune, score=7)
        create_review(critic, self.witcher, score=10)

    def get_titles(self, **params):
        response = self.client.get(self.url, params)
        return list(response.context["title_list"])

    def test_default_sort_is_by_name(self):
        self.assertEqual(
            self.get_titles(),
            [self.alien, self.dune, self.witcher],
        )

    def test_search_by_name_is_case_insensitive(self):
        self.assertEqual(self.get_titles(q="WITCHER"), [self.witcher])

    def test_filter_by_media_type(self):
        self.assertEqual(self.get_titles(media_type="game"), [self.witcher])

    def test_sort_by_rating_puts_unrated_last(self):
        self.assertEqual(
            self.get_titles(sort="rating"),
            [self.witcher, self.dune, self.alien],
        )

    def test_sort_by_newest(self):
        self.assertEqual(
            self.get_titles(sort="newest"),
            [self.dune, self.witcher, self.alien],
        )

    def test_unknown_sort_is_ignored(self):
        response = self.client.get(self.url, {"sort": "password"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["title_list"]), 3)

    def test_filters_are_kept_in_pagination_links(self):
        for number in range(7):
            create_title(
                name=f"Game {number}",
                media_type=Title.MediaType.GAME,
            )
        response = self.client.get(
            self.url,
            {"media_type": "game", "sort": "newest"},
        )
        self.assertContains(
            response,
            "media_type=game&amp;sort=newest&amp;page=2",
        )


class CriticSearchTests(TestCase):
    def test_search_by_username(self):
        john = create_user(username="john")
        create_user(username="kate")
        response = self.client.get(
            reverse("catalog:critic-list"),
            {"q": "jo"},
        )
        self.assertEqual(list(response.context["critic_list"]), [john])


class TopRatedTests(TestCase):
    def test_index_shows_only_rated_titles_by_score(self):
        dune = create_title(name="Dune")
        witcher = create_title(name="The Witcher 3")
        create_title(name="Alien")
        critic = create_user()
        create_review(critic, dune, score=7)
        create_review(critic, witcher, score=10)

        response = self.client.get(reverse("catalog:index"))
        self.assertEqual(list(response.context["top_titles"]), [witcher, dune])
