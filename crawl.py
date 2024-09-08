from pynostr.relay import Relay
from pynostr.filters import FiltersList, Filters
from pynostr.event import EventKind
from pynostr.base_relay import RelayPolicy
from pynostr.message_pool import MessagePool
import tornado.ioloop
from tornado import gen
import time
import uuid
import os
import json
import sys

def crawl_relay(io_loop, job, out_dir, filename):
    message_pool = MessagePool(first_response_only=False)
    policy = RelayPolicy()
    relay = job['relay']
    since = job['since']
    until = job['until']
    kinds = job['kinds']

    r = Relay(
        relay,
        message_pool,
        io_loop,
        policy,
        timeout=3
    )

    filters = FiltersList([Filters(kinds=kinds, since=since, until=until)])
    subscription_id = uuid.uuid1().hex

    r.add_subscription(subscription_id, filters)
    
    ret = True
    try:
        io_loop.run_sync(r.connect)
        file = os.path.join(out_dir, filename)
        with open(file, 'a+') as f:
            while message_pool.has_events():
                event_msg = message_pool.get_event()
                print(event_msg.event, file=f)
    except:
        ret = False

    r.close()
    return ret