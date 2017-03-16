import sys
import Utilities
import configuration
import os


# Define Exit Status Variables
class EXIT_STATUS():
    CASE_UPLOAD_FAILED = 20
    FILE_NOT_FOUND = 19
    BAD_FILE_EXTENSION = 17
    BAD_TYPE = 13
    WAITING_FOR_CASES = 12
    BAD_ARGUMENTS = 11
    TESTING = 100
    OK = 0


def reject_image(filename):
    # Get the rejection path from the configuration file
    rejection_path = configuration.get("image_rejection", "rejection_url") + filename

    # Move the file to the rejection path
    os.rename(filename, rejection_path)

    # If we could not move the file successfully send an email so that this gets taken care of
    # Ultimately the file should be removed from the queue so this will need to be manually checked
    if not os.path.exists(rejection_path):
        Utilities.send_email(email_from=configuration.get("image_rejection", "move_fail_email_from"),
                             email_to=configuration.get("image_rejection", "move_fail_email_to"),
                             email_subject=configuration.get("image_rejection", "move_fail_email_subject"),
                             email_body="Failed to move {0} to {1}".format(filename, rejection_path))
    # Send an email about the failure - Currently this only applies to file extensions that we don't support
    Utilities.send_email(email_from=configuration.get("image_rejection", "type_reject_email_from"),
                         email_to=configuration.get("image_rejection", "type_reject_email_to"),
                         email_subject=configuration.get("image_rejection", "type_reject_email_subject"),
                         email_body="Check file: {0}".format(filename))


# Handle system exit codes
def sys_exit(exit_code):
    if exit_code == EXIT_STATUS.BAD_ARGUMENTS:
        pass
    elif exit_code == EXIT_STATUS.BAD_FILE_EXTENSION:
        pass
    elif exit_code == EXIT_STATUS.BAD_TYPE:
        pass
    elif exit_code == EXIT_STATUS.FILE_NOT_FOUND:
        pass
    elif exit_code == EXIT_STATUS.TESTING:
        pass
    elif exit_code == EXIT_STATUS.WAITING_FOR_CASES:
        pass
    sys.exit(exit_code)
