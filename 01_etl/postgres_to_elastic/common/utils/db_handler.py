from abc import ABC
import typing

import dataclasses
import typing_extensions
from psycopg2.extras import RealDictCursor
from redis import Redis

from .exception_decorator import exception_decorator
from common.utils.db_connectors import ConnectorFactory


class _AbstractDBHandler(ABC):
    pass


class _DBHandler(_AbstractDBHandler):
    def __init__(self, connector: ConnectorFactory, *args, **kwargs):
        self.connector = connector

    def data_handle(self):
        pass


class _SQLReadMixin():
    """Gen of dataclasses covering SQLite3.Row."""

    def _execute_sql(self, *args, **queries) -> typing.Iterable:
        with self.connector(*args) as connection:
            cursor = connection.cursor()
            dataclass_cursor_sqlite_gen = (
                dataclasses.make_dataclass(table,
                                           [('cursor',
                                             typing_extensions.AsyncGenerator,
                                             cursor.execute(query),)
                                            ],
                                           namespace={'class_name': table}
                                           )
                for table, query in queries.items()
            )

            yield from dataclass_cursor_sqlite_gen


class _PostgresCursorMixin():
    """Gen of PG cursor."""

    def _execute_sql(self, query: str, *args, **dsl) -> typing.Optional:
        with self.connector(**dsl) as connection:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query)

            while batch := cursor.fetchmany(*args):
                yield batch


class SQLiteLoader(_DBHandler, _SQLReadMixin):
    """Main SQL tables loader."""

    def data_handle(self, db_name: str, *args, **kwargs) -> typing.Iterable:
        """User implemented handler."""

        result = self._execute_sql(db_name, **kwargs)

        for dataclass_object in result:
            while True:
                cursor = dataclass_object.cursor
                name = dataclass_object.class_name,
                batch = cursor.fetchmany(*args)

                if batch:
                    yield {name: batch}
                else:
                    break


class PostgresSaver():
    """Saves data to PG by execute_values."""

    @exception_decorator
    def _data_load(self, *args) -> typing.Optional:
        """Adapter needed."""
        pass

    @exception_decorator
    def data_handle(self, **dsl) -> typing.Optional:
        """Adapter needed."""
        pass


class PostgresLoader(_DBHandler, _PostgresCursorMixin):
    """Loads data from PG by _PostgresCursorMixin."""

    def data_handle(self, query, *args, **dsl) -> typing.Optional:
        """User implemented handler"""

        pg_loaded_data = self._execute_sql(query, *args, **dsl)

        if pg_loaded_data:
            yield from pg_loaded_data


class RedisStateKeeper(_DBHandler):
    """Saves and retrieves states from Redis."""

    def _kset(self, connection: Redis, *state: typing.Any):
        connection.set(*state,)

    def _kget(self, connection: Redis, *key: typing.Text):
        return connection.get(*key,)

    def _hmset(self, connection: Redis, *state: typing.Any):
        connection.hmset(*state,)

    def _hgetall(self, connection: Redis, *key: typing.Text):
        return connection.hgetall(*key,)

    def data_handle(self, command: typing.Union['kget', 'kset'], *query, **dsl) -> None:
        """User implemented handler"""

        COMMANDS = {
            'kget': self._kget,
            'kset': self._kset,
            'hgetall': self._hgetall,
            'hmset': self._hmset,
        }

        with self.connector(**dsl) as rs:
            return COMMANDS.get(command).__call__(rs, *query)


if __name__ == '__main__':
    SQLiteLoader()
    PostgresSaver()
    PostgresLoader()
    RedisStateKeeper()
