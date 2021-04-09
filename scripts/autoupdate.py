#!/usr/bin/python3

# Checks wether a new plug-in version exists, if yes updates the manifest according to `autoupdate`.
# Usage:
# $ python3 autoupdate.py myPlugin.yaml # update this specific file
# $ python3 autoupdate.py myPluginFolder/ # update every manifest in this folder

import yaml
import sys
import os


def get_latest_version(au_type, au_url, au_branch):
    if au_type == "commit":
        return "master"  # TODO
    else:
        raise NotImplementedError("Unknown autoupdate type '%s'" % au_type)


def update(file):
    print("Running autoupdate for " + file)
    with open(file, "r") as f:
        manifest = yaml.load(f, Loader=yaml.FullLoader)

    au = manifest["autoupdate"]
    au_type = au["type"]
    au_url = au.get("update_url", manifest["homepage"])
    # TODO: Repos can have different default branches, ex. "main", "development"
    au_branch = au.get("branch", "master")
    update_kvs = {}
    for k, v in au.items():
        if k not in ["type", "update_url", "branch"]:
            update_kvs[k] = v

    latest_version = get_latest_version(au_type, au_url, au_branch)

    print("Updating manifest with version '%s'" % latest_version)
    manifest["version"] = latest_version
    for key, value in update_kvs.items():
        value = value.replace("$version", latest_version)
        manifest[key] = value

    print("Saving manifest")
    with open(file, "w") as f:
        yaml.dump(manifest, f, sort_keys=False)


target = sys.argv[1]
files = []
if os.path.isdir(target):
    for filename in os.listdir(target):
        files.append(os.path.join(target, filename))
else:
    files = [target]

for file in files:
    update(file)
