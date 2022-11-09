"""Specxplorer entry point.

Specxplorer is ...
"""

import json
import collections
import sys
import os

import flask
from pygments import highlight, lexers, formatters
import requests
import yaml

app = flask.Flask(__name__)

colors = [
    "w3-amber",
    "w3-aqua",
    "w3-blue",
    "w3-light-blue",
    "w3-brown",
    "w3-cyan",
    "w3-blue-grey",
    "w3-green",
    "w3-light-green",
    "w3-indigo",
    "w3-khaki",
    "w3-lime",
    "w3-orange",
    "w3-deep-orange",
    "w3-pink",
    "w3-purple",
    "w3-deep-purple",
    "w3-red",
    "w3-sand",
    "w3-teal",
    "w3-yellow",
    "w3-pale-red",
    "w3-pale-green",
    "w3-pale-yellow",
    "w3-pale-blue",
]

i = 0
col = dict()


def w3_color(text):
    """Return stable color based on text."""
    global col
    global i
    if text not in col:
        col[text] = colors[i % len(colors)]
        i = i + 1
    return col[text]


def find_common_roles(specs):
    """Return roles that are common to all specs."""
    ret = set()
    for spec in specs:
        roles = spec.get("parameters", {}).get("roles")
        ret = ret.union(set(roles))
    for spec in specs:
        roles = spec.get("parameters", {}).get("roles")
        ret = ret.intersection(set(roles))
    return ret


def get_specs_by_role(specs):
    """Return dict of specs by role."""
    ret = collections.defaultdict(list)
    for spec in specs:
        for role in spec.get("parameters", {}).get("roles"):
            ret[role].append(spec)
    return ret


@app.route("/")
def index():
    """Specxplorer app page."""
    with open("test.json") as f:
        specs = json.load(f)["_items"]
    common_roles = find_common_roles(specs)
    print(common_roles)
    for spec in specs:
        spec["parameters"]["roles"] = [
            role
            for role in spec.get("parameters").get("roles", [])
            if role not in common_roles
        ]
    specs = sorted(specs, key=lambda d: (d["tag"], d["name"]))
    specs_by_role = get_specs_by_role(specs)
    return flask.render_template(
        "app.jinja2",
        specs=specs,
        w3_color=w3_color,
        common_roles=common_roles,
        specs_by_role=specs_by_role,
    )


@app.route("/spec/<name>")
def spec(name):
    """Specxplorer spec item page."""
    with open("test.json") as f:
        specs = json.load(f)["_items"]
    spec = [spec for spec in specs if spec.get("name", "") == name]
    if not spec:
        return flask.abort(404)
    spec = spec[0]

    htmlspec = highlight(
        yaml.dump(spec),
        lexer=lexers.YamlLexer(),
        formatter=formatters.HtmlFormatter(style="colorful"),
    )
    css = formatters.HtmlFormatter().get_style_defs()

    return flask.render_template(
        "spec.jinja2",
        css=css,
        spec=spec,
        htmlspec=htmlspec,
        json_dumps=json.dumps,
    )


def main():
    """Start flask server."""
    global wsr_url
    wsr_url = os.environ.get("SX_WSR_URL")
    if not wsr_url:
        print("Define the SX_WSR_URL environment variable as the")
        sys.exit()
    specs = requests.get(wsr_url).text
    with open("specs.json", "w") as f:
        f.write(specs)

    app.run(port=4328, debug=True)


if __name__ == "__main__":
    main()
