#!/usr/bin/python
"""Ansible module to config SNMP with NAPALM. on Cisco IOS & NXOS."""
import logging
from ansible.module_utils.basic import AnsibleModule
from napalm import get_network_driver
from jinja2 import Template

DOCUMENTATION = r"""
---
module: ntc_snmp

short_description: Configure SNMP communities on Cisco IOS and NXOS

version_added: "1.0.0"

description: Uses NAPALM library to configure SNMP to network devices

options:
    os:
        description: The Network OS of the device based on NAPALM drivers
        required: true
        type: str
    provider:
        description: The NAPALM provider information
        required: true
        type: dict
    community_strings:
        description: SNMP Community information
        required: true
        type: list of dicts
    contact:
        description: SNMP contact information
        required: false
        type: str
    location:
        description: SNMP location information
        required: false
        type: str
    replace:
        description: true / false if you want to replace the SNMP config
        default: false
        required: false
        type: bool

author:
    - Gerasimos Tzakis (@gertzakis)
"""
EXAMPLES = r"""
- name: Configure SNMP through module
    ntc_snmp:
      os: "{{ ansible_network_os }}"
      provider:
        username: ntc
        password: ntc123
        hostname: "{{ inventory_hostname }}"
      community_strings:
        - type: ro
          string: public
        - type: rw
          string: private-new
        - type: rw
          string: private-makis
      contact: Jason
      location: New_York
      replace: false

"""

RETURN = r"""
ok: [host] => {
"msg": {
        "changed": true,
        "config_changes": {
            "replaced": false,
            "snmp_config": "+snmp-server community public RO\n
                            +snmp-server community private-new RW\n
                            +snmp-server community private-makis RW\n
                            +snmp-server contact Jason\n
                            +snmp-server location New_York"
        },
        "failed": false
    }
}
"""


def generate_config(template_file: str, data: dict) -> str:
    """Loads Jinja2 template from file"""
    try:
        logging.info(f"Loading jinja template { template_file }")
        with open(template_file, encoding="UTF-8") as t:
            template = Template(t.read())
            rendered_config = template.render(data=data)
    except IOError as ex:
        logging.error(f"Template file { template_file} could not be opened!")
        logging.error(f"I/O error { ex.errno } '{ ex.strerror }'")
    return rendered_config


def config_device(driver_os: str, device_info: dict, config: str) -> str:
    """Merge config to device using NAPALM.

    Args:
        driver_os (str): NAPALM driver
        device_info (dict): NAPALM provider
        config (str): Configuration to send

    Returns:
        str: config compare output
    """
    res = ""
    driver = get_network_driver(driver_os)
    try:
        logging.info(f"Config SNMP to { device_info['hostname'] }")
        with driver(
            hostname=device_info["hostname"],
            username=device_info["username"],
            password=device_info["password"],
        ) as device:

            device.load_merge_candidate(config=config)
            res = device.compare_config()
            if len(res) > 0:
                device.commit_config()
            return res

    except BaseException as err:
        logging.error(
            f"Could not connect to device { device_info['hostname'] } with error { err }"
        )

    return res


def get_snmp_info(driver_os: str, device_info: dict) -> dict:
    """Gets snmp configuration from device

    Args:
        driver_os (str): NAPALM driver
        device_info (dict): NAPALM provider

    Returns:
        dict: SNMP configuration
    """
    snmp_info = {}
    driver = get_network_driver(driver_os)
    try:
        logging.info(f"Config SNMP to { device_info['hostname'] }")
        with driver(
            hostname=device_info["hostname"],
            username=device_info["username"],
            password=device_info["password"],
        ) as device:
            snmp_info = device.get_snmp_information()

        return snmp_info

    except BaseException as err:
        logging.error(
            f"Could not connect to device { device_info['hostname'] } with error { err }"
        )
    return snmp_info


def main():
    """Ansible module main function"""
    fields = {
        "os": {"required": True, "choices": ["ios", "nxos"], "type": "str"},
        "provider": {"required": True, "type": "dict"},
        "community_strings": {"required": True, "type": "list"},
        "contact": {"required": False, "type": "str"},
        "location": {"required": False, "type": "str"},
        "replace": {"default": "false", "choices": [True, False], "type": "bool"},
    }

    result = {}
    module = AnsibleModule(argument_spec=fields)

    if module.params["replace"]:
        curr_snmp_config = get_snmp_info(
            driver_os=module.params["os"], device_info=module.params["provider"]
        )
        no_snmp_config = generate_config(
            template_file="library/templates/no_snmp_config.j2", data=curr_snmp_config
        )
        config_device(
            driver_os=module.params["os"],
            device_info=module.params["provider"],
            config=no_snmp_config,
        )

    snmp_config = generate_config(
        template_file="library/templates/snmp_config.j2", data=module.params
    )
    result["snmp_config"] = config_device(
        driver_os=module.params["os"],
        device_info=module.params["provider"],
        config=snmp_config,
    )
    result["replaced"] = module.params["replace"]

    if len(result["snmp_config"]) > 0:
        module.exit_json(changed=True, config_changes=result)
    else:
        module.exit_json(changed=False, config_changes=result)


if __name__ == "__main__":
    main()
