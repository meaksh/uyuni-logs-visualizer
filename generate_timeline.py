import jinja2
import pprint
import datetime
import os
import re
import json

templates_dir = os.path.join(os.path.dirname(__file__), './templates')

template_loader = jinja2.FileSystemLoader(searchpath=templates_dir)
template_env = jinja2.Environment(loader=template_loader)

template = template_env.get_template("_index.jinja")

event_counter = 0

data_dict = {
    "title": "Uyuni Logs visualizer",
    "body": "This is the body of the page",
    "groups": [
        {"id" : 0, "name": "Salt Event Bus"},
        {"id" : 1, "name": "Salt Master"},
        {"id" : 2, "name": "Salt API"},
        {"id" : 3, "name": "Java Web UI"},
        {"id" : 4, "name": "Java Taskomatic"},
        {"id" : 5, "name": "PostgreSQL"},
    ],
}

EXCLUDED_SALT_EVENTS = "minion_event"

##################################################################
### Salt Event Bus

data_dict["groups"][0]["events"] = []

with open("salt-events.txt") as f:
    in_data = f.readlines()
    for i, line in enumerate(in_data):
        if re.match("^.*\t{", line):
            # Begin tag and json
            tag, content = line.split("\t")
            j = i
            while j < len(in_data)-1 and in_data[j] != "}\n":
                content += in_data[j+1]
                j += 1
            try:
                content = json.loads(content) 
            except Exception as exc:
                print("Error parsing JSON -> {}".format(content))
                print(exc)
                continue

            new_item = {
                    "id": event_counter,
                    "content": tag,
                    "color": "green",
                    "raw": pprint.pformat(content),
                    "timestamp": content["_stamp"],
            }

            if tag.startswith("salt/batch"):
                new_item["type"] = "batch"
            elif tag.startswith("salt/job"):
                new_item["type"] = "job"
            elif re.match("^/salt/job/[0-9]+/ret/.*", tag):
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
                data_dict["groups"][0]["events"].append(new_item)
                event_counter += 1

##################################################################

data_dict["groups"][3]["events"] = []

with open("rhn_web_ui.log") as f:
    in_data = f.readlines()

    for i, line in enumerate(in_data):
      if re.match("^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3} .*", line):
           timestamp, thread, level, content = re.match("^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}) (\[.*\]) (\w+) (.*)", line).groups()
           if level != "ERROR":
               continue

           j = i
           while j < len(in_data)-1 and not re.match("^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3} .*", in_data[j+1]):
               content += in_data[j+1]
               j += 1

           datetime_obj = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S,%f")

           # TODO: Adjust timezone
           datetime_obj = datetime_obj - datetime.timedelta(hours=1)

#           # Exclude events OLDER than first Salt event
#           if datetime_obj < datetime.datetime.fromisoformat(data_dict["groups"][0]["events"][0]["timestamp"]):
#               continue

           if "LoginController - LOCAL AUTH FAILURE:" in content or "common.DownloadFile - " in content:
               continue

           new_item = {
                   "id": event_counter,
                   "content": level,
                   "raw": "{} - {}".format(level, content),
                    "color": "orange",
                   "timestamp": timestamp,
           }

           data_dict["groups"][3]["events"].append(new_item)
           event_counter += 1

##################################################################

data_dict["groups"][2]["events"] = []

with open("api") as f:
    in_data = f.readlines()

    for i, line in enumerate(in_data):
      if re.match("^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3} .*", line):
           timestamp, component, level, content = re.match("^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}) (\[.*\])(\[.*\])(\[.*\].*)", line).groups()
           if "ERROR" in level:
               continue

           j = i
           while j < len(in_data)-1 and not re.match("^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3} .*", in_data[j+1]):
               content += in_data[j+1]
               j += 1

           datetime_obj = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S,%f")

           new_item = {
                   "id": event_counter,
                   "content": level,
                   "raw": "{} - {}".format(component, content),
                    "color": "red",
                   "timestamp": timestamp,
           }

           data_dict["groups"][2]["events"].append(new_item)
           event_counter += 1

##################################################################

data_dict["groups"][1]["events"] = []

with open("master") as f:
    in_data = f.readlines()

    for i, line in enumerate(in_data):
      if re.match("^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3} .*", line):
           timestamp, component, level, content = re.match("^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}) (\[.*\])(\[.*\])(\[.*\].*)", line).groups()
           if "ERROR" in level:
               continue

           j = i
           while j < len(in_data)-1 and not re.match("^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3} .*", in_data[j+1]):
               content += in_data[j+1]
               j += 1

           datetime_obj = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S,%f")

           new_item = {
                   "id": event_counter,
                   "content": level,
                   "raw": "{} - {}".format(component, content),
                    "color": "blue",
                   "timestamp": timestamp,
           }

           data_dict["groups"][1]["events"].append(new_item)
           event_counter += 1

output = template.render(**data_dict)
print(output)
