from functools import lru_cache
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from pydantic import BaseModel

from src.core.config import settings
from src.db.elastic import get_elastic
from src.enums import FilmsSortOption
from src.models.film import Film, FilmPreview
from src.models.genre import Genre
from src.models.persons import Person


class ElasticService:
    def __init__(self, elastic: AsyncElasticsearch):
        self._elastic = elastic

    async def _get_index_data_by_id(
        self, index: str, id: UUID, model: BaseModel
    ):
        try:
            doc = await self._elastic.get(index=index, id=id)
        except NotFoundError:
            return None
        return model(**doc["_source"])

    def _parse_pagination(self, params: dict):
        page_size = params.get("page_size", 10)
        page = params.get("page", 1)
        return (page - 1) * page_size, page_size

    def _parse_sorting(self, params: dict):
        sort = params.get("sort", None)
        match sort:
            case FilmsSortOption.asc:
                sort_ = [{sort: "asc"}]
            case FilmsSortOption.desc:
                sort_ = [{sort[1:]: "desc"}]
            case _:
                sort_ = None
        return sort_

    def _parse_genre(self, params: dict):
        genre = params.get("genre", None)
        if genre:
            genre = {"match": {"genres": genre}}
        return genre

    def _parse_query(self, params: dict, search_field: str = "title"):
        query = params.get("query", None)
        if query:
            query = {
                "match": {
                    search_field: {
                        "query": query,
                        "fuzziness": 1,
                        "operator": "and",
                    }
                }
            }
        return query

    def _get_es_query_param(self, *args):
        not_none_args = []
        for arg in args:
            if arg:
                not_none_args.append(arg)
        if not not_none_args:
            query = {"match_all": {}}
        else:
            query = {"bool": {"must": not_none_args}}
        return query

    def _parse_query_params(self, params: dict, search_field: str = "title"):
        parsed_params = dict()
        parsed_params["from_"], parsed_params["size"] = self._parse_pagination(
            params
        )
        parsed_params["sort"] = self._parse_sorting(params)

        genre = self._parse_genre(params)
        query = self._parse_query(params, search_field=search_field)
        parsed_params["query"] = self._get_es_query_param(genre, query)
        return parsed_params

    async def _get_index_data_by_query_params(
        self, index: str, model: BaseModel, **params
    ):
        try:
            docs = await self._elastic.search(index=index, **params)
        except NotFoundError:
            return None

        return [model(**doc["_source"]) for doc in docs["hits"]["hits"]]

    async def get_film_from_elastic(self, film_id: str) -> Film | None:
        return await self._get_index_data_by_id(
            settings.movies_index_name, film_id, Film
        )

    async def get_genre_from_elastic(self, genre_id) -> Genre | None:
        return await self._get_index_data_by_id(
            settings.genres_index_name, genre_id, Genre
        )

    async def get_person_from_elastic(self, person_id) -> Person | None:
        return await self._get_index_data_by_id(
            settings.persons_index_name, person_id, Person
        )

    async def get_films_from_elastic(
        self, **kwargs
    ) -> list[FilmPreview] | None:
        params = self._parse_query_params(kwargs)
        return await self._get_index_data_by_query_params(
            settings.movies_index_name, FilmPreview, **params
        )

    async def get_genres_from_elastic(self, **kwargs) -> list[Genre] | None:
        params = self._parse_query_params(kwargs)
        return await self._get_index_data_by_query_params(
            settings.genres_index_name, Genre, **params
        )

    async def get_persons_from_elastic(self, **kwargs) -> list[Person] | None:
        params = self._parse_query_params(kwargs, search_field="full_name")
        return await self._get_index_data_by_query_params(
            settings.persons_index_name, Person, **params
        )

    async def get_films_by_person_from_elastic(self, person_id: str):
        films_by_person = []
        person_data = await self.get_person_from_elastic(person_id)
        if not person_data:
            return None
        films_id = [film["id"] for film in person_data.model_dump()["films"]]
        if not films_id:
            return None
        for id in films_id:
            film = await self.get_film_from_elastic(id)
            films_by_person.append(FilmPreview(**film.model_dump()))
        return films_by_person


@lru_cache()
def get_elastic_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> ElasticService:
    return ElasticService(elastic)
