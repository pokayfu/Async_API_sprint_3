from functools import lru_cache
from typing import Annotated, Any
from src.db.redis import get_redis
from redis.asyncio import Redis
from fastapi import Depends
from src.models.film import Film, FilmPreview
from src.models.genre import Genre
from src.models.persons import Person
from src.services.elastic import ElasticService, get_elastic_service
from src.services.utils import get_key_by_args
from src.core.config import settings
from orjson import orjson


class RedisService:
    def __init__(self, redis: Annotated[Redis, Depends(get_redis)]) -> None:
        self.redis = redis

    async def _films_by_person_from_cache(
        self, *args, **kwargs
    ) -> list[FilmPreview] | None:
        key = f"films_by_person: {args[0]}"
        data = await self.redis.get(key)
        if not data:
            return None
        return [FilmPreview.parse_raw(item) for item in orjson.loads(data)]

    async def _film_from_cache(self, film_id: str) -> Film | None:
        key = f"film: {film_id}"
        data = await self.redis.get(key)
        if not data:
            return None
        film = Film.parse_raw(data)
        return film

    async def _films_from_cache(self, **kwargs) -> list[FilmPreview] | None:
        key = f"films: {await get_key_by_args(**kwargs)}"
        data = await self.redis.get(key)
        if not data:
            return None

        return [FilmPreview.parse_raw(item) for item in orjson.loads(data)]

    async def _put_film_to_cache(self, film: Film):
        key = f"film: {film.id}"
        await self.redis.set(
            key, film.json(), settings.cache_expire_in_seconds
        )

    async def _put_films_to_cache(self, films: list[FilmPreview], **kwargs):
        key = f"films: {await get_key_by_args(**kwargs)}"
        await self.redis.set(
            key,
            orjson.dumps([film.json() for film in films]),
            settings.cache_expire_in_seconds,
        )
        
    async def _genre_from_cache(self, genre_id: str) -> Genre | None:
            key = f"genre: {genre_id}"
            data = await self.redis.get(key)
            if not data:
                return None
            genre = Genre.model_validate_json(data)
            return genre

    async def _put_genre_to_cache(self, genre: Genre):
        key = f"genre: {genre.id}"
        await self.redis.set(
            key, genre.model_dump_json(), settings.cache_expire_in_seconds
        )

    async def _genres_from_cache(self, **kwargs) -> list[Genre] | None:
        key = f"genres: {await get_key_by_args(**kwargs)}"
        data = await self.redis.get(key)
        if not data:
            return None
        return [Genre.model_validate_json(item) for item in orjson.loads(data)]

    async def _put_genres_to_cache(self, genres: list[Genre], **kwargs):
        key = f"genres: {await get_key_by_args(**kwargs)}"
        await self.redis.set(
            key,
            orjson.dumps([genre.model_dump_json() for genre in genres]),
            settings.cache_expire_in_seconds,
        )

    async def _put_person_to_cache(self, person: Person):
        key = f"person: {person.person_id}"
        await self.redis.set(
            key, person.json(), settings.cache_expire_in_seconds
        )

    async def _put_persons_to_cache(self, persons: list[Person], **kwargs):
        key = f"persons: {await get_key_by_args(**kwargs)}"
        await self.redis.set(
            key,
            orjson.dumps([person.json() for person in persons]),
            settings.cache_expire_in_seconds,
        )

    async def _person_from_cache(self, person_id: str) -> Person | None:
        key = f"person: {person_id}"
        data = await self.redis.get(key)
        if not data:
            return None
        person = Person.parse_raw(data)
        return person

    async def _persons_from_cache(self, **kwargs) -> list[Person] | None:
        key = f"persons: {await get_key_by_args(**kwargs)}"
        data = await self.redis.get(key)
        if not data:
            return None
        return [Person.parse_raw(item) for item in orjson.loads(data)]

    async def _put_films_by_person_to_cache(
        self, person_id: str, films: list[FilmPreview], **kwargs
    ):
        key = f"films_by_person: {person_id}"
        await self.redis.set(
            key,
            orjson.dumps([film.json() for film in films]),
            settings.cache_expire_in_seconds,
        )



@lru_cache()
def get_redis_service(
    redis: Redis = Depends(get_redis),
) -> RedisService:
    return RedisService(redis)
