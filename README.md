# uyuni-logs-visualizer
A tool to graphically visualize events from Uyuni logs and Salt events bus

```console
usage: run.py [-h] [-o OUTPUT_FILE]
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
                        Path to the unpacked supportconfig
```

### Example of generated HTML:
![image](https://user-images.githubusercontent.com/7229203/141479052-9fd712eb-45aa-4816-a0a1-7b599ec4a81f.png)


### Authors:
- Pablo Suárez Hernández - <psuarezhernandez@suse.de>
