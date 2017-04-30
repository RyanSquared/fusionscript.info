import json
import os
from base64 import b64decode

import bcrypt
import sqlalchemy
from flask import session as req_session
from flask import Flask, jsonify, request

from .util import (InvalidUsage, User, check_auth_for, get_repos,
                   get_values_from, repos_dir, requires_auth, session)

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.errorhandler(InvalidUsage)
def invalid_usage_handler(error):
    result = error.to_dict()
    return jsonify(result), error.status_code


@app.route('/login', methods=['POST'])
def init_login():
    check_auth_for(request, req_session)


@app.route('/new/user', methods=['POST'])
def new_user():
    auth = b64decode(request.headers['Authentication'].split(' ')[1])
    [username, password] = auth.decode('utf-8').split(':')
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        user = User(username=username, password=hashed_pw)
        session.add(user)
        session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        session.rollback()
        return '', 409
    except:
        return '', 500
    else:
        return ''


@app.route('/test_login')
@requires_auth
def test_login():
    return "If you see this, you are logged in."


@app.route('/updates/<int:limit>')
def get_updates(limit):
    commits = []
    for repo in get_repos():
        for commit in get_values_from(os.path.join(repos_dir, repo), limit):
            for i, stored_commit in enumerate(commits):
                if commit['timestamp'] > stored_commit['timestamp']:
                    commits.insert(i, commit)
                    break
            else:
                commits.insert(0, commit)
    return jsonify(commits[:limit])


def get_json_for(repo, directory=repos_dir):
    _dict = {"target": repo}
    with open(os.path.join(directory, repo, '.git', 'data.json')) as f:
        _dict.update(json.loads(f.read()))
    _dict['clone_url'] = f"git://fusionscript.info/repos/{_dict['name']}"
    return _dict


@app.route('/repos')
def get_repos_json():
    return jsonify([get_json_for(repo) for repo in get_repos()])


@app.route('/repos/<name>/data')
def get_repo_json(name):
    return jsonify(get_json_for(name))
