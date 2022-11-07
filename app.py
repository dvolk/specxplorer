"""Specxplorer entry point.

Specxplorer is ...
"""

import flask
import json


def index():
    """Specxplorer app page."""
    with open("test.json") as f:
        specs = json.load(f)["_items"]
    return flask.render_template("app.jinja2", specs=specs)


def main():
    """Start flask server."""
    flask.run(port=4328)


if __name__ == "__main__":
    main()
