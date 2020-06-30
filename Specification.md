### plugins.yaml

The `plugins.yaml` file contains a list of objects, each representing a plug-in.

YAML has been chosen because of its good readability while still being machine-readable and reasonably widespread. Compatibility with other formats is achieved through the CI, which converts the YAML file to other formats.

### Plug-Ins

A Plug-In object consists of the following key-value pairs:

- `name`
- `url`: A link to the project's github repository.
- `version`: Preferably the name of a git tag, or a commit hash.
- `author`: The author(s) of the plug-in.
- `iconUrl` (optional): A direct URL to an image that is used as thumbnail. If possible, the image should be 160x160 pixels large.
- `description`: A short-to-medium length description, similar to the plug-in's `about.txt`.

