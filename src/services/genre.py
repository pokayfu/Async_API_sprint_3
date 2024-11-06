from functools import lru_cache
from fastapi import Depends
from src.models.genre import Genre
from src.services.elastic import ElasticService, get_elastic_service
from src.services.redis import RedisService, get_redis_service


class GenreService:
    def __init__(self, redis_service: RedisService, elastic_service: ElasticService):
        self._redis_service = redis_service
        self._elastic_service = elastic_service

    async def all(self, **kwargs) -> list[Genre]:
        genres = await self._redis_service._genres_from_cache(**kwargs)
        if not genres:
            genres = await self._elastic_service.get_genres_from_elastic(
                **kwargs
            )
            if not genres:
                return []
            await self._redis_service._put_genres_to_cache(genres, **kwargs)
        return genres

    async def get_by_id(self, genre_id: str) -> Genre | None:
        genre = await self._redis_service._genre_from_cache(genre_id)
        if not genre:
            genre = await self._elastic_service.get_genre_from_elastic(
                genre_id
            )
            if not genre:
                return None
            await self._redis_service._put_genre_to_cache(genre)

        return genre



@lru_cache()
def get_genre_service(
    redis_service: RedisService = Depends(get_redis_service),
    elastic_service: ElasticService = Depends(get_elastic_service),
) -> GenreService:
    return GenreService(redis_service, elastic_service)
