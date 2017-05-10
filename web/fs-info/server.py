from tornado.httpserver import HTTPServer
from tornado.web import Application, FallbackHandler
from tornado.wsgi import WSGIContainer

from .routes import app
from .util import config
from .views import TemplateHandler, IndexHandler, ProjectFileHandler

http_server = HTTPServer(
    Application([
        (r'^/$', IndexHandler),
        (r'^/web/.*', ProjectFileHandler),
        (r'^.*.html$', TemplateHandler),
        (r'^.*', FallbackHandler, {
            'fallback': WSGIContainer(app)
        }),
    ], static_path='./static'),
    ssl_options=config['ssl_options'])
