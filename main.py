# import Image
import argparse
import os
import sys
import timeit
import ErrorHandler
import Utilities
import cases
import guitar_process
import configuration
from PIL import Image

# Get the supported filetypes from the configuration file
guitar_supported_filetypes = configuration.get("supported_filetypes", "guitar_image_types").split(',')


# Function for sanity checks
def sanity_check():
    # If we are logging - check if the logs directory exists
    if configuration.getboolean("logging", "enabled"):
        logs_path = configuration.get_wd("logging", "directory")
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)


def test_method(**kwargs):
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Entering test method")
    return


# Determine if the file extension is valid
def check_file_extension(filename, image_type):
    filetype = filename.lower().split('.')[-1]

    if image_type in ["guitar", "case"]:
        if filetype not in guitar_supported_filetypes:
            configuration.log_debug_out(configuration.inspect.stack()[0][3], "Rejecting bad guitar/case {0} with bad file extension".format(filename))
            ErrorHandler.reject_image(filename=filename)
            ErrorHandler.sys_exit(configuration.EXIT_STATUS.BAD_FILE_EXTENSION)
    else:
        configuration.log_debug_out(configuration.inspect.stack()[0][3], "Unknown type")
        ErrorHandler.sys_exit(configuration.EXIT_STATUS.BAD_TYPE)


# Handle which image path to process
def process_image(filename, image_type):
    # Check for a valid file extension
    check_file_extension(filename=filename, image_type=image_type)

    # Start internal function timer
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Processing {0}{1}".format(filename, "-" * (150 - len("Processing {0}".format(filename)))))
    start = timeit.default_timer()

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Processing image type: {0}".format(image_type))

    # Handle the image type accordingly
    if image_type == "case":
        if "case3" in filename:
            configuration.log_debug_out(configuration.inspect.stack()[0][3], "ENTERING CASE MODE")
            cases.process_cases(filename=filename)
        else:
            configuration.logging.warn("Waiting for third case file to process cases")
            ErrorHandler.sys_exit(configuration.EXIT_STATUS.WAITING_FOR_CASES)
    elif image_type == "guitar":
        configuration.log_debug_out(configuration.inspect.stack()[0][3], "ENTERING GUITAR MODE")
        guitar_process.process_guitar(filename=filename)
    else:
        configuration.log_debug_out(configuration.inspect.stack()[0][3], "Could not determine image type")
        ErrorHandler.sys_exit(configuration.EXIT_STATUS.BAD_TYPE)

    # Stop internal function timer and log the info
    stop = timeit.default_timer()

    # If we are not testing we want to remove the source image
    if not configuration.TESTING:
        try:
            os.remove(filename)
        except:
            configuration.log_debug_out(configuration.inspect.stack()[0][3], "Failed to remove file {0}".format(filename))

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "It took {0} seconds to process image{1}\n".format(stop - start, "-" * (150 - len("It took {0} seconds to process image".format(stop - start)))))


def show_help_and_die(parser):
    parser.print_help()
    ErrorHandler.sys_exit(configuration.EXIT_STATUS.BAD_ARGUMENTS)


# Main method
# TODO: Add argparser since we can pass multiple commands based on the redis queue
if __name__ == '__main__':
    # If there is an argument use that image, otherwise glob all the files in the directory
    # The glob should only be used for testing
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", help="Image Type", type=str)
    parser.add_argument("-p", "--path", help="Image Path", type=str)
    parser.add_argument("-v", "--verbose", help="Increase output verbosity - Warning", action="store_true")
    parser.add_argument("-vv", "--very_verbose", help="Increase output verbosity - Debug", action="store_true")
    parser.add_argument("--testing", help="Turn on testing features", action="store_true")
    args = parser.parse_args()

    # Perform a sanity check on the filesystem
    sanity_check()

    # Check if we are testing
    if args.testing or configuration.TESTING:
        test_method(image=sys.argv[1] if len(sys.argv) > 1 else None)

    # If the two necessary arguments are missing show usage and exit
    if Utilities.string_is_none_or_empty(args.path):
        show_help_and_die(parser=parser)

    # Do not process the image if we do not know the type
    if Utilities.string_is_none_or_empty(args.type):
        configuration.log_debug_out(configuration.inspect.stack()[0][3], "Bad file type")
        ErrorHandler.sys_exit(configuration.EXIT_STATUS.BAD_TYPE)
    else:
        image_type = args.type

    # Set the log verbosity
    if args.verbose is not None:
        configuration.logging.basicConfig(stream=sys.stderr, level=configuration.logging.WARNING)
    if args.very_verbose is not None:
        configuration.logging.basicConfig(stream=sys.stderr, level=configuration.logging.DEBUG)

    # Attempt to open a log file, will fail if there are incorrect permissions on the output folder
    try:
        if configuration.getboolean("logging", "enabled"):
            configuration.log_file = open("{0}logs/{1}.log".format(configuration.working_directory, args.path.split("/")[-1]), 'w+')
    except:
        configuration.log_debug_out(configuration.inspect.stack()[0][3], "Could not open log file for writing")

    # Process the image
    process_image(filename=args.path, image_type=image_type)
