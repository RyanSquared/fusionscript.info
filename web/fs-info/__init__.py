from flask import Flask, jsonify
import json
import os
import subprocess

app = Flask(__name__)
icons = {
    'ryansquared':
        'https://avatars0.githubusercontent.com/u/12415837?v=3&s=460',
    'chickennuggers':
        'https://avatars0.githubusercontent.com/u/12415837?v=3&s=460',
    'ryan':
        'https://avatars0.githubusercontent.com/u/12415837?v=3&s=460',
}
repos_dir = os.environ.get('REPOS_DIR') or "repos"


def get_values_from(repo, count=10):
    path = os.getcwd()
    os.chdir(repo)
    result = subprocess.run([
        "git", "log", "--pretty=format:%ct\x01%an\x01%s", f"-{count}"
        ], stdout=subprocess.PIPE)
    values = [
        dict(zip(("timestamp", "author", "content"), value.split("\x01")))
        for value in result.stdout.decode('ascii').split('\n')]
    for value in values:
        value['timestamp'] = int(value['timestamp'])
        value['repo'] = repo.split('/')[-1]
        value['avatar'] = icons[value['author'].lower()]
    os.chdir(path)
    return values


def get_repos(directory=repos_dir):
    return os.listdir(directory)


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
    _dict['clone_url'] = f"https://fusionscript.info/repos/{_dict['name']}"
    return _dict


@app.route('/repos')
def get_repos_json():
    return jsonify([get_json_for(repo) for repo in get_repos()])


@app.route('/repos/<name>/data')
def get_repo_json(name):
    return jsonify(get_json_for(name))
