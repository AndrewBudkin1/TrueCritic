from django.urls import path

from catalog.views import (
    CriticDetailView,
    CriticListView,
    GenreCreateView,
    GenreDeleteView,
    GenreDetailView,
    GenreListView,
    GenreUpdateView,
    ReviewCreateView,
    ReviewDeleteView,
    ReviewUpdateView,
    SignUpView,
    StudioCreateView,
    StudioDeleteView,
    StudioDetailView,
    StudioListView,
    StudioUpdateView,
    TitleCreateView,
    TitleDeleteView,
    TitleDetailView,
    TitleListView,
    TitleUpdateView,
    toggle_favorite,
    index,
)

app_name = "catalog"

urlpatterns = [
    path("", index, name="index"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("titles/", TitleListView.as_view(), name="title-list"),
    path(
        "titles/create/",
        TitleCreateView.as_view(),
        name="title-create",
    ),
    path(
        "titles/<int:pk>/",
        TitleDetailView.as_view(),
        name="title-detail",
    ),
    path(
        "titles/<int:pk>/update/",
        TitleUpdateView.as_view(),
        name="title-update",
    ),
    path(
        "titles/<int:pk>/delete/",
        TitleDeleteView.as_view(),
        name="title-delete",
    ),
    path(
        "titles/<int:pk>/favorite/",
        toggle_favorite,
        name="title-favorite",
    ),
    path(
        "titles/<int:pk>/reviews/create/",
        ReviewCreateView.as_view(),
        name="review-create",
    ),
    path(
        "reviews/<int:pk>/update/",
        ReviewUpdateView.as_view(),
        name="review-update",
    ),
    path(
        "reviews/<int:pk>/delete/",
        ReviewDeleteView.as_view(),
        name="review-delete",
    ),
    path("studios/", StudioListView.as_view(), name="studio-list"),
    path(
        "studios/create/",
        StudioCreateView.as_view(),
        name="studio-create",
    ),
    path(
        "studios/<int:pk>/",
        StudioDetailView.as_view(),
        name="studio-detail",
    ),
    path(
        "studios/<int:pk>/update/",
        StudioUpdateView.as_view(),
        name="studio-update",
    ),
    path(
        "studios/<int:pk>/delete/",
        StudioDeleteView.as_view(),
        name="studio-delete",
    ),
    path("genres/", GenreListView.as_view(), name="genre-list"),
    path(
        "genres/create/",
        GenreCreateView.as_view(),
        name="genre-create",
    ),
    path(
        "genres/<int:pk>/",
        GenreDetailView.as_view(),
        name="genre-detail",
    ),
    path(
        "genres/<int:pk>/update/",
        GenreUpdateView.as_view(),
        name="genre-update",
    ),
    path(
        "genres/<int:pk>/delete/",
        GenreDeleteView.as_view(),
        name="genre-delete",
    ),
    path("critics/", CriticListView.as_view(), name="critic-list"),
    path(
        "critics/<int:pk>/",
        CriticDetailView.as_view(),
        name="critic-detail",
    ),
]
