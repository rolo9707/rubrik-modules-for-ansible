#!/usr/bin/python
# (c) 2018 Rubrik, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
module: rubrik_physical_host
short_description: Add or delete a physical host from a Rubrik cluster.
description:
    - Add or delete a physical host from a Rubrik cluster.
version_added: '2.8'
author: Rubrik Build Team (@drew-russell) <build@rubrik.com>
options:
  hostname:
    description:
      - The hostname or IP Address of the physical host you want to add or delete from the Rubrik cluster.
      - When C(action=add) this may also be a list of hostnames.
    required: True
    type: raw
    aliases: ["ip_address"]
  action:
    description:
      - Specify whether or not you wish to add or delete the physical host from the Rubrik cluster.
    required: True
    type: str
    choices: [add, delete]
  timeout:
    description:
      - The number of seconds to wait to establish a connection the Rubrik cluster before returning a timeout error.
    required: False
    type: int
    default: 120


extends_documentation_fragment: rubrikinc.cdm.credentials
requirements: [rubrik_cdm]
'''

EXAMPLES = '''
- rubrik_physical_host:
    hostname: 'ubuntu-physical-demo'
    action: 'add'

- rubrik_physical_host:
    hostname: 'ubuntu-physical-demo'
    action: 'delete'
'''

RETURN = '''
full_response_action_add:
    description: The full API response for POST /v1/host
    returned: on success when action is add
    type: dict
    sample:
        {
            "id": "string",
            "hostname": "string",
            "primaryClusterId": "string",
            "operatingSystem": "string",
            "operatingSystemType": "string",
            "status": "string",
            "agentId": "string",
            "compressionEnabled": true
        }

success_response_action_delete:
    description: The full API response for DELETE /v1/host/{id}.
    returned: on success when action is delete
    type: dict
    sample: {"status_code": 204}

idempotent_response_action_add:
    description: A "No changed required" message when the host has already been added to the Rubrik cluster.
    returned: When the module idempotent check is succesful and action is add.
    type: str
    sample: No change requird. The host 'hostname' is already connected to the Rubrik cluster.

idempotent_response_action_delete:
    description: A "No changed required" message when the host is not present on the Rubrik cluster.
    returned: When the module idempotent check is succesful and action is delete.
    type: str
    sample: No change required. The host 'hostname' is not connected to the Rubrik cluster.
'''

from ansible.module_utils.rubrik_cdm import credentials, load_provider_variables, rubrik_argument_spec
from ansible.module_utils.basic import AnsibleModule

try:
    import rubrik_cdm
    HAS_RUBRIK_SDK = True
except ImportError:
    HAS_RUBRIK_SDK = False


def main():
    """ Main entry point for Ansible module execution.
    """

    argument_spec = dict(
        hostname=dict(required=True, aliases=['ip_address'], type="raw"),
        action=dict(required=True, choices=['add', 'delete']),
        timeout=dict(required=False, type='int', default=120),

    )

    argument_spec |= rubrik_argument_spec

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    ansible = module.params

    load_provider_variables(module)

    if not HAS_RUBRIK_SDK:
        module.fail_json(msg='The Rubrik Python SDK is required for this module (pip install rubrik_cdm).')

    node_ip, username, password, api_token = credentials(module)

    try:
        rubrik = rubrik_cdm.Connect(node_ip, username, password, api_token)
    except Exception as error:
        module.fail_json(msg=str(error))

    if ansible["action"] == "add":
        try:
            api_request = rubrik.add_physical_host(ansible["hostname"], ansible["timeout"])
        except Exception as error:
            module.fail_json(msg=str(error))
    elif ansible["action"] == "delete":

        # module.fail_json(msg=str(ansible["hostname"]))

        if isinstance(ansible["hostname"], list):
            module.fail_json(msg="A list of hostnames is not supported when action is delete.")
        try:
            api_request = rubrik.delete_physical_host(ansible["hostname"], ansible["timeout"])
        except Exception as error:
            module.fail_json(msg=str(error))

    results = {
        "changed": "No change required" not in api_request
        and "No Change Required" not in api_request,
        "response": api_request,
    }
    module.exit_json(**results)


if __name__ == '__main__':
    main()
