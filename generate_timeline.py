#!/usr/bin/python3
#
# Uyuni Logs Visualizer
#
# A tool to graphically visualize events from Uyuni logs and Salt events bus
#
# Author: Pablo Suárez Hernández <psuarezhernandez@suse.com>
#

import argparse
import datetime
import json
import logging
import os
import pprint
import re
import shutil
import tarfile
import tempfile

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
    metavar="FROM_DATETIME",
    action="store",
    dest="_from",
    type=str,
    help="Only events after this datetime. (Example: 2021-11-11T16:23:28.804535)",
)

parser.add_argument(
    "-u",
    "--until",
    metavar="FROM_DATETIME",
    action="store",
    dest="_until",
    type=str,
    help="Only events before this datetime. (Example: 2021-11-11T16:23:28.804535)",
)

parser.add_argument(
    "-p",
    "--logs-path",
    type=str,
    help="Path to logs files",
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

if bool(args.logs_path) == bool(args.supportconfig_path):
    log.error("ERROR: You must specify either a logs path or supportconfig path")
    exit(1)

templates_dir = os.path.join(os.path.dirname(__file__), "./templates")

template_loader = jinja2.FileSystemLoader(searchpath=templates_dir)
template_env = jinja2.Environment(loader=template_loader)

template = template_env.get_template("_output.jinja")

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

COLLECTORS_AND_FILES_MAPPING = {
    "salt_events": {
        "files": [
            "salt-events.txt",
            "salt-event.log",
            "var/log/rhn/salt-event.log",
            "spacewalk-debug/salt-logs/salt/salt-event.log",
        ],
        "group": 0,
    },
    "salt_master": {
        "files": [
            "master",
            "var/log/salt/master",
            "spacewalk-debug/salt-logs/salt/master",
        ],
        "group": 1,
    },
    "salt_api": {
        "files": ["api", "var/log/salt/api", "spacewalk-debug/salt-logs/salt/api"],
        "group": 2,
    },
    "java_web_ui": {
        "files": [
            "rhn_web_ui.log",
            "var/log/rhn/rhn_web_ui.log",
            "spacewalk-debug/rhn-logs/rhn/rhn_web_ui.log",
        ],
        "group": 3,
    },
}


print(" -----------------------")
print("| Uyuni Logs Visualizer |")
print(" ----------------------- ")
print()
print("  Options:")
if args._from:
    print("    * From datetime: {}".format(args._from))
if args._until:
    print("    * Until datetime: {}".format(args._until))
if args.logs_path:
    print("    * Path to logs: {}".format(args.logs_path))
if args.supportconfig_path:
    print("    * Path to supportconfig tarball: {}".format(args.supportconfig_path))

print()
print("  Collecting logs:")
temp_dirpath = None
if args.supportconfig_path and not os.path.isfile(args.supportconfig_path):
    log.error(
        "ERROR: Supportconfig tarball does not exist: {}".format(
            args.supportconfig_path
        )
    )
    exit(1)
elif args.supportconfig_path:
    temp_dirpath = tempfile.mkdtemp()
    if args.supportconfig_path.endswith("tar.gz"):
        mode = "r:gz"
    elif args.supportconfig_path.endswith("txz"):
        mode = "r:xz"
    elif args.supportconfig_path.endswith("tar.bz2"):
        mode = "r:bz2"
    else:
        log.error(
            "ERROR: Supportconfig tarball format is unknown: {}".format(
                args.supportconfig_path
            )
        )
        exit(1)
    tar = tarfile.open(args.supportconfig_path, mode)
    tar.extractall(temp_dirpath)
    tar.close()

logs_path = (
    args.logs_path
    if args.logs_path
    else os.path.join(temp_dirpath, os.listdir(temp_dirpath)[0])
)

# Start the actual execution
try:
    for collector in COLLECTORS_AND_FILES_MAPPING:
        try:
            event_file = next(
                f
                for f in COLLECTORS_AND_FILES_MAPPING[collector]["files"]
                if os.path.isfile(os.path.join(logs_path, f))
            )
            event_file_path = os.path.join(logs_path, event_file)
            template_data["groups"][COLLECTORS_AND_FILES_MAPPING[collector]["group"]][
                "events"
            ] = getattr(collectors, "from_{}".format(collector))(
                event_file_path, args._from, args._until
            )
        except StopIteration:
            log.error("  - Cannot find logs for '{}'\n".format(collector))
    template_data["groups"][4]["events"] = []
    template_data["groups"][5]["events"] = []
    template_data["groups"][6]["events"] = []
except OSError as exc:
    log.error("Oops! There was an error when collecting events:")
    log.error(exc)
    exit(1)

# Render template and write output file
rendered_output = template.render(**template_data)
with open(args.output, "w") as f:
    f.write(rendered_output)

print("  Summary:")
print("    * {} events were collected.".format(collectors._stats["event_count"]))

if collectors._stats["first_event"] and collectors._stats["last_event"]:
    print(
        "    * First event at: {}".format(collectors._stats["first_event"].isoformat())
    )
    print("    * Last event at: {}".format(collectors._stats["last_event"].isoformat()))

print()
print("  Results:")
print("    * Results HTML file: {}".format(args.output))
print()
print(" -----------")
print("| Finished! |")
print(" -----------")
