#!/usr/bin/python3

# Checks all URLs it can find in plugins.yaml
# Usage: ./check_urls.py plugins.yaml

import yaml
import sys
from urllib.parse import urlparse
from urllib.error import HTTPError
from urllib.request import urlopen

file = sys.argv[1]
with open(file, "r") as f:
    plugins = yaml.load(f, Loader=yaml.FullLoader)

valid = True
for plugin in plugins:
    for value in plugin.values():
        url = urlparse(value)
        # urlparse will happily parse any string as relative URL,
        # but only those with `netloc` are absolute, valid URLs.
        if url.netloc:
            print("Testing " + value)
            try:
                conn = urlopen(value)
            except HTTPError as e:
                print("%s: %s" % (e.code, e.reason))
                valid = False

if not valid:
    exit(1)
