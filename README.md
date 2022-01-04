# uyuni-logs-visualizer [![pre-commit](https://github.com/meaksh/uyuni-logs-visualizer/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/meaksh/uyuni-logs-visualizer/actions/workflows/pre-commit.yml)
A tool to graphically visualize events from Uyuni logs and Salt events bus. The tool generates a HTML output where you can navigate the collected events using your web browser.

When running this tool, you provide a path where the different logs files are stored, i.a. "rhn_web_ui.log", "master" or "salt-events.txt", or you can pass the path to your "supportconfig" tarball, then the tool will temporary unpack the supportconfig and collect the logs file from it.

### Requirements:
- Python3
- Jinja2

### How to setup:

- Install `python3-jinja2` package or alternatively get `jinja2` python library using pip:

```console
# pip install -r requirements.txt
```

### How to run it:

```console
# python3 uyuni-logs-visualizer -h
usage: uyuni-logs-visualizer [-h] [-o OUTPUT_FILE]
                            [-f FROM_DATETIME] [-u UNTIL_DATETIME]
                            [-p LOGS_PATH] [-s SUPPORTCONFIG_PATH]

Generate a HTML view of Uyuni logs.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        generated output HTML file (default: output.html)
  -f FROM_DATETIME, --from FROM_DATETIME
                        Only events after this datetime. (Example: 2021-11-11T16:23:28.804535)
  -u UNTIL_DATETIME, --until UNTIL_DATETIME
                        Only events before this datetime. (Example: 2021-11-11T16:23:28.804535)
  -p LOGS_PATH, --logs-path LOGS_PATH
                        Path to logs files
  -s SUPPORTCONFIG_PATH, --supportconfig-path SUPPORTCONFIG_PATH
                        Path to supportconfig tarball
```

### Example execution:

```console
# python3 uyuni-logs-visualizer -s /tmp/example_supportconfig.txz -f 2022-01-03T14:01:05.093000 -u 2022-01-04T10:01:05.093000

   __  __                  _    __                        _    ___                  ___
  / / / /_  ____  ______  (_)  / /   ____  ____ ______   | |  / (_)______  ______ _/ (_)___  ___  _____
 / / / / / / / / / / __ \/ /  / /   / __ \/ __ `/ ___/   | | / / / ___/ / / / __ `/ / /_  / / _ \/ ___/
/ /_/ / /_/ / /_/ / / / / /  / /___/ /_/ / /_/ (__  )    | |/ / (__  ) /_/ / /_/ / / / / /_/  __/ /
\____/\__, /\__,_/_/ /_/_/  /_____/\____/\__, /____/     |___/_/____/\__,_/\__,_/_/_/ /___/\___/_/
     /____/                             /____/


  Options:
    * From datetime: 2022-01-03T14:01:05.093000
    * Until datetime: 2022-01-04T10:01:05.093000
    * Path to supportconfig tarball: /tmp/scc_suma-42-srv_220104_1049.txz

  Extracting supportconfig at: /tmp/tmpbf9ne78p

  Collecting logs:
    * WARN: Couldn't find any logs files for Salt Event Bus:
      - salt-events.txt not found
      - salt-event.log not found
      - var/log/rhn/salt-event.log not found
      - spacewalk-debug/salt-logs/salt/salt-event.log not found

    * Found Salt Master logs file at: /tmp/tmpbf9ne78p/scc_suma-42-srv_220104_1049/spacewalk-debug/salt-logs/salt/master
    * Found Salt API logs file at: /tmp/tmpbf9ne78p/scc_suma-42-srv_220104_1049/spacewalk-debug/salt-logs/salt/api
    * Found Java Web UI logs file at: /tmp/tmpbf9ne78p/scc_suma-42-srv_220104_1049/spacewalk-debug/rhn-logs/rhn/rhn_web_ui.log

  Cleanup:
    * Temporary files removed: /tmp/tmpbf9ne78p

  Summary:
    * 1541 events were collected.
    * First event at: 2022-01-03T14:01:59.479000
    * Last event at: 2022-01-04T10:01:05.093000

  Results:
    * Results HTML file: output.html

    ____                      __
   / __ \____  ____  ___     / /
  / / / / __ \/ __ \/ _ \   / /
 / /_/ / /_/ / / / /  __/  /_/
/_____/\____/_/ /_/\___/  (_)

```

Generated HTML:
![image](https://user-images.githubusercontent.com/7229203/141479052-9fd712eb-45aa-4816-a0a1-7b599ec4a81f.png)


### Authors:
- Pablo Suárez Hernández - <psuarezhernandez@suse.de>
