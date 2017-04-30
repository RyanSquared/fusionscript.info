import functools
import json
import os
import subprocess
from base64 import b64decode

import bcrypt
import sqlalchemy
import sqlalchemy.ext.declarative
from flask import session as req_session
from flask import request
from pygments import highlight
from pygments.formatters import HtmlFormatter

from .fusionscript_pygments import FusionScriptLexer

errors = [
    "Authentication failed",
    "User not logged in",
    "User not found",
    "Incorrect password"
]
[EAUTHFAILED, ENOAUTH, EUSERNOTFOUND,
 EBADPASS] = range(4)
# Get config from XDG_CONFIG_HOME/fs-info/conf.json
# XDG_CONFIG_HOME defaults to $HOME/.config
try:
    conf_path = os.environ['XDG_CONFIG_HOME']
except Exception as e:
    print(f"Error using XDG_CONFIG_HOME: {type(e)}({e})")
    conf_path = os.path.join(os.environ['HOME'], '.config')
    print(f"Falling back to {conf_path}")
with open(os.path.join(conf_path, 'fs-info/conf.json')) as f:
    config = json.loads(f.read())

Base = sqlalchemy.ext.declarative.declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer(), primary_key=True)
    username = sqlalchemy.Column(
        sqlalchemy.String(), unique=True, nullable=False)
    password = sqlalchemy.Column(
        sqlalchemy.String(), nullable=False)


engine = sqlalchemy.create_engine(config["uri"])
Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sqlalchemy.orm.sessionmaker()
db_session = DBSession()

lexer = FusionScriptLexer()
formatter = HtmlFormatter()
rendered_code = {}


class InvalidUsage(Exception):
    def __init__(self, message, status_code=400, payload=()):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        data = dict(self.payload)
        data['message'] = self.message
        return data


def check_auth_for(request, session):
    auth = b64decode(request.headers['Authentication'].split(' ')[1])
    [username, password] = auth.decode('utf-8').split(':')
    try:
        user = db_session.query(User).filter(User.username == username).one()
    except:
        raise InvalidUsage(
            errors[EAUTHFAILED], 401,
            (("reason", errors[EUSERNOTFOUND]), ("user", username)))
    pw_to_check = user.password
    if bcrypt.checkpw(password.encode('utf-8'), pw_to_check):
        print(f"Initializing session for: {username}")
        session['username'] = username
        return
    else:
        raise InvalidUsage(
            errors[EAUTHFAILED],
            (("reason", errors[EBADPASS]), ("user", username)))


def requires_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = req_session.get('username')
        if auth is None:
            if request.headers.get('Authentication'):
                check_auth_for(request, req_session)
                return f(*args, **kwargs)
            raise InvalidUsage(errors[ENOAUTH], 401)
        else:
            print(f"Using session for: {auth}")
            return f(*args, **kwargs)
    return decorated


repos_dir = os.environ.get('REPOS_DIR') or "repos"
icons = {
    "ryansquared":
        "https://avatars0.githubusercontent.com/u/12415837?v=3&s=460",
    "chickennuggers":
        "https://avatars0.githubusercontent.com/u/12415837?v=3&s=460",
    "ryan":
        "https://avatars0.githubusercontent.com/u/12415837?v=3&s=460",
}


def load_code(filename):
    if not rendered_code.get(filename):
        with open(os.path.join('static/snippets', filename)) as code_file:
            rendered_code[filename] = highlight(
                    code_file.read(), lexer, formatter)
    return rendered_code[filename]


def get_values_from(repo, count=10):
    path = os.getcwd()
    os.chdir(repo)
    result = subprocess.run([
        "git", "log", "--pretty=format:%ct\x01%an\x01%s", f"-{count}"
        ], stdout=subprocess.PIPE)
    values = [
        dict(zip(("timestamp", "author", "content"), value.split("\x01")))
        for value in result.stdout.decode('utf-8').split('\n')]
    for value in values:
        value['timestamp'] = int(value['timestamp'])
        value['repo'] = repo.split('/')[-1]
        value['avatar'] = icons[value['author'].lower()]
    os.chdir(path)
    return values[::-1]


def get_repos(directory=repos_dir):
    for folder in os.listdir(directory):
        if folder != "rendered":
            yield folder


types = {
    "html": "text/html",
    "css": "text/css",
    "javascript": "text/javascript"
}
