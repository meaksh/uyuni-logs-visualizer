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
from utils.constants import COLLECTORS_AND_FILES_MAPPING, TEMPLATE_DATA

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
    help="Path to supportconfig tarball",
)

parser.add_argument(
    "-sk",
    "--skip-cleanup",
    type=str,
    help="Skip cleanup of temporary files",
)

args = parser.parse_args()


class UyuniLogsVisualizer:
    def __init__(self, args):
        self.args = self.validate_args(args)

        templates_dir = os.path.join(os.path.dirname(__file__), "./templates")
        template_loader = jinja2.FileSystemLoader(searchpath=templates_dir)
        template_env = jinja2.Environment(loader=template_loader)
        self.template = template_env.get_template("_output.jinja")

    def start(self):
        self.__config_summary()
        self.__setup_logs_path()
        self.__collect()
        self.__generate_output()
        self.__cleanup()
        self.__output_summary()

    def validate_args(self, args):
        if args._from:
            try:
                datetime.datetime.fromisoformat(args._from)
            except ValueError:
                log.error("ERROR: '{}' is not a valid datetime".format(args._from))
                exit(1)
        if bool(args.logs_path) == bool(args.supportconfig_path):
            log.error(
                "ERROR: You must specify either a logs path or supportconfig path"
            )
            exit(1)
        return args

    def __config_summary(self):
        print(" -----------------------")
        print("| Uyuni Logs Visualizer |")
        print(" ----------------------- ")
        print()
        print("  Options:")
        if self.args._from:
            print("    * From datetime: {}".format(self.args._from))
        if self.args._until:
            print("    * Until datetime: {}".format(self.args._until))
        if self.args.logs_path:
            print("    * Path to logs: {}".format(self.args.logs_path))
        if self.args.supportconfig_path:
            print(
                "    * Path to supportconfig tarball: {}".format(
                    self.args.supportconfig_path
                )
            )
        print()

    def __setup_logs_path(self):
        self.temp_dirpath = None
        if self.args.supportconfig_path and not os.path.isfile(
            self.args.supportconfig_path
        ):
            log.error(
                "ERROR: Supportconfig tarball does not exist: {}".format(
                    self.args.supportconfig_path
                )
            )
            exit(1)
        elif self.args.supportconfig_path:
            self.temp_dirpath = tempfile.mkdtemp()
            print("  Extracting supportconfig at: {}".format(self.temp_dirpath))
            print()
            if self.args.supportconfig_path.endswith("tar.gz"):
                mode = "r:gz"
            elif self.args.supportconfig_path.endswith("txz"):
                mode = "r:xz"
            elif self.args.supportconfig_path.endswith("tar.bz2"):
                mode = "r:bz2"
            else:
                log.error(
                    "ERROR: Supportconfig tarball format is unknown: {}".format(
                        self.args.supportconfig_path
                    )
                )
                exit(1)
            tar = tarfile.open(self.args.supportconfig_path, mode)
            tar.extractall(self.temp_dirpath)
            tar.close()

        self.logs_path = (
            self.args.logs_path
            if self.args.logs_path
            else os.path.join(self.temp_dirpath, os.listdir(self.temp_dirpath)[0])
        )

    def __collect(self):
        # Start the actual execution
        print("  Collecting logs:")
        try:
            for collector in COLLECTORS_AND_FILES_MAPPING:
                try:
                    event_file = next(
                        f
                        for f in COLLECTORS_AND_FILES_MAPPING[collector]["files"]
                        if os.path.isfile(os.path.join(self.logs_path, f))
                    )
                    event_file_path = os.path.join(self.logs_path, event_file)
                    TEMPLATE_DATA["groups"][
                        COLLECTORS_AND_FILES_MAPPING[collector]["group"]
                    ]["events"] = getattr(collectors, "from_{}".format(collector))(
                        event_file_path, self.args._from, self.args._until
                    )
                    print(
                        "    * Found {} logs file at: {}".format(
                            [
                                x["name"]
                                for x in TEMPLATE_DATA["groups"]
                                if x["id"]
                                == COLLECTORS_AND_FILES_MAPPING[collector]["group"]
                            ][0],
                            event_file_path,
                        )
                    )
                except StopIteration:
                    log.warning(
                        "    * WARN: Couldn't find any logs files for {}:".format(
                            [
                                x["name"]
                                for x in TEMPLATE_DATA["groups"]
                                if x["id"]
                                == COLLECTORS_AND_FILES_MAPPING[collector]["group"]
                            ][0]
                        )
                    )
                    for file in COLLECTORS_AND_FILES_MAPPING[collector]["files"]:
                        print("      - {} not found".format(file))
                    print()
            TEMPLATE_DATA["groups"][4]["events"] = []
            TEMPLATE_DATA["groups"][5]["events"] = []
            TEMPLATE_DATA["groups"][6]["events"] = []
        except OSError as exc:
            log.error("Oops! There was an error when collecting events:")
            log.error(exc)
            exit(1)
        print()

    def __generate_output(self):
        # Render template and write output file
        rendered_output = self.template.render(**TEMPLATE_DATA)
        with open(self.args.output, "w") as f:
            f.write(rendered_output)

    def __cleanup(self):
        # Clean up temporary files
        if (
            not self.args.skip_cleanup
            and self.args.supportconfig_path
            and self.temp_dirpath
        ):
            print("  Cleanup:")
            try:
                shutil.rmtree(self.temp_dirpath)
                print("    * Temporary files removed: {}".format(self.temp_dirpath))
            except Exception as exc:
                log.error("ERROR: Something unexpected happending during cleanup")
                log.error(exc)
                exit(1)
            print()

    def __output_summary(self):
        print("  Summary:")
        print(
            "    * {} events were collected.".format(collectors._stats["event_count"])
        )
        if collectors._stats["first_event"] and collectors._stats["last_event"]:
            print(
                "    * First event at: {}".format(
                    collectors._stats["first_event"].isoformat()
                )
            )
            print(
                "    * Last event at: {}".format(
                    collectors._stats["last_event"].isoformat()
                )
            )
        print()
        print("  Results:")
        print("    * Results HTML file: {}".format(self.args.output))
        print()
        print(" ---------------------")
        print("| Execution finished! |")
        print(" ---------------------")


UyuniLogsVisualizer(args).start()
