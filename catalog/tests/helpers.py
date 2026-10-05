from django.contrib.auth import get_user_model

from catalog.models import Review, Studio, Title

PASSWORD = "Str0ngPass123!"


def create_user(username="critic", **extra_fields):
    return get_user_model().objects.create_user(
        username=username,
        password=PASSWORD,
        **extra_fields,
    )


def create_title(
    name="Dune",
    media_type=Title.MediaType.MOVIE,
    release_year=2021,
    studio=None,
):
    if studio is None:
        studio = Studio.objects.create(
            name=f"{name} Studio",
            country="USA",
        )
    return Title.objects.create(
        name=name,
        media_type=media_type,
        release_year=release_year,
        studio=studio,
    )


def create_review(critic, title, score=8, text="Great!"):
    return Review.objects.create(
        critic=critic,
        title=title,
        score=score,
        text=text,
    )
