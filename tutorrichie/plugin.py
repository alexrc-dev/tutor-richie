from glob import glob
import os
import pkg_resources
from tutor import hooks

from .__about__ import __version__

# templates = pkg_resources.resource_filename("tutorrichie", "templates")

config = {
    "add": {
        "HOOK_SECRET": "{{ 20|random_string }}",
        "SECRET_KEY": "{{ 20|random_string }}",
        "MYSQL_PASSWORD": "{{ 12|random_string }}",
    },
    "defaults": {
        "VERSION": __version__,
        "DOCKER_IMAGE": "{{ DOCKER_REGISTRY }}overhangio/openedx-richie:{{ RICHIE_VERSION }}",
        "RELEASE_VERSION": "v2.9.2",
        "HOST": "courses.{{ LMS_HOST }}",
        "MYSQL_DATABASE": "richie",
        "MYSQL_USERNAME": "richie",
        "ELASTICSEARCH_INDICES_PREFIX": "richie",
    },
}

# hooks = {
#     "build-image": {"richie": "{{ RICHIE_DOCKER_IMAGE }}"},
#     "remote-image": {"richie": "{{ RICHIE_DOCKER_IMAGE }}"},
#     "init": ["mysql", "richie", "richie-openedx"],
# }
# Initialization hooks
for service in ("mysql", "richie", "richie-openedx"):
    with open(
            os.path.join(
                pkg_resources.resource_filename("tutorrichie", "templates"),
                "richie",
                "hooks",
                service,
                "init",
            ),
            encoding="utf-8",
    ) as task_file:
        hooks.Filters.CLI_DO_INIT_TASKS.add_item((service, task_file.read()))
# Image management
hooks.Filters.IMAGES_BUILD.add_items(
    [
        (
            "richie",
            ("plugins", "richie", "build", "richie"),
            "{{ RICHIE_DOCKER_IMAGE }}",
            (),
        ),
    ]
)
hooks.Filters.IMAGES_PULL.add_items(
    [
        (
            "richie",
            "{{ RICHIE_DOCKER_IMAGE }}",
        ),
    ]
)
hooks.Filters.IMAGES_PUSH.add_items(
    [
        (
            "richie",
            "{{ RICHIE_DOCKER_IMAGE }}",
        ),
    ]
)
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    pkg_resources.resource_filename("tutorrichie", "templates")
)
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [(f"RICHIE_{key}", value) for key, value in config["defaults"].items()]
)
hooks.Filters.CONFIG_UNIQUE.add_items(
    [(f"RICHIE_{key}", value) for key, value in config["add"].items()]
)


def patches():
    all_patches = {}
    patches_dir = pkg_resources.resource_filename("tutorrichie", "patches")
    for path in glob(os.path.join(patches_dir, "*")):
        with open(path) as patch_file:
            name = os.path.basename(path)
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
