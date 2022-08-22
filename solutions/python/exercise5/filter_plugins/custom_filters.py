#!/usr/bin/python
"""Ansible custom jinja2 filters"""


class FilterModule:
    """Ansible Filter class"""
    def filters(self):
        """Ansible filters"""
        return {"expand_interfaces": self.expand_interfaces}

    def expand_interfaces(self, interfaces, profiles):
        """Exapnd interfaces info from profiles

        Args:
            interfaces (list): list of dicts with interface info
            profiles (dict): dict of dicts for every profile

        Returns:
            list: list of dicts with enchanced the interface info
        """
        for interface in interfaces:
            interface.update(profiles[interface["profile"]])

        return interfaces
