import os
import time

from redis import StrictRedis

redis = StrictRedis(host=os.getenv('DEFAULT_REDIS_CACHE', 'localhost'), port=6379)

pubsub = redis.pubsub()
pubsub.psubscribe('__keyspace@0__:email_event')

print('Starting message loop', flush=True)
while True:
    message = pubsub.get_message()
    if message:
        if message['data'] == b'expired':
            # send email
            print('sent!')

    time.sleep(0.01)
