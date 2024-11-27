from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    verbose_name = _("filmwork genre")
    verbose_name_plural = _("filmwork genres")


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    verbose_name = _("filmwork person")
    verbose_name_plural = _("filmwork persons")


@admin.register(Filmwork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (
        PersonFilmworkInline,
        GenreFilmworkInline,
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass
