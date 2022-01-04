TEMPLATE_DATA = {
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
            "plugin-saltlogfiles.txt",
        ],
        "group": 1,
    },
    "salt_api": {
        "files": [
            "api",
            "var/log/salt/api",
            "spacewalk-debug/salt-logs/salt/api",
            "plugin-saltlogfiles.txt",
        ],
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

CLI_FANCY_TITLE = """
   __  __                  _    __                        _    ___                  ___
  / / / /_  ____  ______  (_)  / /   ____  ____ ______   | |  / (_)______  ______ _/ (_)___  ___  _____
 / / / / / / / / / / __ \/ /  / /   / __ \/ __ `/ ___/   | | / / / ___/ / / / __ `/ / /_  / / _ \/ ___/
/ /_/ / /_/ / /_/ / / / / /  / /___/ /_/ / /_/ (__  )    | |/ / (__  ) /_/ / /_/ / / / / /_/  __/ /
\____/\__, /\__,_/_/ /_/_/  /_____/\____/\__, /____/     |___/_/____/\__,_/\__,_/_/_/ /___/\___/_/
     /____/                             /____/
"""

CLI_FANCY_DONE = """
    ____                      __
   / __ \____  ____  ___     / /
  / / / / __ \/ __ \/ _ \   / /
 / /_/ / /_/ / / / /  __/  /_/
/_____/\____/_/ /_/\___/  (_)
"""
