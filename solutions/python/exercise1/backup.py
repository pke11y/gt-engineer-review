"""Get backups of running config from devices."""
import sys
import logging
from pathlib import Path
import yaml
from yaml.loader import FullLoader
from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)
from constants import USERNAME, PASSWORD, BACKUP_DIR, COMMANDS


def send_command(device: dict, command: str) ->str:
    """Connect with netmiko and send one command.

    Args:
        device (dict): Device info in netmiko dict format
        command (str): Command to send to device

    Returns:
        str: command output
    """
    output = ""
    try:
        logging.info(f"Connect to device { device['host'] }")
        with ConnectHandler(**device) as ssh:
            output = ssh.send_command(command)

        return output
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        logging.error(
            f"Could not connect to device { device['host'] } with error {error}"
        )
    return output


def write_file(file_name: str, text: str):
    """Write text to file.

    Args:
        file_name (str): file name and parent dir
        text (str): text to be written
    """
    # Create parent directory if not exists
    file_dir = Path(file_name).parent.absolute()
    if not file_dir.exists():
        logging.info(f"Creating directory { file_dir } for backups")
        file_dir.mkdir(parents=True)

    try:
        logging.info(f"Write output to file { file_name }")
        with open(file_name, "w", encoding="UTF-8") as f:
            f.write(text)
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
    """Connect to devices and save the running config to files as backup."""
    logging.basicConfig(level=logging.INFO)
    devices_info = read_yaml("hosts.yaml")

    for device, device_info in devices_info["devices"].items():
        device_info["username"] = USERNAME
        device_info["password"] = PASSWORD
        device_output = send_command(
            device=device_info, command=COMMANDS[device_info["device_type"]]
        )
        write_file(file_name=f"{BACKUP_DIR}/{device}.cfg", text=device_output)


if __name__ == "__main__":
    main()
