from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from catalog.models import Critic, Genre, Review, Studio, Title


@admin.register(Critic)
class CriticAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("bio",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional info",
            {"fields": ("first_name", "last_name", "email", "bio")},
        ),
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    list_filter = ("country",)
    search_fields = ("name",)


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ("name", "media_type", "release_year", "studio")
    list_filter = ("media_type", "studio", "genres")
    search_fields = ("name",)
    list_select_related = ("studio",)
    filter_horizontal = ("genres", "favorited_by")
    inlines = [ReviewInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("title", "critic", "score", "created_at")
    list_filter = ("score", "title__media_type")
    search_fields = ("title__name", "critic__username")
    list_select_related = ("title", "critic")
