import sqlite3
import psycopg2

import elasticsearch
from elasticsearch import Elasticsearch

import redis
from redis import Redis

import backoff
import logging

from abc import ABC
from contextlib import contextmanager
from typing import Literal, Union

logger = logging.getLogger(__name__)


class _DBConnector(ABC):
    pass


class _SQLiteConnector(_DBConnector):

    @contextmanager
    @backoff.on_exception(backoff.expo, sqlite3.OperationalError,
                          logger=logger, max_tries=30)
    def __call__(self, db_name: str):
        try:
            _connection = sqlite3.connect(db_name)
            _connection.row_factory = sqlite3.Row
            yield _connection

        except sqlite3.OperationalError as err:
            logger.error('SQLite error occurred: {0} {1}'
                         .format(err, self.__class__.__name__))

        _connection.close()


class _PGConnector(_DBConnector):

    @contextmanager
    @backoff.on_exception(backoff.expo, psycopg2.Error,
                          logger=logger, max_tries=30)
    def __call__(self, **dsl):
        try:
            _connection = psycopg2.connect(**dsl)

        except (psycopg2.OperationalError, psycopg2.InterfaceError) as err:
            logger.error('PG error occurred: {0} {1} {2}'
                         .format(err.pgcode,
                                 err.pgerror,
                                 self.__class__.__name__
                                 )
                         )
        else:
            yield _connection

            _connection.commit()


class _ESConnector(_DBConnector):

    @contextmanager
    @backoff.on_exception(backoff.expo, elasticsearch.ElasticsearchException,
                          logger=logger, max_tries=30)
    def __call__(self, **dsl):
        try:
            connection_url = [
                'http://{}:{}'.format(dsl.get('host', '127.0.0.1'),
                                      dsl.get('port', '9200'))]
            _connection = Elasticsearch(connection_url)

        except (elasticsearch.ElasticsearchException) as err:
            logger.error('ES error occurred: {0} {1}'
                         .format(err, self.__class__.__name__)
                         )
        else:
            yield _connection

            _connection.transport.close()


class _RedisConnector(_DBConnector):

    @contextmanager
    @backoff.on_exception(backoff.expo, redis.exceptions,
                          logger=logger, max_tries=30)
    def __call__(self, **dsl):
        try:
            _connection = Redis(**dsl)

        except redis.exceptions as err:
            logger.error('Redis error occurred: {0} {1}'
                         .format(err, self.__class__.__name__)
                         )
        else:
            yield _connection

            _connection.close()


class ConnectorFactory():
    CONNECTIONS = {
        'sql': _SQLiteConnector,
        'pg': _PGConnector,
        'es': _ESConnector,
        'redis': _RedisConnector,
    }

    @classmethod
    def connect_to(cls, connector: Union['sql', 'pg', 'es', 'redis']):
        connector = cls.CONNECTIONS.get(connector)
        if connector:
            return connector()


if __name__ == '__main__':
    ConnectorFactory()
