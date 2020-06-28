#!/usr/bin/python3

# Checks constructed download URLs and all other URLs it can find
# Usage: ./check_urls.py plugins.yaml

import yaml
import sys
from urllib.parse import urlparse
from urllib.error import HTTPError
from urllib.request import urlopen, Request


def test(url):
    print("Testing " + url)
    try:
        conn = urlopen(Request(url, method="HEAD"))
        return True
    except HTTPError as e:
        print("%s: %s" % (e.code, e.reason))
        return False


file = sys.argv[1]
with open(file, "r") as f:
    plugins = yaml.load(f, Loader=yaml.FullLoader)


valid = True
for plugin in plugins:

    # Test download link
    download_link = "%s/archive/%s.zip" % (plugin["url"], plugin["version"])
    if not test(download_link):
        valid = False

    # Find and test any other links
    for value in plugin.values():
        url = urlparse(value)
        # urlparse will happily parse any string as relative URL,
        # but only those with `netloc` are absolute, VALID URLs.
        if url.netloc:
            if not test(value):
                valid = False

if not valid:
    exit(1)
