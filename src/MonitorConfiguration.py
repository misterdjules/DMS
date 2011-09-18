import syslog
import pwd
import os
import stat
import sys
import grp
import string

"""Utility functions for configuration of the Compiler
daemon. Every module that needs to use a configuration file
should supply a function such as check_values(), even it
is just a "pass" instruction."""
    
def check_values(config_values):
    """Check if all the configuration values are correct and usable.
    Emit a warning for each bad value.
    Return false if at least one configuration value is erroneous,
    and a tuple containing the keys that contain bad values, and need to be replaced
    by default ones."""

    # tuple containing names of the configuration dictionnary keys that
    # are erroneous
    erroneous_keys = []
    
    config_valid = 1

    return (tuple(erroneous_keys), config_valid)
