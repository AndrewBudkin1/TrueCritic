from django.test import TestCase
from django.utils import timezone

from catalog.forms import CriticCreationForm, TitleFilterForm, TitleForm
from catalog.models import Genre, Studio
from catalog.tests.helpers import PASSWORD


class TitleFormTests(TestCase):
    def setUp(self):
        self.studio = Studio.objects.create(name="Studio", country="USA")
        self.genre = Genre.objects.create(name="Drama")

    def get_form(self, release_year, genres=None):
        if genres is None:
            genres = [self.genre.id]
        return TitleForm(
            data={
                "name": "Dune",
                "media_type": "movie",
                "release_year": release_year,
                "studio": self.studio.id,
                "genres": genres,
                "description": "",
            }
        )

    def test_current_year_is_valid(self):
        self.assertTrue(self.get_form(timezone.now().year).is_valid())

    def test_year_out_of_range_is_invalid(self):
        for year in (1887, timezone.now().year + 1):
            with self.subTest(year=year):
                form = self.get_form(year)
                self.assertFalse(form.is_valid())
                self.assertIn("release_year", form.errors)

    def test_genres_are_required(self):
        form = self.get_form(2020, genres=[])
        self.assertFalse(form.is_valid())
        self.assertIn("genres", form.errors)


class CriticCreationFormTests(TestCase):
    def test_bio_and_names_are_optional(self):
        form = CriticCreationForm(
            data={
                "username": "newcritic",
                "password1": PASSWORD,
                "password2": PASSWORD,
            }
        )
        self.assertTrue(form.is_valid())


class TitleFilterFormTests(TestCase):
    def test_empty_form_is_valid(self):
        self.assertTrue(TitleFilterForm(data={}).is_valid())

    def test_unknown_sort_is_invalid(self):
        form = TitleFilterForm(data={"sort": "password"})
        self.assertFalse(form.is_valid())
