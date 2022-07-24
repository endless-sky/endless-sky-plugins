#!/usr/bin/env python3

# Generates a yaml file containing all plug-ins.
# Usage: ./generate_table.py manifests/ generated/plugins.yaml

import yaml
import sys
import os


manifest_dir = sys.argv[1]
manifests = []
for filename in os.listdir(manifest_dir):
    file = os.path.join(manifest_dir, filename)
    with open(file, "r") as f:
        manifests.append(yaml.load(f, Loader=yaml.FullLoader))

with open(sys.argv[2], "w") as f:
    yaml.dump(manifests, f, sort_keys=False)
