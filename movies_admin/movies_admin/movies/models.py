import uuid
import requests

from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class FilmworkType(models.TextChoices):
    MOVIE = "movie", _("movie")
    TV_SHOW = "tv show", _("tv show")


class MinioStorage(Storage):
    def _save(self, name, content: InMemoryUploadedFile):
        r = requests.post(
            f'http://{settings.FILE_API_UVICORN_HOST}:{settings.FILE_API_UVICORN_PORT}/api/v1/files/upload', params={"path": content.name}, files={'file': (content.name, content, content.content_type)}
        )
        return r.json().get('short_name')

    def _open(self, name):
        return requests.get(f'http://{settings.FILE_API_UVICORN_HOST}:{settings.FILE_API_UVICORN_PORT}/api/v1/files/download/{name}')
    
    def url(self, name):
        return  f'http://{settings.FILE_API_UVICORN_HOST_DIRECT}:{settings.FILE_API_UVICORN_PORT}/api/v1/files/download/{name}'

    def exists(self, name):
        return False


class Filmwork(UUIDMixin, TimeStampedMixin):
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)
    creation_date = models.DateField(_("creation date"), blank=True, null=True)
    rating = models.DecimalField(
        _("rating"), max_digits=3, decimal_places=1, blank=True, null=True
    )
    type = models.CharField(
        _("type"),
        max_length=7,
        choices=FilmworkType.choices,
        default=FilmworkType.MOVIE,
    )
    file = models.FileField(storage=MinioStorage(), null=True)
    genres = models.ManyToManyField(to="Genre", through="GenreFilmwork")
    persons = models.ManyToManyField("Person", through="PersonFilmwork")

    def __str__(self):
        return str(self.title)

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = _("filmwork")
        verbose_name_plural = _("filmworks")


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_("name"), max_length=255, unique=True)
    description = models.TextField(_("description"), blank=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _("genre")
        verbose_name_plural = _("genres")


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(
        "Filmwork", on_delete=models.CASCADE, verbose_name=_("filmwork")
    )
    genre = models.ForeignKey(
        "Genre", on_delete=models.CASCADE, verbose_name=_("genre")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        unique_together = ["film_work", "genre"]


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(_("full name"))

    def __str__(self):
        return str(self.full_name)

    class Meta:
        db_table = 'content"."person'
        verbose_name = _("person")
        verbose_name_plural = _("persons")


class Role(models.TextChoices):
    ACTOR = "actor", _("Actor")
    DIRECTOR = "director", _("Director")
    WRITER = "writer", _("Writer")


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey(
        "Filmwork", on_delete=models.CASCADE, verbose_name=_("filmwork")
    )
    person = models.ForeignKey(
        "Person", on_delete=models.CASCADE, verbose_name=_("person")
    )
    role = models.CharField(
        _("type"),
        max_length=15,
        choices=Role.choices,
        default=Role.ACTOR,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        unique_together = ["film_work", "person", "role"]
