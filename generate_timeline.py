import argparse
import datetime
import json
import os
import pprint
import re

import jinja2

from utils import collectors

parser = argparse.ArgumentParser(description="Generate a HTML view of Uyuni logs.")
parser.add_argument(
    "-o",
    "--output",
    metavar="OUTPUT_FILE",
    action="store",
    type=str,
    default="output.html",
    help="generated output HTML file (default: output.html)",
)

parser.add_argument(
    "-f",
    "--from",
    metavar="datetime",
    action="store",
    dest="_from",
    type=str,
    help="Only events after this datetime. (Example: 2021-11-11T16:23:28.804535)",
)

parser.add_argument(
    "-u",
    "--until",
    metavar="datetime",
    action="store",
    dest="_until",
    type=str,
    help="Only events before this datetime. (Example: 2021-11-11T16:23:28.804535)",
)

args = parser.parse_args()

if args._from:
    try:
        datetime.datetime.fromisoformat(args._from)
    except ValueError:
        print("ERROR: '{}' is not a valid datetime".format(args._from))
        exit(1)

templates_dir = os.path.join(os.path.dirname(__file__), "./templates")

template_loader = jinja2.FileSystemLoader(searchpath=templates_dir)
template_env = jinja2.Environment(loader=template_loader)

template = template_env.get_template("_index.jinja")

event_counter = 0

data_dict = {
    "title": "Uyuni Logs Visualizer",
    "body": "Hacked during DCM workshop 2021 at SUSE",
    "groups": [
        {"id": 0, "name": "Salt Event Bus"},
        {"id": 1, "name": "Salt Master"},
        {"id": 2, "name": "Salt API"},
        {"id": 3, "name": "Java Web UI"},
        {"id": 4, "name": "Java Taskomatic"},
        {"id": 5, "name": "PostgreSQL"},
        {"id": 6, "name": "Test group"},
    ],
}

try:
    data_dict["groups"][0]["events"] = collectors.from_salt_events(
        "salt-events.txt", args._from, args._until
    )
    data_dict["groups"][1]["events"] = collectors.from_salt_master(
        "master", args._from, args._until
    )
    data_dict["groups"][2]["events"] = collectors.from_salt_api(
        "api", args._from, args._until
    )
    data_dict["groups"][3]["events"] = collectors.from_java_web_ui(
        "rhn_web_ui.log", args._from, args._until
    )
    data_dict["groups"][4]["events"] = []
    data_dict["groups"][5]["events"] = []
    data_dict["groups"][6]["events"] = []
except OSError as exc:
    print("Oops, there was an error when collecting events!")
    print(exc)

# Assign ID to all collected events
event_counter = 0
for group in data_dict["groups"]:
    for ev in group["events"]:
        ev["id"] = event_counter
        event_counter += 1

print("Collected {} events".format(event_counter))

output = template.render(**data_dict)

with open(args.output, "w") as f:
    f.write(output)
