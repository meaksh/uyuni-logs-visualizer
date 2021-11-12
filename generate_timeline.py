import argparse
import datetime
import json
import logging
import os
import pprint
import re

import jinja2

from utils import collectors

log = logging.getLogger(__name__)

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

parser.add_argument(
    "-s",
    "--supportconfig-path",
    type=str,
    help="Path to the unpacked supportconfig",
)

args = parser.parse_args()

if args._from:
    try:
        datetime.datetime.fromisoformat(args._from)
    except ValueError:
        log.error("ERROR: '{}' is not a valid datetime".format(args._from))
        exit(1)

templates_dir = os.path.join(os.path.dirname(__file__), "./templates")

template_loader = jinja2.FileSystemLoader(searchpath=templates_dir)
template_env = jinja2.Environment(loader=template_loader)

template = template_env.get_template("_index.jinja")

event_counter = 0

template_data = {
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
    template_data["groups"][0]["events"] = collectors.from_salt_events(
        "salt-events.txt", args._from, args._until
    )
    template_data["groups"][1]["events"] = collectors.from_salt_master(
        "master", args._from, args._until
    )
    template_data["groups"][2]["events"] = collectors.from_salt_api(
        "api", args._from, args._until
    )
    template_data["groups"][3]["events"] = collectors.from_java_web_ui(
        "rhn_web_ui.log", args._from, args._until
    )
    template_data["groups"][4]["events"] = []
    template_data["groups"][5]["events"] = []
    template_data["groups"][6]["events"] = []
except OSError as exc:
    log.error("Oops! There was an error when collecting events:")
    log.error(exc)
    exit(1)

# Assign ID to all collected events
event_counter = 0
for group in template_data["groups"]:
    for ev in group["events"]:
        ev["id"] = event_counter
        event_counter += 1

# Render template and write output file
rendered_output = template.render(**template_data)
with open(args.output, "w") as f:
    f.write(rendered_output)

print("------------------------------------------------")
print("------------- Uyuni Log Visualizer -------------")
print("------------------------------------------------")
print()
if args._from:
    print("  * From datetime: {}".format(args._from))
if args._until:
    print("  * Until datetime: {}".format(args._until))
if args.supportconfig_path:
    print("  * Supportconfig path: {}".format(args.supportconfig_path))
print("  * {} events were collected.".format(event_counter))
print()
print("  * Results HTML file: {}".format(args.output))
print()
print("------------------------------------------------")
