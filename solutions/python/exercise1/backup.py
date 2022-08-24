"""Get backups of running config from devices."""
import sys
import logging
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)
from constants import USERNAME, PASSWORD, BACKUP_DIR, COMMANDS


def send_command(device: dict, command: str) -> str:
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


def create_parent_dir(dir_name: str) -> None:
    """Create parent directory for backup files.

    Args:
        dir_name (str): file name with parent dir
    """

    try:
        files_dir = Path(dir_name).absolute()
        logging.info(f"Creating directory { dir_name } for backups if not exists")
        files_dir.mkdir(parents=True, exist_ok=True)
    except OSError as err:
        logging.error(f"Could not create dir { dir_name }!")
        logging.error(f"OS error { err.errno } '{ err.strerror }'")


def write_file(file_name: str, text: str) -> None:
    """Write text to file.

    Args:
        file_name (str): file name and parent dir
        text (str): text to be written
    """

    try:
        logging.info(f"Write output to file { file_name }")
        with open(file_name, "w", encoding="UTF-8") as f:
            f.write(text)
    except OSError as err:
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
        logging.debug(f"Read data from { file_name }")
        with open(file_name, encoding="UTF-8") as f:
            yaml_data = yaml.load(f, Loader=SafeLoader)
    except OSError as err:
        logging.error(f"Yaml data file { file_name } could not be opened!")
        logging.error(f"I/O error { err.errno } '{ err.strerror }'")
        sys.exit(1)

    return yaml_data


def main() -> None:
    """Connect to devices and save the running config to files as backup."""
    logging.basicConfig(level=logging.INFO)
    create_parent_dir(dir_name=BACKUP_DIR)
    inventory = read_yaml("hosts.yaml")

    for device, device_info in inventory["devices"].items():
        device_info["username"] = USERNAME
        device_info["password"] = PASSWORD
        device_output = send_command(
            device=device_info,
            command=COMMANDS.get(device_info["device_type"], "show running-config"),
        )
        write_file(file_name=f"{BACKUP_DIR}/{device}.cfg", text=device_output)


if __name__ == "__main__":
    main()
