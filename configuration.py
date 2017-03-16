import ConfigParser
import os
import logging, sys
import inspect
import time
from ErrorHandler import EXIT_STATUS

# Get the working directory to open the configuration file
working_directory = "/".join(os.path.realpath(__file__).split('/')[:-1]) + "/"

# Instantiate the ConfigParser object
config = ConfigParser.ConfigParser()

# Read the config file
config.read(working_directory + "config.ini")

log_file = None

TESTING = config.getboolean("testing", "testing")

# Determine the base level of logging that we want
if config.getboolean("testing", "debug_logging_enabled"):
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
else:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)


def log_debug_out(method, l):
    # pprint(inspect.stack())
    if log_file is not None:
        log_file.write("{0}: {1} - {2}\n".format(time.strftime("%d-%m-%Y-%H-%M-%S"), method, l))
        log_file.flush()
    logging.debug("{0} - {1}".format(method, l))


def log_info_out(method, l):
    if log_file is not None:
        log_file.write("{0} - {1}\n".format(method, l))
        log_file.flush()
    logging.info("{0} - {1}".format(method, l))


def get(section, option):
    return config.get(section=section, option=option)


def getboolean(section, option):
    return config.getboolean(section=section, option=option)


def getint(section, option):
    return config.getint(section=section, option=option)


def getfloat(section, option):
    return config.getfloat(section=section, option=option)


def get_wd(section, option):
    return working_directory + config.get(section=section, option=option)
