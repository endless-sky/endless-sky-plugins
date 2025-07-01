#!/usr/bin/env python3

# Check whether a new plug-in version exists. When one is found, updates the manifest according to `autoupdate`.
# Usage:
# $ ./autoupdate.py myPlugin.yaml # update this specific file
# $ ./autoupdate.py myPluginFolder/ # update every manifest in this folder

import yaml
import sys
import os
import dulwich.porcelain
import functools
import re
import itertools
from traceback import print_exc


BASEVERSION = r"^[vV]?([0-9]+(\.[0-9]+)*)[a-z]?(-?[a-z.]+[0-9]*)?$"
VERSION_COMPONENTS = re.compile(r"(\d+ | [a-z]+ | \.)", re.VERBOSE)


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
        (c) an optional letter
        (-alpha(1)) optional suffix such as -alpha or -alpha1

    Example:
        get_latest_versioned_tag_from_refs(['refs/tags/1.2.3-beta2', 'refs/tags/v1.2.3', 'refs/tags/1.1.1a', 'refs/tags/1.2.3-alpha', 'refs/tags/1.2.3-beta'])
    Returns:
        1.2.3
    """
    # remove refs/tags/ prefix (other refs will exist but will be filtered out
    # in the next step
    tags = list(map(lambda x: x.replace("refs/tags/", ""), refs))
    # filter out only valid version numbers (optional v prefix with a set of
    # numbers separated by periods)
    tags = list(filter(lambda x: re.match(BASEVERSION, x), tags))
    # Sort list from lowest to highest version (last item is highest version)

    # This is taken from distutils.version.LooseVersion - we need access to the component list, so we have to reimplement
    def parse_version(vstring):
        vstring = vstring.lstrip("vV")
        components = [x for x in VERSION_COMPONENTS.split(vstring) if x and x != "."]
        for i, obj in enumerate(components):
            try:
                components[i] = int(obj)
            except ValueError:
                pass
        return components

    def cmp(tag1, tag2):
        components1 = parse_version(tag1)
        components2 = parse_version(tag2)
        # can't compare mixed lists of int & str directly, so we iterate
        for x, y in itertools.zip_longest(components1, components2):
            if x == y:
                continue
            # longer version > shorter version
            if x is None:
                return -1
            if y is None:
                return 1
            if type(x) != type(y):
                # in case of mixed types, int > str
                return (type(x) == int) - (type(y) == int)
            else:
                return (x > y) - (x < y)  # old school cmp
        return 0  # equality

    tags.sort(key=functools.cmp_to_key(cmp))
    # return the highest version which is the last item in list
    return tags[-1]


def decode_byte_dict(input):
    output = {}
    for k, v in input.items():
        output[k.decode("utf-8")] = v.decode("utf-8")
    return output


def get_latest_version(au_type, au_url, au_branch):
    ls_remote = dulwich.porcelain.ls_remote(au_url)
    refs = decode_byte_dict(ls_remote.refs)
    symrefs = decode_byte_dict(ls_remote.symrefs)

    if au_type == "commit":
        if not au_branch:
            head_ref = symrefs.get("HEAD")
            if not head_ref:
                raise LookupError(
                    "no HEAD in ls-remote symrefs, can't determine default branch"
                )
            au_branch = head_ref.removeprefix("refs/heads/")

        commit = refs.get("refs/heads/" + au_branch)
        if not commit:
            raise LookupError("Branch %s doesn't exist" % au_branch)
        return commit

    elif au_type == "tag":
        # Sort by the second tuple item, which is a parser semver object
        # Then return the associated string (so any prefix that `coerce` stripped doesn't get discarded)
        return get_latest_versioned_tag_from_refs(refs)

    raise NotImplementedError("Unknown autoupdate type '%s'" % au_type)


def update(file):
    print("Running autoupdate for " + file)
    with open(file, "r") as f:
        manifest = yaml.load(f, Loader=yaml.FullLoader)

    if not "autoupdate" in manifest:
        return

    au = manifest["autoupdate"]
    au_type = au["type"]
    au_url = au.get("update_url", manifest["homepage"])
    # TODO: dulwich needs to support this first: https://github.com/dulwich/dulwich/issues/863
    au_branch = au.get("branch")
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

error = False
for file in files:
    try:
        update(file)
    except Exception:
        error = True
        print("Error while updating {file}, stacktrace follows:")
        print_exc()
        print("Exit code will be non-zero")

if error:
    exit(1)
