from pydantic import BaseSettings, Field, StrictStr, StrictInt


class PostgresDSL(BaseSettings):
    """dsl format validation."""

    dbname: StrictStr = Field(..., env='PG_DBNAME')
    user: StrictStr = Field(..., env='PG_USER')
    password: StrictStr = Field(..., env='PG_PASSWORD')
    host: StrictStr = Field(..., env='PG_HOST')
    port: StrictStr = Field(..., env='PG_PORT')


class ElasticDSL(BaseSettings):
    """elasticsearch url settings validation."""

    host: StrictStr = Field(..., env='ES_HOST')
    port: StrictStr = Field(..., env='ES_PORT')


class RedisDSL(BaseSettings):
    """redis url settings validation."""

    host: StrictStr = Field(..., env='RS_HOST')
    port: StrictStr = Field(..., env='RS_PORT')
    charset: StrictStr = Field(..., env='RS_CHARSET')
    decode_responses: StrictStr= Field(..., env='RS_DECODE_RESPONSES')


class ConnectorType(BaseSettings):
    """connector type validation."""

    connector_pg: StrictStr = Field(..., env='CT_PG')
    connector_es: StrictStr = Field(..., env='CT_ES')
    connector_rs: StrictStr = Field(..., env='CT_RS')


class TablesPG(BaseSettings):
    """tables type validation."""

    genre: StrictStr = Field(..., env='TABLE_PG_GENRE')
    person: StrictStr = Field(..., env='TABLE_PG_PERSON')
    film_work: StrictStr = Field(..., env='TABLE_PG_FW')
    genre_film_work: StrictStr = Field(..., env='TABLE_PG_GFW')
    person_film_work: StrictStr = Field(..., env='TABLE_PG_PFW')


class SQLQueries(BaseSettings):
    """SQL queries validation."""

    sql_queryset_path: StrictStr = Field(..., env='SQL_QUERIES_PATH')


class BackoffSettings(BaseSettings):
    """backoff settings type validation."""

    wait_gen: StrictStr = Field(..., env='BACKOFF_WAIT_GEN')
    exception: StrictStr = Field(..., env='BACKOFF_EXCEPTION')
    max_tries: StrictInt = Field(..., env='BACKOFF_MAX_TRIES')


class CommonSettings(BaseSettings):
    """common settings validation."""

    chunk_size: int = Field(..., env='CHUNK_SIZE')
    uuid_initial: StrictStr = Field(..., env='UUID_INITIAL')
    dt_initial: StrictStr = Field(..., env='DT_INITIAL')
    sleep_time_secs: float = Field(..., env='SLEEP_APP_SECS')
