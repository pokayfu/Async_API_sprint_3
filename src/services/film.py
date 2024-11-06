from functools import lru_cache
from fastapi import Depends
from src.models.film import Film, FilmPreview
from src.services.elastic import ElasticService, get_elastic_service
from src.services.redis import RedisService, get_redis_service


class FilmService:
    def __init__(self, redis_service: RedisService, elastic_service: ElasticService):
        self._redis_service = redis_service
        self._elastic_service = elastic_service
    
    async def all(self, **kwargs) -> list[FilmPreview]:
        films = await self._redis_service._films_from_cache(**kwargs)
        if not films:
            films = await self._elastic_service.get_films_from_elastic(
                **kwargs
            )
            if not films:
                return []
            await  self._redis_service._put_films_to_cache(films, **kwargs)
        return films

    async def get_by_id(self, film_id: str) -> Film | None:
        film = await self._redis_service._film_from_cache(film_id)
        if not film:
            film = await self._elastic_service.get_film_from_elastic(film_id)
            if not film:
                return None
            await  self._redis_service._put_film_to_cache(film)
        return film

@lru_cache()
def get_film_service(
    redis_service: RedisService = Depends(get_redis_service),
    elastic_service: ElasticService = Depends(get_elastic_service),
) -> FilmService:
    return FilmService(redis_service, elastic_service)
