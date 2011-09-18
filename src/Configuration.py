__author__ = "Julien Gilli <jgilli@nerim.fr>,\
Julien Barbot <julien.barbot@laposte.net>"
__version__ = "0.0"
__date__ = "21 August 2002"

"""This module is used to get the configuration information from
the configuration file.
It also checks the information contained in this file before
using it, so the user can see configuration errors before
they really happen."""

import grp
import stat
import ConfigParser
import pwd
import os
import sys
import getopt
import commands
import Protocol
import syslog


# this list of tuples match the dictionnary keys
# used throughout all the program by developpers and
# configuration file's keys. It's intended to change
# only this list of tuples whenever the configuration file
# changes. The dictionnary key is the first element of every tuples,
# and the config file key is the third. The second is the
# section to which the config key belongs.


CONFIG_FILE_PATH="/etc/dms.cfg"

def get_configuration(display_usage_func,\
                      check_values_func,\
                      configuration_keys_match,\
                      configuration_default_values,\
                      command_line_options,\
                      config_file_path=CONFIG_FILE_PATH,
                      use_command_line=1):
    """Return a dictionnary whose keys are configuration settings
    and values are the ones contained in the configuration file
    passed as config_file_path parameter.
    - display_usage_func is a function that displays the online help;
    - check_values_func is a function that takes one parameter which is
    a dictionnary containing all the configuration values and tells wether
    they are correct or not;
    - configuration keys match associate a key-value pair of the configuration
    dictionnary to a value and section in the configuration file;
    - configuration_default_values is a dictionnary which contains default
    configuration values;
    - command line options associates a set of command line options with a
    configuration dictionnary key.
    """

    config_dictionnary = configuration_default_values.copy()

    if use_command_line:
        #check if the -f option has been set and set the config_file_path to
        #its command line value
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:", [])
            for o, opt_val in opts:
                if o == "-f":
                    config_file_path = opt_val
        except getopt.GetoptError:
            pass

    # parse config file
    try:
        config_file = open(config_file_path)
        config = ConfigParser.ConfigParser()
        config.readfp(config_file)
    
        for (dict_key, section, config_file_key) in configuration_keys_match:
            try:
                config_dictionnary[dict_key] = config.get(section, config_file_key)
            except ConfigParser.NoSectionError, msg:
                print >> sys.stderr, "A section is missing in the configuration file: "\
                      + str(msg)
        
            except ConfigParser.NoOptionError, msg:
                print >> sys.stderr,  "An option is missing in the configuration file: "\
                      + str(msg)
            
            except ConfigParser.ParsingError, msg:
                print >> sys.stderr,  "Parse error reading configuration file : "\
                      + str(msg)
            
            except :
                print >> sys.stderr,  "Unknown error in configuration file."
    except IOError:
        print >> sys.stderr, "Warning : File " + config_file_path + \
              " doesn't exist, using default"            
        
    check_result = check_values_func(config_dictionnary)
    if check_result[1] == 0:
        syslog.syslog(syslog.LOG_WARNING | syslog.LOG_DAEMON, \
                      "Bad config file, using default configuration.")
        print >> sys.stderr, "Encountered errors in config file, replacing values."

        for erroneous_config_key in check_result[0]:
            print >> sys.stderr, "Replacing " + erroneous_config_key + " by " + configuration_default_values[erroneous_config_key]
            config_dictionnary[erroneous_config_key] = configuration_default_values[erroneous_config_key]
            
    if use_command_line:
        # parse command line
        short_options = "f:"
        long_options = []

        for (short, long, type, key) in command_line_options:
            if short != None:
                if type == 0:
                    # expect a value
                    short_options += short[1] + ':'
                else:
                    short_options += short[1]
            if long != None:
                if type == 0:
                    # expect a value
                    long_options.append(long[2:] + '=')
                else:
                    long_options.append(long[2:])
        print "Short options : " + short_options
        print "Long options : " + str(long_options)
        try:
            opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
        except getopt.GetoptError:
            display_usage_func()
            sys.exit(2)

        for option, values in opts:
            for (short, long, type, key) in command_line_options:
                if option in (short, long):
                    if type == 0:
                        config_dictionnary[key] = values
                else:
                    config_dictionnary[key] = 1
    return config_dictionnary
