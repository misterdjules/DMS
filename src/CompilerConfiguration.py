import syslog
import string

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

    return (tuple(erroneous_keys), config_valid)
