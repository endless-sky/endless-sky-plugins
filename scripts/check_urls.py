#!/usr/bin/env python3

# Checks if `url` and `iconUrl` (if it exists) are valid
# Usage: ./check_urls.py manifests/
# Usage: ./check_urls.py myPlugin.yaml
import os
import yaml
import sys
from urllib.parse import urlparse
from urllib.error import HTTPError
from urllib.request import urlopen, Request


def check_url(url):
    try:
        conn = urlopen(Request(url, method="HEAD"))
        status = f"  OK {conn.status}\t{url}"
    except HTTPError as e:
        status = f"  ERROR {e.code}\t{url}"
        failed_urls.append(status)
    
    print(status)

def check_plugin(file):
    print("Checking " + file)
    with open(file, "r") as f:
        manifest = yaml.load(f, Loader=yaml.FullLoader)

    check_url(manifest["url"])
    if manifest.get("iconUrl"):
        check_url(manifest["iconUrl"])




target = sys.argv[1]
files = []
if os.path.isdir(target):
    for filename in os.listdir(target):
        files.append(os.path.join(target, filename))
else:
    files = [target]

failed_urls = []
for file in files:
    check_plugin(file)

if failed_urls:
    print("\nFailed URLs:")
    for status in failed_urls:
        print(status)
    exit(1)
