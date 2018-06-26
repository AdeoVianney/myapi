import logging
from os import getenv
from sys import exit

from celery import Celery

LOG = logging.getLogger('vptressource')

sentinel_port = getenv('SENTINEL_PORT', '26379')
redis_db = getenv('REDIS_DB', '1')
sentinel_host = getenv('SENTINEL_HOST', '127.0.0.1')
sentinel_master_name = getenv('SENTINEL_MASTER_NAME', 'mymaster')

if sentinel_host is None:
    LOG.error('"SENTINEL_HOST" is not set, exiting...')
    exit(1)

if redis_db is None:
    LOG.error('"REDIS_DB" is not set, exiting...')
    exit(1)

if sentinel_master_name is None:
    LOG.error('"SENTINEL_MASTER_NAME" is not set, exiting...')
    exit(1)

sentinel_url = 'sentinel://{host}:{port}/{db}'.format(
    host=sentinel_host, port=sentinel_port, db=redis_db)

CONSUMER_APP = Celery('vptressource')
CONSUMER_APP.conf.broker_url = sentinel_url 
CONSUMER_APP.conf.result_backend = sentinel_url 
CONSUMER_APP.conf.broker_transport_options = {'master_name': sentinel_master_name}
CONSUMER_APP.conf.result_backend_transport_options = {'master_name': sentinel_master_name}
CONSUMER_APP.conf.task_track_started = True