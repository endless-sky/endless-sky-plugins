#!/usr/bin/env python3

# Check whether a new plug-in version exists. When one is found, updates the manifest according to `autoupdate`.
# Usage:
# $ ./autoupdate.py myPlugin.yaml # update this specific file
# $ ./autoupdate.py myPluginFolder/ # update every manifest in this folder

import yaml
import sys
import os
import dulwich.porcelain
import re
import semver


BASEVERSION = r'^[vV]?((\.?[0-9]+)+)(-?[a-z]+[0-9]*)?$'

def get_latest_versioned_tag_from_refs(refs):
    """
    Given a list of refs (refs/tags/*) containing version numbers with or
    without v prefix.  This function will discover the highest version and
    return the tag name ($name in refs/tags/$name) of the highest version
    number.

    This function supports versions containing a mixed list of v prefix or pure
    numbers.  For example, versions ['v1.2', '1.0.0', 'v2.5-alpha1'] will find
    v2.5-alpha1 tag name to be the highest version.

    Supported version formats where parenthesis show optional values:
        (v) optional prefix
        1.0 a version number of dot-separated nubmers
        (-alpha(1)) optional suffix such as -alpha or -alpha1

    Example:
        get_latest_versioned_tag_from_refs(['refs/tags/1.2.3-beta2', 'refs/tags/v1.2.3', 'refs/tags/1.1.1', 'refs/tags/1.2.3-alpha', 'refs/tags/1.2.3-beta'])
    Returns:
        1.2.3
    """
    # remove refs/tags/ prefix (other refs will exist but will be filtered out
    # in the next step
    tags=list(map(lambda x: x.replace('refs/tags/', ''), refs))
    # filter out only valid version numbers (optional v prefix with a set of
    # numbers separated by periods)
    tags=list(filter(lambda x: re.match(BASEVERSION, x), tags))
    # Sort list from lowest to highest version (last item is highest version)
    # Converts each version number into a list of ints and compares the lists
    # for ordered integers.  The end result is the same list of tag names but
    # sorted according to version number.
    def key(tag):
        match = re.match(BASEVERSION, tag)
        version = list(map(int, match.group(1).split('.'))) # List of ints, so they can be properly compared
        suffix = match.groups()[-1] or '\xff' * 100 # Make sure no suffix is considered "greater" than any other suffix
        return (version, suffix)
    tags.sort(key=key)
    # return the highest version which is the last item in list
    return tags[-1]

def ls_remote(url):
    byte_dict = dulwich.porcelain.ls_remote(url)
    string_dict = {}
    for k, v in byte_dict.items():
        string_dict[k.decode("utf-8")] = v.decode("utf-8")
    return string_dict


def get_latest_version(au_type, au_url, au_branch):
    if au_type == "commit":
        refs = ls_remote(au_url)
        ref = refs.get("refs/heads/" + au_branch)
        if not ref:
            raise LookupError("Branch %s doesn't exist" % au_branch)
        return ref

    if au_type == "tag":
        refs = ls_remote(au_url)
        # Sort by the second tuple item, which is a parser semver object
        # Then return the associated string (so any prefix that `coerce` stripped doesn't get discarded)
        return get_latest_versioned_tag_from_refs(refs)

    raise NotImplementedError("Unknown autoupdate type '%s'" % au_type)


def update(file):
    print("Running autoupdate for " + file)
    with open(file, "r") as f:
        manifest = yaml.load(f, Loader=yaml.FullLoader)

    au = manifest["autoupdate"]
    au_type = au["type"]
    au_url = au.get("update_url", manifest["homepage"])
    # TODO: dulwich needs to support this first: https://github.com/dulwich/dulwich/issues/863
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
