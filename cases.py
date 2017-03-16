import ftplib
import numpy as np
from os import listdir
from os.path import isfile, join
import ErrorHandler
import class_variables
import green_screen as gs
from PIL import Image
import Utilities
import configuration
import os


# Case height method that is calculated by adding one-third the size of each case file
def get_case_height2(case):
    # gs.green_screen_y_cb_cr(case, background=Utilities.get_background(case))
    # Open and conver to RGBA
    img = Image.open(case)
    img = img.convert("RGBA")

    # Replace the green screen in the case image
    case = gs.green_screen_removal_2015(img,
                                        background=Utilities.get_background_from_image(img),
                                        green_offset=30)
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Case size: x = {0}, y = {1}".format(img.size[0], img.size[1]))

    # Get the height and width of the image
    width = img.size[0]
    height = img.size[1]

    # Calculate the height based on one-third of the image height
    y = int(height*0.333333)

    # Return the width of the image, the calculated height, and the cropped image
    return width, y, case.crop((0, y, width, height))


# Get the case height based on finding the first non green line - Uses mostly the same algorithm from the YCbCr green screen removal
# This should theoretically get better pictures as it will always include the full case in the photo
def get_case_height(case, green_offset=configuration.get("green_screen", "offset"), height_offset=10):
    # DEBUG - Just use the one-third
    return get_case_height2(case=case)

    # Open the image and load the pixel data
    img = Image.open(case)
    img = img.convert("RGBA")
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Case size: x = {0}, y = {1}".format(img.size[0], img.size[1]))
    pixdata = img.load()
    img_np = np.array(img)
    width = img.size[0]
    height = img.size[1]

    # Check for green values using the old imageengine (2015) code for speed
    for y in xrange(height):
        for x in xrange(width):
            # Get the RGBA values from the pixel
            r, g, b, a = pixdata[x, y]

            # Calculate the non green max and the green threshold
            non_green_max = max(r, b)
            green_threshold = (non_green_max + green_offset)

            # If the green pixel is below the threshold
            if g < green_threshold:
                configuration.log_debug_out(configuration.inspect.stack()[0][3], "Found first non green line at y: {0}".format(y))

                # Start at x = 0, y = height - offset and grab all of the x values and the corrected remaining height
                configuration.log_debug_out(configuration.inspect.stack()[0][3], "Cropping {0} to box {1}".format(case, (0, y - height_offset, img.size[0], img.size[1] - y + height_offset)))

                # Return the width, the calculated y component, and the cropped image
                return width, y, img.crop((0, height - y, width, height))
    return 0


# Function for processing and building the full case photo
def process_cases(filename, outbox=configuration.get("outbox", "outbox1")):
    directory = "/".join(filename.split('/')[:-1])
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Searching for cases in {0}".format(directory))

    # Determine the case prefix and only grab case files that are for this guitar
    case_prefix = "--".join(filename.split('/')[-1].split('--')[:-1])
    onlyfiles = [x for x in [f for f in listdir(directory) if isfile(join(directory, f))] if "case" in x and "_new_image" not in x and case_prefix in x]

    # Initialize variables
    case_data = {}
    total_case_height = 0
    max_case_width = 0
    paste_y = 0

    guitar_model, guitar_serial, guitar_shot = filename.split('/')[-1].split('--')
    file_type = guitar_shot.split('.')[-1]

    # Loop through all the files that we found earlier
    for case_file in onlyfiles:
        configuration.log_debug_out(configuration.inspect.stack()[0][3], "Found {0}".format(case_file))
        # case_size = get_case_height(directory + case_file)

        # Get the case height
        case_size = get_case_height("{0}/{1}".format(directory, case_file))

        # Add this to the total case height
        total_case_height += case_size[2].size[1]

        # Check for the largest photo width
        # May cause stretching of smaller images if they decide to shoot different file sizes for some reason
        if max_case_width < case_size[0]:
            max_case_width = case_size[0]

        # Add the cropped image to the case data dict
        case_data[case_file] = case_size[2]
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Total case image width = {0}, height = {1}".format(max_case_width, total_case_height))
    # Image.fromarray(data, 'RGB')

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Creating image of size ({0}, {1})".format(max_case_width, total_case_height))
    im_new = Image.new("RGBA", (max_case_width, total_case_height))

    # Loop through the sorted case keys
    for key in sorted(case_data.keys()):
        # Paste the image at y
        configuration.log_debug_out(configuration.inspect.stack()[0][3], paste_y)
        im_new.paste(case_data[key], (0, paste_y))
        configuration.log_debug_out(configuration.inspect.stack()[0][3], case_data[key])
        configuration.log_debug_out(configuration.inspect.stack()[0][3], case_data[key].size)

        # Increment y by the y size of the photo
        paste_y += case_data[key].size[1]

    # Build the save path from the name, serial and shot type (In this case it is a case)
    save_path = "{0}/{1}--case.{2}".format(outbox, guitar_serial, file_type)
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Saving case composite to {0}".format(save_path))

    # Save the image to the save path
    im_new.save(save_path)
