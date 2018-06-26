from __future__ import absolute_import
import time

from consumer.celery import CONSUMER_APP
from celery.result import AsyncResult


@CONSUMER_APP.task(name='vptressource.post', bind=True)
def post(self, *args, **kwargs):
    try:
        output = {
            'results': [{
                'id': 'awesome-id',
                'description': kwargs['description'],
            }],
            'success': True,
            'error_msg': None,
        }
        time.sleep(15)
        return output
    except KeyError:
        return {
            'success': False,
            'error_msg': 'No description provided',
        }