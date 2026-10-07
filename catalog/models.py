from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Critic(AbstractUser):
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ["username"]
        verbose_name = "critic"
        verbose_name_plural = "critics"

    def __str__(self):
        return f"{self.username} {self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("catalog:genre-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class Studio(models.Model):
    name = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("catalog:studio-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.name} | {self.country}"


class Title(models.Model):
    class MediaType(models.TextChoices):
        MOVIE = "movie", "Movie"
        GAME = "game", "Video game"

    name = models.CharField(max_length=255)
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
    )
    release_year = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True)
    studio = models.ForeignKey(
        Studio,
        on_delete=models.PROTECT,
        related_name="titles",
    )
    genres = models.ManyToManyField(Genre, related_name="titles")
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="favorite_titles",
        blank=True,
    )

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("catalog:title-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.name} ({self.get_media_type_display()})"


class Review(models.Model):
    critic = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["critic", "title"],
                name="unique_review_per_critic_and_title",
            ),
        ]

    def __str__(self):
        return f"{self.critic.username} - {self.title.name}: {self.score}"

    def get_absolute_url(self):
        return self.title.get_absolute_url()
