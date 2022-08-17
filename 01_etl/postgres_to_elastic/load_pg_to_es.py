import datetime
import typing
from _collections_abc import Sequence
from time import sleep


import configparser
from dotenv import load_dotenv
from elasticsearch import helpers

from common.models.models import MoviesPG
from common.utils.config_validator import CommonSettings, ConnectorType, \
    ElasticDSL, PostgresDSL, RedisDSL, SQLQueries
from common.utils.db_connectors import ConnectorFactory
from common.utils.db_handler import PostgresLoader, RedisStateKeeper


def migrate_pg_es(query_es: typing.List[Sequence],
                  state_keeper: RedisStateKeeper,
                  dsl_es: typing.Dict, dsl_rs: typing.Dict,
                  chunk_size: int = 100):
    """main function for migration pg to es."""

    with connector_es(**dsl_es) as es:

        for status_ok, model_updated in helpers.streaming_bulk(es, query_es,
                                                               chunk_size=chunk_size):
            if status_ok:
                model_id = model_updated['index']['_id']
                redis_dict_process = {'id': model_id,
                                   'updated_at': str(datetime.datetime.now())}
                redis.data_handle('hmset',
                                  'migrate_control', redis_dict_process,
                                  **dsl_rs)


if __name__ == '__main__':
    load_dotenv()

    # common section
    connector_type = ConnectorType()
    chunk_size = CommonSettings().chunk_size
    uuid_initial = CommonSettings().uuid_initial
    dt_initial = CommonSettings().dt_initial
    sleep_time_secs = CommonSettings().sleep_time_secs

    # redis section
    dsl_rs = RedisDSL().dict()

    connector_rs = ConnectorFactory.connect_to(connector_type.connector_rs)
    redis = RedisStateKeeper(connector_rs)

    redis_dict_init = {'id': uuid_initial, 'updated_at': dt_initial}
    redis.data_handle('hmset', 'migrate_control', redis_dict_init, **dsl_rs)


    # pg query constructor section
    queries_path = SQLQueries()
    cfp = configparser.ConfigParser()

    # pg section
    dsl_pg = PostgresDSL().dict()

    connector_pg = ConnectorFactory.connect_to(connector_type.connector_pg)
    pg_loader = PostgresLoader(connector_pg)

    # es section
    dsl_es = ElasticDSL().dict()
    connector_es = ConnectorFactory.connect_to(connector_type.connector_es)


    while True:
        # pg query constructor section
        cfp.read(queries_path.sql_queryset_path)

        query = cfp.get("movies", "select", raw=True).replace('\n', ' ')
        query_pg_variables = redis.data_handle('hgetall', 'migrate_control',
                                               **dsl_rs)

        query = query.format(query_pg_variables.get('id'),
                             query_pg_variables.get('updated_at'))

        # pg execute query section
        pg_data = pg_loader.data_handle(query, chunk_size, **dsl_pg)

        # transform and validation data section
        step_0 = (item for element in pg_data for item in element)
        step_1 = (dict(item) for item in step_0)
        valid = (MoviesPG.parse_obj(item) for item in step_1)

        # es query constructor section
        query = [{'_index': 'movies', '_id': data.id, '_source': data.json()}
                 for
                 data in valid]

        # es migrate section
        migrate_pg_es(query, redis, dsl_es, dsl_rs, chunk_size=chunk_size)
        sleep(sleep_time_secs)
