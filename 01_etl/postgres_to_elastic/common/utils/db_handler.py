import dataclasses

import typing
import typing_extensions

from abc import ABC

from common.utils.db_connectors import ConnectorFactory
from .exception_decorator import exception_decorator

from psycopg2.extras import RealDictCursor

from redis import Redis


class _AbstractDBHandler(ABC):
    pass


class _DBHandler(_AbstractDBHandler):
    def __init__(self, connector: ConnectorFactory, *args, **kwargs):
        self.connector = connector

    def data_handle(self):
        pass


class _SQLReadMixin():
    """ Gen of dataclasses covering SQLite3.Row """

    def _execute_sql(self, *args, **queries) -> typing.Iterable:
        with self.connector(*args) as connection:
            cursor = connection.cursor()
            result = (
                dataclasses.make_dataclass(table,
                                           [('cursor',
                                             typing_extensions.AsyncGenerator,
                                             cursor.execute(query),)
                                            ],
                                           namespace={'class_name': table}
                                           )
                for table, query in queries.items()
            )

            yield from result


class _PostgresCursorMixin():
    """ Gen of PG cursor """

    def _execute_sql(self, query: str, *args, **dsl) -> typing.Optional:
        with self.connector(**dsl) as connection:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query)

            while batch := cursor.fetchmany(*args):
                yield batch


class SQLiteLoader(_DBHandler, _SQLReadMixin):
    """ Main SQL tables loader """

    def data_handle(self, db_name: str, *args, **kwargs) -> typing.Iterable:
        """User implemented handler"""

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
    """ Loads data to PG by execute_values"""

    @exception_decorator
    def _data_load(self, *args) -> typing.Optional:
        """ Adapter needed"""
        pass

    @exception_decorator
    def data_handle(self, **dsl) -> typing.Optional:
        """ Adapter needed"""
        pass


class PostgresLoader(_DBHandler, _PostgresCursorMixin):

    def data_handle(self, query, *args, **dsl) -> typing.Optional:
        """User implemented handler"""

        result = self._execute_sql(query, *args, **dsl)

        if result:
            yield from result


class RedisStateKeeper(_DBHandler):

    def _kset(self, connection: Redis, *state: typing.Any):
        connection.set(*state,)

    def _kget(self, connection: Redis, *key: typing.Text):
        return connection.get(*key,)

    def data_handle(self, command: typing.Union['kget', 'kset'], *query, **dsl) -> None:
        """User implemented handler"""

        COMMANDS = {
            'kget': self._kget,
            'kset': self._kset,
        }

        with self.connector(**dsl) as rs:
            return COMMANDS.get(command).__call__(rs, *query)


if __name__ == '__main__':
    SQLiteLoader()
    PostgresSaver()
    PostgresLoader()
    RedisStateKeeper()
