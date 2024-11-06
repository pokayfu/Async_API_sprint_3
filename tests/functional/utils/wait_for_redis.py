import time
import backoff
import logging
from redis import Redis
from tests.functional.settings import test_settings


def handle_backoff(details):
    logging.error("Backing off {wait:0.1f} seconds after {tries} tries. Calling function {targer}".format(**details))

@backoff.on_exception(backoff.expo, (ConnectionError,), on_backoff=handle_backoff)
def launch_redis_connection():
    redis = Redis.from_url(test_settings.redis_dsn)
    if not redis.ping():
        raise ConnectionError("Could not connect to redis")
    return redis


if __name__ == '__main__':
    redis = launch_redis_connection()
    