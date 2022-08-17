from abc import ABC
from pydantic import BaseModel, StrictStr, StrictFloat, UUID4, validator
from typing import Iterable, List, Optional


class AbstractValidator(ABC):
    pass


class ModelValidator(AbstractValidator, BaseModel):
    pass


class GenresElastic(ModelValidator):
    """pg input parser model for genres table."""

    name: StrictStr


class PersonInFilm(ModelValidator):
    """pg input parser model for person table."""

    name: StrictStr


class PersonInFilmByID(ModelValidator):
    """pg input parser for custom person aggregation."""

    id: UUID4
    name: StrictStr


class MoviesPG(ModelValidator):
    """pg main parser preparing data for further validation."""

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
    def unpack_field_data(cls, data_packed: Iterable):
        """transform raw data for es field format."""

        if data_packed:
            return [data_to_transform.name for data_to_transform in data_packed]
        return []
