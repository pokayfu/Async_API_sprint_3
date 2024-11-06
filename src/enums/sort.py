from enum import Enum


class FilmsSortOption(str, Enum):
    asc = "imdb_rating"
    desc = "-imdb_rating"