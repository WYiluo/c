from pynostr.relay import Relay
from pynostr.filters import FiltersList, Filters
from pynostr.event import EventKind
from pynostr.base_relay import RelayPolicy
from pynostr.message_pool import MessagePool
import tornado.ioloop
from tornado import gen
import time
import uuid
from crawl import crawl_relay
from relay_list import relay_list
import random
import json
import sys


def gen_crawl_job(relay, since, until, kinds):
    return {
        'relay': relay,
        'since': since,
        'until': until,
        'kinds': kinds
    }

def gen_crawl_jobs(relays, from_ts, to_ts, step, kinds):
    ret = []
    for r in relays:
        since = from_ts
        while since < to_ts:
            ret.append(gen_crawl_job(r, since, since+step, kinds))
            since += step
    return ret

def main():
    args = sys.argv[1:]
    ts_since = int(args[0])
    lasting = int(args[1])
    step = int(args[2])
    kinds = eval(args[3])
    relay_list = args[4]

    with open(relay_list) as file:
        relays = json.load(file)

    jobs = gen_crawl_jobs(relays, ts_since, ts_since+lasting, step, kinds)

    random.shuffle(jobs)

    out_file = args[5]
    with open(out_file, 'w+') as file:
        json.dump(jobs, fp=file)

if __name__=="__main__":
    main()