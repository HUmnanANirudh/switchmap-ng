#!/usr/bin/env python3
"""Switchmap-NG setup.

Manages parameters required by all classes in the module.

"""

# Standard imports
from collections import namedtuple

# Do library imports
from .core import log
from .poller.update import TrunkInterface

# Create global variables for the various daemons
SITE_PREFIX = "/switchmap"

# API URIs
API_PREFIX = "{}/api".format(SITE_PREFIX)
API_POLLER_POST_URI = "/post/poller"

# DASHBOARD related
DASHBOARD_PREFIX = "{}/dashboard".format(SITE_PREFIX)
DASHBOARD_STATIC_FOLDER = "static/default"
DASHBOARD_TEMPLATE_FOLDER = "templates/default"

# Agent related
AGENT_POLLER = "Poller"
AGENT_INGESTER = "Ingester"
AGENT_DASHBOARD = "Dashboard"
AGENT_DASHBOARD_CHILD = "switchmap-dashboard"
AGENT_API = "API"
AGENT_API_CHILD = "switchmap-api"

# Important tuples
Found = namedtuple("Found", "idx_l1interface")
IP = namedtuple("IP", "address version")
MacDetail = namedtuple(
    "MacDetail", "hostname mac ip_ organization idx_l1interface idx_mac"
)
InterfaceDetail = namedtuple(
    "InterfaceDetail", "RL1Interface MacDetails RVlans"
)
DeviceDetail = namedtuple("DeviceDetail", "RDevice InterfaceDetails")


def main():
    """Process data.

    Args:
        None

    Returns:
        None

    """
    # Check the environment
    log.check_environment()


if __name__ == "switchmap":
    main()
