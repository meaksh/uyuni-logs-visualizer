import datetime
import json
import pprint
import re

EXCLUDED_SALT_EVENTS = "minion_event"


def from_salt_events(path, from_date, until_date):
    with open(path) as f:
        ret = []
        in_data = f.readlines()
        for i, line in enumerate(in_data):
            if re.match(r"^.*\t{", line):
                # Begin tag and json
                tag, content = line.split("\t")
                j = i
                while j < len(in_data) - 1 and in_data[j] != "}\n":
                    content += in_data[j + 1]
                    j += 1
                try:
                    content = json.loads(content)
                except Exception as exc:
                    print("Error parsing JSON -> {}".format(content))
                    print(exc)
                    continue

                # Exclude events older than given datetime
                if from_date and datetime.datetime.fromisoformat(
                    content["_stamp"]
                ) < datetime.datetime.fromisoformat(from_date):
                    continue

                # Exclude events newer than given datetime
                if until_date and datetime.datetime.fromisoformat(
                    content["_stamp"]
                ) > datetime.datetime.fromisoformat(until_date):
                    continue

                new_item = {
                    "content": tag,
                    "color": "green",
                    "raw": pprint.pformat(content),
                    "timestamp": content["_stamp"],
                }

                if tag.startswith("salt/batch"):
                    new_item["type"] = "batch"
                elif tag.startswith("salt/job"):
                    new_item["type"] = "job"
                elif re.match(r"^/salt/job/[0-9]+/ret/.*", tag):
                    new_item["type"] = "job_return"
                elif tag.startswith("salt/auth"):
                    new_item["type"] = "auth"
                elif tag.startswith("salt/minion"):
                    new_item["type"] = "minion_event"
                elif tag.startswith("salt/engines/"):
                    new_item["type"] = "minion_event"
                elif tag.startswith("minion/refresh"):
                    new_item["type"] = "minion_refresh"

                if new_item.get("type", "") not in EXCLUDED_SALT_EVENTS:
                    ret.append(new_item)
        return ret


def from_java_web_ui(path, from_date, until_date):
    with open(path) as f:
        in_data = f.readlines()
        ret = []
        for i, line in enumerate(in_data):
            if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3} .*", line):
                timestamp, thread, level, content = re.match(
                    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}) (\[.*\]) (\w+) (.*)",
                    line,
                ).groups()
                if level != "ERROR":
                    continue

                j = i
                while j < len(in_data) - 1 and not re.match(
                    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3} .*", in_data[j + 1]
                ):
                    content += in_data[j + 1]
                    j += 1

                datetime_obj = datetime.datetime.strptime(
                    timestamp, "%Y-%m-%d %H:%M:%S,%f"
                )

                # TODO: Adjust timezone
                datetime_obj = datetime_obj - datetime.timedelta(hours=1)

                # Exclude events older than given datetime
                if from_date and datetime_obj < datetime.datetime.fromisoformat(
                    from_date
                ):
                    continue

                # Exclude events rewer than given datetime
                if until_date and datetime_obj > datetime.datetime.fromisoformat(
                    until_date
                ):
                    continue

                if (
                    "LoginController - LOCAL AUTH FAILURE:" in content
                    or "common.DownloadFile - " in content
                ):
                    continue

                new_item = {
                    "content": level,
                    "raw": "{} - {}".format(level, content),
                    "color": "orange",
                    "timestamp": datetime_obj,
                }

                ret.append(new_item)
        return ret


def from_salt_api(path, from_date, until_date):
    with open(path) as f:
        in_data = f.readlines()
        ret = []
        for i, line in enumerate(in_data):
            if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3} .*", line):
                timestamp, component, level, content = re.match(
                    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}) (\[.*\])(\[.*\])(\[.*\].*)",
                    line,
                ).groups()
                if "ERROR" in level:
                    continue

                j = i
                while j < len(in_data) - 1 and not re.match(
                    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3} .*", in_data[j + 1]
                ):
                    content += in_data[j + 1]
                    j += 1

                datetime_obj = datetime.datetime.strptime(
                    timestamp, "%Y-%m-%d %H:%M:%S,%f"
                )

                # Exclude events older than given datetime
                if from_date and datetime_obj < datetime.datetime.fromisoformat(
                    from_date
                ):
                    continue

                # Exclude events rewer than given datetime
                if until_date and datetime_obj > datetime.datetime.fromisoformat(
                    until_date
                ):
                    continue

                new_item = {
                    "content": level,
                    "raw": "{} - {}".format(component, content),
                    "color": "red",
                    "timestamp": timestamp,
                }

                ret.append(new_item)
        return ret


def from_salt_master(path, from_date, until_date):
    with open(path) as f:
        in_data = f.readlines()
        ret = []
        for i, line in enumerate(in_data):
            if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3} .*", line):
                timestamp, component, level, content = re.match(
                    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}) (\[.*\])(\[.*\])(\[.*\].*)",
                    line,
                ).groups()
                if "ERROR" in level:
                    continue

                j = i
                while j < len(in_data) - 1 and not re.match(
                    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3} .*", in_data[j + 1]
                ):
                    content += in_data[j + 1]
                    j += 1

                datetime_obj = datetime.datetime.strptime(
                    timestamp, "%Y-%m-%d %H:%M:%S,%f"
                )

                # Exclude events older than given datetime
                if from_date and datetime_obj < datetime.datetime.fromisoformat(
                    from_date
                ):
                    continue

                # Exclude events rewer than given datetime
                if until_date and datetime_obj > datetime.datetime.fromisoformat(
                    until_date
                ):
                    continue

                new_item = {
                    "content": level,
                    "raw": "{} - {}".format(component, content),
                    "color": "blue",
                    "timestamp": timestamp,
                }

                ret.append(new_item)
        return ret
