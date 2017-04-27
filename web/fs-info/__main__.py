#!/usr/bin/env python3

from . import app, util
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from tornado.web import Application, FallbackHandler, RequestHandler
from tornado.web import HTTPError
import jinja2
import json
import sys
import os

print('== CONFIG ==')
print(json.dumps(util.config, indent=4))
print('==+------+==')
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(['templates']),
    block_start_string='<%',
    block_end_string='%>',
    variable_start_string='<<',
    variable_end_string='>>',
    comment_start_string='<#',
    comment_end_string='#>')


def assert_has(iterable, key):
    if key not in iterable:
        raise KeyError(key, iterable)


for key in ['ssl_options']:
    assert_has(util.config, key)
for key in ['certfile', 'keyfile']:
    assert_has(util.config['ssl_options'], key)


env.globals.update(load_code=util.load_code)


class TemplateHandler(RequestHandler):
    def render_template(self, template_name, **kwargs):
        return env.get_template(template_name).render(kwargs)

    def get(self):
        try:
            path = self.request.path[1:]
            return self.write(self.render_template(path))
        except jinja2.exceptions.TemplateNotFound as e:
            raise HTTPError(404, reason=f"File not found: {path}")


class IndexHandler(TemplateHandler):
    def get(self):
        try:
            path = "index.html"
            return self.write(self.render_template(path))
        except jinja2.exceptions.TemplateNotFound as e:
            raise HTTPError(404, reason=f"File not found: {path}")


class ProjectFileHandler(RequestHandler):
    def get(self):
        try:
            path = self.request.path[1:].rstrip("/").split("/")
            if "." not in path[-1]:
                path.append("index.html")
            del path[:1]
            with open(os.path.join("static/web", *path)) as f:
                ext = os.path.splitext(path[-1])[1][1:]
                if util.types.get(ext):
                    self.set_header("Content-Type", util.types[ext])
                return self.write(f.read())
        except jinja2.exceptions.TemplateNotFound as e:
            raise HTTPError(404, reason=f"File not found: {path}")


if '--debug' in sys.argv:
    app.run(host=(util.config.get('address') or '0.0.0.0'),
            port=(util.config.get('port') or '25562'),
            debug=True,
            ssl_context=tuple(util.config.get('ssl_options').values()))

else:
    http_server = HTTPServer(
        Application([
            (r'^/$', IndexHandler),
            (r'^/web/.*', ProjectFileHandler),
            (r'^.*.html$', TemplateHandler),
            (r'^.*', FallbackHandler, {
                'fallback': WSGIContainer(app)
            }),
        ], static_path='./static'),
        ssl_options=util.config['ssl_options'])

    http_server.bind(**{
        option: util.config[option]
        for option in util.config if option in ('address', 'port')
    })
    http_server.start(0)
    IOLoop.instance().start()
