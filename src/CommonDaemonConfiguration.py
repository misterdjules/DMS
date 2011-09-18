import syslog
import pwd
import os
import stat
import sys
import grp
import string

"""Utility functions for configuration of common
daemon. Every module that needs to use a configuration file
should supply a function such as check_values(), even it
is just a "pass" instruction."""

def user_is_in_group(user_name, group_name):
    """Return true if the user of name user_name is
    in the group group_name."""
    for group in grp.getgrall():
        if group_name == group[0] and (user_name in group[3]):
            return 1
    return 0
    
def check_values(config_values):
    """Check if all the configuration values are correct and usable.
    Emit a warning for each bad value.
    Return false if at least one configuration value is erroneous,
    and a tuple containing the keys that contain bad values, and need to be replaced
    by default ones."""

    config_valid = 1
    erroneous_keys = []
    
    # check if the user exists
    try:
        pwd.getpwnam(config_values["user_privilege"])
    except KeyError:
        syslog.syslog(syslog.LOG_WARNING | syslog.LOG_DAEMON, \
                      "The user : " + config_values["user_privilege"]\
                      + " doesn't exist.")
        config_valid = 0
        erroneous_keys.append("user_privilege")
    else:
        # check for tmp dir access
        try:
            stat_res = os.stat(config_values["temp_dir"])
        except OSError:
            config_valid = 0
            erroneous_keys.append("temp_dir")
        else:
            owner_perms_to_check = stat.S_IWUSR | stat.S_IXUSR
            grp_perms_to_check = stat.S_IWGRP | stat.S_IXGRP
            others_perms_to_check = stat.S_IWOTH | stat.S_IXOTH
            
            uid_config_user = pwd.getpwnam(config_values["user_privilege"])[2]
            if (uid_config_user == stat_res[4]):
                # user of the config file is the owner of the tmp directory
                if (stat_res[stat.ST_MODE] & owner_perms_to_check) != owner_perms_to_check:
                    syslog.syslog(syslog.LOG_WARNING | syslog.LOG_DAEMON, \
                                  "Warning : can't create file in temporary \
                                  directory : " + config_values["temp_dir"])
                    config_valid = 0
                    erroneous_keys.append("temp_dir")
                    
            elif  stat_res[5] == pwd.getpwnam(config_values["user_privilege"])[3]:
                owner_group_name = grp.getgrgid(stat_res[5])[0]
                if  user_is_in_group(config_values["user_privilege"], owner_group_name) \
                       and stat_res[stat.ST_MODE] & grp_perms_to_check != grp_perms_to_check:   
                    syslog.syslog(syslog.LOG_WARNING | syslog.LOG_DAEMON, \
                                  "Warning : can't create file in temporary \
                                  directory : " + config_values["temp_dir"])
                    config_valid = 0
                    erroneous_keys.append("temp_dir")
                    
            elif (stat_res[stat.ST_MODE] & others_perms_to_check) != others_perms_to_check:
                syslog.syslog(syslog.LOG_WARNING | syslog.LOG_DAEMON, \
                              "Warning : can't create file in temporary \
                              directory : " + config_values["temp_dir"])
                config_valid = 0
                erroneous_keys.append("temp_dir")
                
    # check if the directory of the lock file path exists
    try:
        os.stat(os.path.dirname(config_values["lock_file_path"]))
    except OSError:
        config_valid = 0
        erroneous_keys.append("lock_file_path")
        syslog.syslog(syslog.LOG_WARNING | syslog.LOG_DAEMON, \
                      "Warning : the lock directory : "\
                      +  os.path.dirname(config_values["lock_file_path"])\
                      + " doesn't exist.")

    return (tuple(erroneous_keys), config_valid)
