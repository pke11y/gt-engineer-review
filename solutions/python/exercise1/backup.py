from imaplib import Commands
import yaml
from yaml.loader import FullLoader
from pathlib import Path
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from constants import USERNAME, PASSWORD, BACKUP_DIR, COMMANDS


def send_command(device:dict, command:str):
    """_summary_
    Args:
        device (dict): _description_
        command (str): _description_
    Returns:
        _type_: _description_
    """
    try:
        with ConnectHandler(**device) as ssh:
            # ssh.enable()
            output = ssh.send_command(command)
        
        return output
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        print(error)
            

def write_file(file_name:str, text:str):
    """
    """

    # if Path(file_name):
    #     Path(file_name).mkdir(parents=True, exist_ok=True)
    try:
        with open(file_name, "w") as f:
            f.write(text)
    except IOError as err:
        print(f"Could not read to file: { err }")


def main():
    """_summary_
    """
    devices_info = read_yaml("hosts.yaml")
    
    # print(type(devices_info["devices"]))
    
    # for item,value in devices_info.items():
    #     print(devices_info[item])
        # print(item["csr1"])
        # device_result = send_command(device=item, command="show running config")
        # print(device_result)
        
    for device in devices_info.keys():
        print(device)
        devices_info[device]["username"]=USERNAME
        devices_info[device]["password"]=PASSWORD
        # print(devices_info[device])
        device_result = send_command(device=devices_info[device], 
            command=COMMANDS[devices_info[device]["device_type"]])
        # print(device_result)
        write_file(file_name=f"{BACKUP_DIR}/{device}.cfg", text=device_result)


def read_yaml(filename: str):
    try:
        print(f"Getting data from { filename }")

        with open(filename) as f:
            yaml_data = yaml.load(f, Loader=FullLoader)
    except IOError as ex:
        print(f"Yaml data file { filename } could not be opened!")
        print(f"I/O error { ex.errno } '{ ex.strerror }'")
        sys.exit(1)
    
    return yaml_data["devices"]


if __name__ == "__main__":
    main()