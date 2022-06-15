#!/usr/bin/env python3
"""Script to flag duplicate error codes."""

from __future__ import print_function
import os
import sys


# Try to create a working PYTHONPATH
EXEC_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(
    os.path.abspath(os.path.join(EXEC_DIR, os.pardir)), os.pardir))
_EXPECTED = '{0}switchmap-ng{0}tests{0}bin'.format(os.sep)
if EXEC_DIR.endswith(_EXPECTED) is True:
    # We need to prepend the path in case the repo has been installed
    # elsewhere on the system using PIP. This could corrupt expected results
    sys.path.insert(0, ROOT_DIR)
else:
    print('''This script is not installed in the "{0}" directory. Please fix.\
'''.format(_EXPECTED))
    sys.exit(2)


# Import application libraries
from tests.testlib_ import errors


def main():
    """Process the error codes.

    Args:
        None

    Returns:
        None

    """
    # Get code report
    minimum = 1000
    maximum = 9999
    errors.check_source_code(ROOT_DIR, minimum=minimum, maximum=maximum)


if __name__ == '__main__':
    main()
