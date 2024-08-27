# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

# builtin
import json
import logging
import os

# internal
from stixmarx import utils

# Module-level logger
LOG = logging.getLogger(__name__)

_FIELD_MAPPINGS = {}


def get_field_mappings():
    return _FIELD_MAPPINGS


def update_field_mappings(mappings):
    global _FIELD_MAPPINGS
    _FIELD_MAPPINGS.update(mappings)


def _initialize_fields():
    utils._load_stix()
    utils._load_cybox()
    utils._load_maec()
    utils._load_mixbox()

    if workdir_path := os.getenv("STIXMARX_WORKDIR_PATH"):
        field_load_path = os.path.join(workdir_path, ".stixmarx")
    else:
        field_load_path = os.path.join(os.path.expanduser("~"), ".stixmarx")

    if os.path.isdir(field_load_path) is False:
        os.makedirs(field_load_path)
        LOG.debug("Created directory '%s'", field_load_path)

    for loaded_module, module_name in ((utils.stix, "stix"), (utils.cybox, "cybox"), (utils.maec, "maec")):
        if loaded_module:
            fname = module_name + loaded_module.__version__.replace(".", "") + ".json"
            file_location = os.path.join(field_load_path, fname)

            if os.path.isfile(file_location) is False:
                message = "Generating compatible mappings for %s %s"
                LOG.info(message, module_name, loaded_module.__version__)

                obj_mapper = utils.ModelMapper(module_name)
                model_resource = obj_mapper.to_dict()
                with open(file_location, "w") as f:
                    json.dump(model_resource, f)
                LOG.debug("Saved %s", file_location)
            else:
                with open(file_location, "r") as f:
                    model_resource = json.load(f)
                LOG.debug("Loaded %s", file_location)

            _FIELD_MAPPINGS.update(model_resource["fields"])
            LOG.debug("Updated field mappings for %s", module_name)
        else:
            message = "No %s library found in environment."
            LOG.debug(message, module_name)


_initialize_fields()
