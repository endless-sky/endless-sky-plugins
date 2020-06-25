#!/usr/bin/python3

# Generates a markdown file containing a table of all plug-ins.
# Usage: ./generate_table.py plugins.yaml PLUGINS.md

import yaml
import sys


with open(sys.argv[1], "r") as f:
    plugins = yaml.load(f, Loader=yaml.FullLoader)

buffer = \
    """
| | Name | Author | Description |
|-|------|--------|-------------|"""

plugin_template = """
| ![Icon]({iconUrl}) | [{name}]({url}) | {author} | {description} |"""

for plugin in plugins:
    plugin["description"] = plugin["description"] \
        .replace("\n", " ") \
        .replace("\r", "") \
        .strip()
    buffer += plugin_template.format(**plugin)

with open(sys.argv[2], "w") as f:
    f.write(buffer)
