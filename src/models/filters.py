from pydantic import BaseModel, Field

from src.enums import FilmsSortOption


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Page size")


class FilmsSorting(BaseModel):
    sort: FilmsSortOption | None = Field(
        default=None, description="Sort films by rating value"
    )


class FilmsGenreFilter(Pagination, FilmsSorting):
    genre: str | None = Field(
        default=None, description="Filter films by genre name"
    )


class FilmSearching(Pagination, FilmsSorting):
    query: str | None = Field(
        default=None, description="Search films by query"
    )
