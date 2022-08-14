import typing

from abc import ABC
from typing import List, Optional, Any
from pydantic import BaseModel, StrictStr, StrictFloat, UUID4, validator


class AbstractValidator(ABC):
    pass


class ModelValidator(AbstractValidator, BaseModel):
    pass


class GenresElastic(ModelValidator):
    name: StrictStr


class PersonInFilm(ModelValidator):
    name: StrictStr


class PersonInFilmByID(ModelValidator):
    id: UUID4
    name: StrictStr


class MoviesPG(ModelValidator):
    id: UUID4
    imdb_rating: Optional[StrictFloat]
    genre: Optional[List[GenresElastic]]
    title: StrictStr
    description: Optional[StrictStr]
    director: Optional[List[PersonInFilm]]
    actors_names: Optional[List[PersonInFilm]]
    writers_names: Optional[List[PersonInFilm]]
    actors: Optional[List[PersonInFilmByID]]
    writers: Optional[List[PersonInFilmByID]]

    @validator('actors_names', 'writers_names', 'director', 'genre')
    def unpack_field_data(cls, data_packed: typing.Iterable):
        if data_packed:
            return [item.name for item in data_packed]
        return []
