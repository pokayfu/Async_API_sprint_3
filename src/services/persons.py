from functools import lru_cache
from fastapi import Depends
from src.models.film import FilmPreview
from src.models.persons import Person
from src.services.elastic import ElasticService, get_elastic_service
from src.services.redis import RedisService, get_redis_service


class PersonService:
    def __init__(self, redis_service: RedisService, elastic_service: ElasticService):
        self._redis_service = redis_service
        self._elastic_service = elastic_service

    async def all(self, **kwargs) -> list[Person]:
        persons = await self._redis_service._persons_from_cache(**kwargs)
        if not persons:
            persons = await self._elastic_service.get_persons_from_elastic(
                **kwargs
            )
            if not persons:
                return []
            await self._redis_service._put_persons_to_cache(persons, **kwargs)
        return persons

    async def get_by_id(self, person_id: str) -> Person | None:
        person = await self._redis_service._person_from_cache(person_id)
        if not person:
            person = await self._elastic_service.get_person_from_elastic(
                person_id
            )
            if not person:
                return None
            await self._redis_service._put_person_to_cache(person)
        return person

    async def get_films_by_person(
        self, person_id: str
    ) -> list[FilmPreview] | None:
        films = await self._redis_service._films_by_person_from_cache(person_id)
        if not films:
            films = (
                await self._elastic_service.get_films_by_person_from_elastic(
                    person_id
                )
            )
            if not films:
                return None
            await self._redis_service._put_films_by_person_to_cache(
                person_id=person_id, films=films
            )
        return films


@lru_cache()
def get_person_service(
    redis: RedisService = Depends(get_redis_service),
    elastic_service: ElasticService = Depends(get_elastic_service),
) -> PersonService:
    return PersonService(redis, elastic_service)
