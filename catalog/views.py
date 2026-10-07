from django.contrib.auth import login, get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Avg, Count, F, Prefetch, ProtectedError
from catalog.forms import (
    CriticCreationForm,
    ReviewForm,
    SearchForm,
    TitleFilterForm,
    TitleForm,
)
from catalog.models import Title, Review, Studio, Genre
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.db.models import ProtectedError
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


def index(request):
    top_titles = (
        Title.objects.annotate(
            avg_score=Avg("reviews__score"),
            num_reviews=Count("reviews"),
        )
        .filter(num_reviews__gt=0)
        .order_by("-avg_score", "name")[:5]
    )
    context = {
        "num_titles": Title.objects.count(),
        "num_movies": Title.objects.filter(
            media_type=Title.MediaType.MOVIE
        ).count(),
        "num_games": Title.objects.filter(
            media_type=Title.MediaType.GAME
        ).count(),
        "num_reviews": Review.objects.count(),
        "top_titles": top_titles,
    }
    return render(request, "catalog/index.html", context=context)


@login_required
@require_POST
def toggle_favorite(request, pk: int):
    title = get_object_or_404(Title, pk=pk)
    if title.favorited_by.filter(pk=request.user.pk).exists():
        title.favorited_by.remove(request.user)
    else:
        title.favorited_by.add(request.user)
    return redirect(title)


class SearchMixin:
    search_field = "name"

    def get_queryset(self):
        queryset = super().get_queryset()
        form = SearchForm(self.request.GET)
        if form.is_valid() and form.cleaned_data["q"]:
            return queryset.filter(
                **{f"{self.search_field}__icontains": form.cleaned_data["q"]}
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm(self.request.GET)
        return context


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class SignUpView(generic.CreateView):
    form_class = CriticCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("catalog:index")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("catalog:index")
        else:
            return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class TitleListView(SearchMixin, generic.ListView):
    model = Title
    queryset = (
        Title.objects.select_related("studio")
        .prefetch_related("genres")
        .annotate(avg_score=Avg("reviews__score"))
        .order_by("name")
    )
    paginate_by = 6
    sort_options = {
        "name": ("name",),
        "rating": (F("avg_score").desc(nulls_last=True), "name"),
        "newest": ("-release_year", "name"),
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        form = TitleFilterForm(self.request.GET)
        if not form.is_valid():
            return queryset

        media_type = form.cleaned_data["media_type"]
        if media_type:
            queryset = queryset.filter(media_type=media_type)

        sort = form.cleaned_data["sort"] or "name"
        return queryset.order_by(*self.sort_options[sort])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = TitleFilterForm(self.request.GET)
        return context


class TitleDetailView(generic.DetailView):
    model = Title
    queryset = (
        Title.objects.select_related("studio")
        .prefetch_related(
            "genres",
            Prefetch(
                "reviews",
                queryset=Review.objects.select_related("critic"),
            ),
        )
        .annotate(
            avg_score=Avg("reviews__score"),
            num_reviews=Count("reviews"),
        )
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            context["user_review"] = Review.objects.filter(
                critic=user,
                title=self.object,
            ).first()
            context["review_form"] = ReviewForm()
            context["is_favorite"] = self.object.favorited_by.filter(
                pk=user.pk
            ).exists()
        return context


class StudioListView(SearchMixin, generic.ListView):
    model = Studio
    queryset = Studio.objects.annotate(
        num_titles=Count("titles")
    ).order_by("name")
    paginate_by = 10


class StudioDetailView(generic.DetailView):
    model = Studio
    queryset = Studio.objects.prefetch_related("titles")


class GenreListView(generic.ListView):
    model = Genre
    queryset = Genre.objects.annotate(
        num_titles=Count("titles")
    ).order_by("name")
    paginate_by = 20


class GenreDetailView(generic.DetailView):
    model = Genre
    queryset = Genre.objects.prefetch_related(
        Prefetch("titles", queryset=Title.objects.select_related("studio"))
    )


class CriticListView(SearchMixin, generic.ListView):
    model = get_user_model()
    queryset = (
        get_user_model()
        .objects.annotate(num_reviews=Count("reviews"))
        .order_by("username")
    )
    search_field = "username"
    paginate_by = 10


class CriticDetailView(generic.DetailView):
    model = get_user_model()
    queryset = get_user_model().objects.prefetch_related(
        Prefetch("reviews", queryset=Review.objects.select_related("title")),
        "favorite_titles",
    )


class TitleCreateView(StaffRequiredMixin, generic.CreateView):
    model = Title
    form_class = TitleForm
    template_name = "catalog/form.html"
    extra_context = {"cancel_url": reverse_lazy("catalog:title-list")}


class TitleUpdateView(StaffRequiredMixin, generic.UpdateView):
    model = Title
    form_class = TitleForm
    template_name = "catalog/form.html"


class TitleDeleteView(StaffRequiredMixin, generic.DeleteView):
    model = Title
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:title-list")


class StudioCreateView(StaffRequiredMixin, generic.CreateView):
    model = Studio
    fields = ("name", "country")
    template_name = "catalog/form.html"
    extra_context = {"cancel_url": reverse_lazy("catalog:studio-list")}


class StudioUpdateView(StaffRequiredMixin, generic.UpdateView):
    model = Studio
    fields = ("name", "country")
    template_name = "catalog/form.html"


class StudioDeleteView(StaffRequiredMixin, generic.DeleteView):
    model = Studio
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:studio-list")

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            return self.render_to_response(
                self.get_context_data(
                    error=(
                        "This studio still has titles. "
                        "Delete them or move them to another studio first."
                    )
                )
            )


class GenreCreateView(StaffRequiredMixin, generic.CreateView):
    model = Genre
    fields = ("name",)
    template_name = "catalog/form.html"
    extra_context = {"cancel_url": reverse_lazy("catalog:genre-list")}


class GenreUpdateView(StaffRequiredMixin, generic.UpdateView):
    model = Genre
    fields = ("name",)
    template_name = "catalog/form.html"


class GenreDeleteView(StaffRequiredMixin, generic.DeleteView):
    model = Genre
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:genre-list")


class ReviewCreateView(LoginRequiredMixin, generic.CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "catalog/form.html"

    def dispatch(self, request, *args, **kwargs):
        self.title = get_object_or_404(Title, pk=kwargs["pk"])
        if (
                request.user.is_authenticated
                and Review.objects.filter(
            critic=request.user,
            title=self.title,
        ).exists()
        ):
            return redirect(self.title)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.critic = self.request.user
        form.instance.title = self.title
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.title.get_absolute_url()
        return context


class ReviewUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "catalog/form.html"

    def get_queryset(self):
        return Review.objects.filter(critic=self.request.user)


class ReviewDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Review
    template_name = "catalog/confirm_delete.html"

    def get_queryset(self):
        return Review.objects.filter(critic=self.request.user)

    def get_success_url(self):
        return self.object.title.get_absolute_url()
