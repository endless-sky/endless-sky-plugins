#!/usr/bin/env python3

# Checks if `url` and `iconUrl` (if it exists) are valid
# Usage: ./check_urls.py manifests/
# Usage: ./check_urls.py myPlugin.yaml
import os
import yaml
import sys
from urllib.error import HTTPError
from urllib.request import urlopen, Request


class PluginChecker:

    failed_urls = []

    def check_url(self, url: str) -> bool:
        try:
            conn = urlopen(Request(url, method="HEAD"))
            status = f"  OK {conn.status}\t{url}"
            ok = True
        except HTTPError as e:
            status = f"  ERROR {e.code}\t{url}"
            self.failed_urls.append(status)
            ok = False

        print(status)
        return ok

    def check_plugin(self, manifest: str) -> bool:
        icon_url = manifest.get("iconUrl")

        url_ok = self.check_url(manifest["url"])

        if icon_url:
            icon_url_ok = self.check_url(icon_url)

        return url_ok and (icon_url_ok if icon_url else True)

    def check_plugin_file(self, file: str) -> bool:
        print("Checking " + file)
        with open(file, "r") as f:
            manifest = yaml.load(f, Loader=yaml.FullLoader)
        self.check_plugin(manifest)


target = sys.argv[1]
files = []
if os.path.isdir(target):
    for filename in os.listdir(target):
        files.append(os.path.join(target, filename))
else:
    files = [target]

checker = PluginChecker()
for file in files:
    checker.check_plugin_file(file)

if checker.failed_urls:
    print("\nFailed URLs:")
    for status in checker.failed_urls:
        print(status)
    exit(1)
