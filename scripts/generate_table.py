#!/usr/bin/env python3

# Generates a markdown file containing a table of all plug-ins.
# Usage: ./generate_table.py generated/plugins.yaml PLUGINS.md

import yaml
import sys


with open(sys.argv[1], "r") as f:
    plugins = yaml.load(f, Loader=yaml.FullLoader)
    plugins.sort(key=lambda p: p["name"])

buffer = """
| | Name | Author | Description |
|-|------|--------|-------------|"""

plugin_template = """
| ![Icon]({iconUrl}) | [{name}]({url}) | {authors} | {shortDescription} |"""

for plugin in plugins:
    plugin["shortDescription"] = (
        plugin["shortDescription"].replace("\n", " ").replace("\r", "").strip()
    )
    if "iconUrl" not in plugin:
        plugin[
            "iconUrl"
        ] = "https://raw.githubusercontent.com/endless-sky/endless-sky/master/images/outfit/unknown.png"
    buffer += plugin_template.format(**plugin)

with open(sys.argv[2], "w") as f:
    f.write(buffer)
