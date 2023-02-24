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
module: rubrik_login_banner
short_description: Configure the Rubrik cluster login banner text.
description:
    - Configure the Rubrik cluster login banner text.
version_added: '2.8'
author: Eric Alba (@KowMangler) <noman.wonder@gmail.com>
options:
  banner_text:
    description:
      - The Login Banner you wish the Rubrik cluster to display prior to user login.
    required: True
    type: str
  timeout:
    description:
      - The number of seconds to wait to establish a connection the Rubrik cluster before returning a timeout error.
    required: False
    type: int
    default: 15

extends_documentation_fragment: rubrikinc.cdm.credentials
requirements: [rubrik_cdm]
'''

EXAMPLES = '''
- rubrik_login_banner:
    banner_text: "This is a pre-login Banner. Welcome to Rubrik!"
'''


RETURN = '''
full_response:
    description: The full API response for PUT /internal/cluster/me/login_banner
    returned: on success
    type: dict

idempotent_response:
    description: A "No changed required" message when the banner text is identical to that which is already configured on the cluster.
    returned: When the module idempotent check is succesful.
    type: str
    sample: No change required. The Rubrik cluster is already configured with I(banner_text) as it's banner.
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
        banner_text=dict(required=True, type='str'),
        timeout=dict(required=False, type='int', default=15),
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

    try:
        api_request = rubrik.configure_login_banner(ansible["banner_text"], ansible["timeout"])
    except Exception as error:
        module.fail_json(msg=str(error))

    results = {
        "changed": "No change required" not in api_request,
        "response": api_request,
    }
    module.exit_json(**results)


if __name__ == '__main__':
    main()
