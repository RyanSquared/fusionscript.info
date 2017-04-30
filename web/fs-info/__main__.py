#!/usr/bin/env python3

import json
import sys

from tornado.ioloop import IOLoop

from . import util
from .tornado import http_server

print('== CONFIG ==')
print(json.dumps(util.config, indent=4))
print('==+------+==')


def assert_has(iterable, key):
    if key not in iterable:
        raise KeyError(key, iterable)


for key in ['ssl_options']:
    assert_has(util.config, key)
for key in ['certfile', 'keyfile']:
    assert_has(util.config['ssl_options'], key)

if '--debug' in sys.argv:
    http_server.listen(**{
        option: util.config[option]
        for option in util.config if option in ('address', 'port')})
else:
    http_server.bind(**{
        option: util.config[option]
        for option in util.config if option in ('address', 'port')})
    http_server.start(0)
IOLoop.instance().start()
