import syslog
import pwd
import os
import stat
import sys
import grp
import string
import CommonDaemonConfiguration

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

    # check the CommonDaemonConfiguration
    
    check_results = CommonDaemonConfiguration.check_values(config_values)
    config_valid = check_results[1]

    erroneous_keys += list(check_results[0])

    # check if the scheduler_port is a valid string int
    try:
        string.atoi(config_values["scheduler_port"], 10)
    except:
        config_valid = 0
        erroneous_keys.append("scheduler_port")
        syslog.syslog(syslog.LOG_WARNING | syslog.LOG_DAEMON, \
                      "Warning : in the configuration file the scheduler_port is "\
                      + "a bad string representing an int : "
                      +  config_values["scheduler_port"])

    # check if the port is a valid string int
    try:
        string.atoi(config_values["port"], 10)
    except:
        config_valid = 0
        erroneous_keys.append("port")
        syslog.syslog(syslog.LOG_WARNING | syslog.LOG_DAEMON, \
                      "Warning : in the configuration file the port is "\
                      + "a bad string representing an int : "
                      +  config_values["port"])

    return (tuple(erroneous_keys), config_valid)
