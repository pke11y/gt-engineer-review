"""Get backups of running config from devices."""
from code import interact
import sys
import logging
from pathlib import Path
from textwrap import indent
import yaml
import json
from yaml.loader import FullLoader
from napalm import get_network_driver
from constants import USERNAME, PASSWORD, BACKUP_DIR, COMMANDS


def get_lldp_neighbors(device_info: dict)-> dict:
    """Get lldp neighbors from device with NAPALM.

    Args:
        device_info (dict): device connection information

    Returns:
        dict: lldp neighbors of device
    """
    device_lldp_neighbors = {}
    driver = get_network_driver(device_info["device_type"])
    try:
        logging.info(f"Get lldp neighbors from device { device_info['host'] }")
        with driver(
            hostname=device_info["host"],
            username=device_info["username"],
            password=device_info["password"],
        ) as device:
            device_lldp_neighbors = device.get_lldp_neighbors()
            return device_lldp_neighbors
    except BaseException as err:
        logging.error(f"Could not connect to device { device_info['host'] } with error { err }")

    return device_lldp_neighbors

def replace_dict_key(lldp_neighbors: dict) -> dict:
    """Replace keys for neighbors under interfaces in dict.

    Args:
        lldp_neighbors (dict): full dict with lldp information

    Returns:
        dict: full dict changed hostname with neighbor and port with neighbor_interface
    """
    for lldp_interfaces in lldp_neighbors.values():
        for neighbors in lldp_interfaces.values():
            for neighbor in neighbors:
                neighbor["neighbor"] = neighbor.pop("hostname")
                neighbor["neighbor_interface"] = neighbor.pop("port")

    return lldp_neighbors

def write_json_file(file_name: str, text: dict):
    """Write text to file.

    Args:
        file_name (str): file name and parent dir
        text (dict): json to be written
    """
    # Create parent directory if not exists
    file_dir = Path(file_name).parent.absolute()
    if not file_dir.exists():
        logging.info(f"Creating directory { file_dir } for backups")
        file_dir.mkdir(parents=True)

    try:
        logging.info(f"Write output to file { file_name }")
        with open(file_name, "w", encoding="UTF-8") as f:
            f.write(json.dumps(text))
    except IOError as err:
        logging.error(f"File { file_name } could not be opened!")
        logging.error(f"I/O error { err.errno } '{ err.strerror }'")


def read_yaml(file_name: str) -> dict:
    """Read yaml file.

    Args:
        filename (str): name of file

    Returns:
        dict: data from yaml file
    """
    try:
        logging.info(f"Read data from { file_name }")
        with open(file_name, encoding="UTF-8") as f:
            yaml_data = yaml.load(f, Loader=FullLoader)
    except IOError as err:
        logging.error(f"Yaml data file { file_name } could not be opened!")
        logging.error(f"I/O error { err.errno } '{ err.strerror }'")
        sys.exit(1)

    return yaml_data


def main() -> None:
    """Connect to devices and get lldp neighbors."""
    logging.basicConfig(level=logging.INFO)
    devices_info = read_yaml("hosts.yaml")
    lldp_neighbors = {}
    
    for device, device_info in devices_info["devices"].items():
        device_info["username"] = USERNAME
        device_info["password"] = PASSWORD
        lldp_neighbors[device] = get_lldp_neighbors(device_info=device_info)

    lldp_neighbors = replace_dict_key(lldp_neighbors)
    print(json.dumps(lldp_neighbors, indent=4))
    write_json_file(file_name="lldp_neighbors.json", text=lldp_neighbors)


if __name__ == "__main__":
    main()
