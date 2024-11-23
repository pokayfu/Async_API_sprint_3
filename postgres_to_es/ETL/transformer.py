from typing import Dict, List

from models import GenreModel, MovieModel, PersonModel
from settings.settings import logger
from settings.settings import file_api_settings


class DataTransformer:
    """Класс для преобразования данных из Postgres для загрузки в Elastic."""

    @staticmethod
    def transform(rows_from_postgres: Dict[str, List[Dict]]) -> Dict[str, List[MovieModel | GenreModel | PersonModel]]:
        """Преобразование сырых данных из БД в объекты для загрузки в Elastic."""
        transformed_data = {
            'movies': [],
            'genres': [],
            'persons': []
        }
        for data_type, rows in rows_from_postgres.items():
            for row in rows:
                try:
                    if data_type == 'movies':
                        if short_name := row.get("short_name"):
                            row["url"] = file_api_settings.file_api_domain + short_name
                        transformed_data['movies'].append(MovieModel(**row))
                    elif data_type == 'genres':
                        transformed_data['genres'].append(GenreModel(**row))
                    elif data_type == 'persons':
                        transformed_data['persons'].append(PersonModel(**row))
                except Exception as er:
                    logger.error(f'Ошибка преобразования данных {row=}, {er=}')
                    continue
        return transformed_data
