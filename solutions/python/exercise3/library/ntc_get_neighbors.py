#!/usr/bin/python
"""Ansible module to get lldp neighbors with NAPALM."""
import logging
from ansible.module_utils.basic import AnsibleModule
from napalm import get_network_driver

DOCUMENTATION = r"""
---
module: ntc_get_neighbors

short_description: Gets lldp neighbors

version_added: "1.0.0"

description: Uses NAPALM library to get lldp neighbors from network devices

options:
    os:
        description: The Network OS of the device based on NAPALM drivers
        required: true
        type: str
    provider:
        description: The NAPALM provider information
        required: true
        type: dict

author:
    - Gerasimos Tzakis (@gertzakis)
"""
EXAMPLES = r"""
- name: Get lldp neighbors through module
ntc_get_neighbors:
    os: "{{ ansible_network_os }}"
    provider:
    username: user
    password: pass
    hostname: "{{ inventory_hostname }}"

"""

RETURN = r"""
lldp_neighbors:
    description: The lldp neighbors of host
    type: str
    sample: "lldp_neighbors": {
                "ge-0/0/0": [
                    {
                        "neighbor": "vmx1",
                        "neighbor_interface": "ge-0/0/0"
                    }
                ],
                "ge-0/0/2": [
                    {
                        "neighbor": "vmx2",
                        "neighbor_interface": "ge-0/0/2"
                    }
                ],
                "ge-0/0/3": [
                    {
                        "neighbor": "csr3.ntc.com",
                        "neighbor_interface": "Gi4"
                    }
                ]
            }
"""


def get_lldp_neighbors(driver_os: str, device_info: dict) -> dict:
    """Get lldp neighbors from device with NAPALM.
    Args:
        device_info (dict): device connection information
    Returns:
        dict: lldp neighbors of device
    """
    device_lldp_neighbors = {}
    driver = get_network_driver(driver_os)
    try:
        logging.info(f"Get lldp neighbors from device { device_info['hostname'] }")
        with driver(
            hostname=device_info["hostname"],
            username=device_info["username"],
            password=device_info["password"],
        ) as device:
            device_lldp_neighbors = device.get_lldp_neighbors()
            return device_lldp_neighbors
    except BaseException as err:
        logging.error(
            f"Could not connect to device { device_info['hostname'] } with error { err }"
        )

    return device_lldp_neighbors


def replace_dict_key(lldp_neighbors: dict) -> dict:
    """Replace keys for neighbors under interfaces in dict.
    Args:
        lldp_neighbors (dict): full dict with lldp information
    Returns:
        dict: full dict changed hostname with neighbor and port with neighbor_interface
    """
    for lldp_interface in lldp_neighbors.values():
        for neighbor in lldp_interface:
            neighbor["neighbor"] = neighbor.pop("hostname")
            neighbor["neighbor_interface"] = neighbor.pop("port")

    return lldp_neighbors


def main():
    """Ansible module main function"""
    fields = {
        "os": {"required": True, "type": "str"},
        "provider": {"required": True, "type": "dict"},
    }

    module = AnsibleModule(argument_spec=fields)
    lldp_neighbors = get_lldp_neighbors(
        driver_os=module.params["os"], device_info=module.params["provider"]
    )
    result = replace_dict_key(lldp_neighbors=lldp_neighbors)
    # module.exit_json(changed=False, meta=module.params)
    module.exit_json(changed=False, lldp_neighbors=result)


if __name__ == "__main__":
    main()
