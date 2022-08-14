import os
import ast

import configparser
import typing
from _collections_abc import Sequence

from common.utils.db_connectors import ConnectorFactory
from common.utils.db_handler import PostgresLoader, RedisStateKeeper

from common.utils.config_validator import PostgresDSL, ConnectorType, \
    SQLQueries, CommonSettings, ElasticDSL, RedisDSL
from common.models.models import MoviesPG

from dotenv import load_dotenv

from elasticsearch import helpers


def migrate_pg_es(query_es: typing.List[Sequence], state_keeper: RedisStateKeeper,
                  dsl_es: typing.Dict, dsl_rs: typing.Dict, chunk_size: int = 100):

    with connector_es(**dsl_es) as es:

        for status_ok, model_updated in helpers.streaming_bulk(es, query_es,
                                                               chunk_size=batch_size):
            if status_ok:
                model_id = model_updated['index']['_id']
                state_keeper.data_handle('kset', 'id', model_id, **dsl_rs)
        else:
            print('Migration pg_es successful')


if __name__ == '__main__':
    load_dotenv()

    # common section
    connector_type = ConnectorType()
    batch_size = CommonSettings().batch_size
    uuid_initial = CommonSettings().uuid_initial

    # redis section
    dsl_rs = RedisDSL().dict()

    connector_rs = ConnectorFactory.connect_to(connector_type.connector_rs)
    redis = RedisStateKeeper(connector_rs)
    redis.data_handle('kset', 'id', uuid_initial, **dsl_rs)

    # pg query constructor section
    queries_path = SQLQueries()

    cfp = configparser.ConfigParser()
    cfp.read(queries_path.sql_queryset_path)

    query = cfp.get("movies", "select", raw=True).replace('\n', ' ')
    query = query.format(redis.data_handle('kget', 'id', **dsl_rs))

    # pg execute query section
    dsl_pg = PostgresDSL().dict()

    connector_pg = ConnectorFactory.connect_to(connector_type.connector_pg)
    pg_loader = PostgresLoader(connector_pg)

    pg_data = pg_loader.data_handle(query, batch_size, **dsl_pg)

    # transform and validation data section
    step_0 = (item for element in pg_data for item in element)
    step_1 = (dict(item) for item in step_0)
    valid = (MoviesPG.parse_obj(item) for item in step_1)

    # es section
    dsl_es = ElasticDSL().dict()
    connector_es = ConnectorFactory.connect_to(connector_type.connector_es)

    query = [{'_index': 'movies', '_id': data.id, '_source': data.json()}
             for
             data in valid]

    migrate_pg_es(query, redis, dsl_es, dsl_rs, batch_size)
