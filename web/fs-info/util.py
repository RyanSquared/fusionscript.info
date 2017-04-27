from pygments import highlight
from pygments.formatters import HtmlFormatter
from .fusionscript_pygments import FusionScriptLexer
from os import environ as env
from os import path
import json

# Get config from XDG_CONFIG_HOME/fs-info/conf.json
# XDG_CONFIG_HOME defaults to $HOME/.config
try:
    conf_path = env['XDG_CONFIG_HOME']
except Exception as e:
    print(f"Error using XDG_CONFIG_HOME: {type(e)}({e})")
    conf_path = path.join(env['HOME'], '.config')
    print(f"Falling back to {conf_path}")
with open(path.join(conf_path, 'fs-info/conf.json')) as f:
    config = json.loads(f.read())

lexer = FusionScriptLexer()
formatter = HtmlFormatter()
rendered_code = {}


def load_code(filename):
    if not rendered_code.get(filename):
        with open(path.join('static/snippets', filename)) as code_file:
            rendered_code[filename] = highlight(
                    code_file.read(), lexer, formatter)
    return rendered_code[filename]


types = {
    "html": "text/html",
    "css": "text/css",
    "javascript": "text/javascript"
}
