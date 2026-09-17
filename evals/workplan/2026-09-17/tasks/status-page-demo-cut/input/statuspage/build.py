"""Read the data files and write the page."""
import json
import os

from . import render

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def build(out_path):
    services = load("services.json")
    incidents = load("incidents.json")
    uptime = load("uptime.json")
    markup = render.page(services, incidents, uptime)
    directory = os.path.dirname(os.path.abspath(out_path))
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(markup)
    return out_path
