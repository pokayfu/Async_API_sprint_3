from elasticsearch import Elasticsearch
from tests.functional.settings import test_settings
import logging
import backoff


def handle_backoff(details):
    logging.error("Backing off {wait:0.1f} seconds after {tries} tries. Calling function {targer}".format(**details))

@backoff.on_exception(backoff.expo, (ConnectionError,), on_backoff=handle_backoff)
def launch_elastic_connection():
    es_client = Elasticsearch(test_settings.elastic_dsn)
    if not es_client.ping():
        raise ConnectionError("Could not connect to elasticsearch")
    return es_client


if __name__ == '__main__':
    es_client = launch_elastic_connection()
    