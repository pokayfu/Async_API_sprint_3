from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from src.models.film import Film, FilmPreview
from src.models.filters import FilmSearching, FilmsGenreFilter
from src.services.film import FilmService, get_film_service

router = APIRouter()


@router.get(
    "/{film_id}", response_model=Film, summary="Retrieve film details by ID"
)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    """
    Fetch detailed information about a film, including title,
    genres, imdb rating, actors, and other information
    by providing its unique film ID
    """
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="film not found"
        )

    return Film(**film.model_dump(by_alias=True))


@router.get(
    "/",
    response_model=list[FilmPreview],
    summary="Retrieve a list of films with pagination and filters",
)
async def get_films(
    params: Annotated[FilmsGenreFilter, Query(description="Query params")],
    film_service: FilmService = Depends(get_film_service),
) -> list[Film]:
    """
    Fetch a paginated list of films with optional sorting by fields
    like IMDb rating and optional filtering by genre.
    The response contains a film id, and basic details
    like title and rating.
    """
    films = await film_service.all(
        page_size=params.page_size,
        page=params.page,
        sort=params.sort,
        genre=params.genre,
    )
    return films


@router.get(
    "/search/",
    response_model=list[FilmPreview],
    summary="Search films by title with pagination and sorting",
)
async def search_films_by_title(
    params: Annotated[FilmSearching, Query(description="Query params")],
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmPreview]:
    """
    Perform a search for films by their title. Supports pagination
    for managing large result sets and allows sorting
    by fields such as IMDb rating. The response contains a film id,
    and basic details like title and imdb rating.
    """
    films = await film_service.all(
        page_size=params.page_size,
        page=params.page,
        sort=params.sort,
        query=params.query,
    )
    return films
