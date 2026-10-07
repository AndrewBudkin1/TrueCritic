from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from catalog.models import Genre, Title, Review


class CriticCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
            "bio",
        )


class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search..."}
        ),
    )


class TitleFilterForm(SearchForm):
    SORT_CHOICES = (
        ("name", "Name"),
        ("rating", "Top rated"),
        ("newest", "Newest"),
    )

    media_type = forms.ChoiceField(
        choices=[("", "All types")] + Title.MediaType.choices,
        required=False,
        label="",
        widget=forms.Select(attrs={"class": "form-control ml-2"}),
    )
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        label="",
        widget=forms.Select(attrs={"class": "form-control ml-2"}),
    )


class TitleForm(forms.ModelForm):
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Title
        fields = (
            "name",
            "media_type",
            "release_year",
            "studio",
            "genres",
            "description",
        )

    def clean_release_year(self):
        year = self.cleaned_data["release_year"]
        current_year = timezone.now().year
        if year < 1888 or year > current_year:
            raise ValidationError(
                f"Release year must be between 1888 and {current_year}."
            )
        return year


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("score", "text")
        widgets = {
            "score": forms.NumberInput(attrs={"min": 1, "max": 10}),
            "text": forms.Textarea(attrs={"rows": 4}),
        }
