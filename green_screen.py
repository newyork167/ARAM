#!/usr/bin/env python
import timeit
import Utilities
import configuration
import math
from PIL import Image

# Get configuration values
GREEN_SCREEN_TESTING = configuration.getboolean("testing", "green_screen_testing")

green_pixels = []


def _ycc(r, g, b):  # in (0,255) range
    y = .299 * r + .587 * g + .114 * b
    cb = 128 - .168736 * r - .331364 * g + .5 * b
    cr = 128 + .5 * r - .418688 * g - .081312 * b
    return int(y), int(cb), int(cr)


def _rgb(y, cb, cr):
    r = y + 1.402 * (cr - 128)
    g = y - .34414 * (cb - 128) - .71414 * (cr - 128)
    b = y + 1.772 * (cb - 128)
    return int(r), int(g), int(b)


def green_screen_removal_2015(image, background=Image.open(configuration.get_wd("green_screen", "background")), green_offset=int(configuration.get("green_screen", "offset"))):
    if not configuration.getboolean("green_screen", "remove_green_screen"):
        return image

    # Start the internal function timer
    start = timeit.default_timer()

    # Open the image and background image and get the pixel data from each
    img = image
    img = img.convert("RGBA")
    bg_img = background
    bg_img = bg_img.convert("RGBA")
    pixdata = img.load()
    bg_pixdata = bg_img.load()

    should_check_alpha = pixdata[0, 0][3] == 0

    # if img.size[:2][0] > img.size[:2][1]:
    #     img = img.rotate(90, expand=True)
    #     pixdata = img.load()

    # Replace all known green screen values
    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            try:
                # Get the RGBA values from each pixel
                r, g, b, a = pixdata[x, y]

                # Calculate which value is highest
                non_green_max = max(r, b)

                # Determine the green threshold from the difference of the green offset from the non green max
                green_threshold = (non_green_max + green_offset)

                # If the green value in this pixel meets our conditions replace it with the background
                if should_check_alpha:
                    if a == 0:
                        pixdata[x, y] = bg_pixdata[x, y]
                        green_pixels.append([x, y])
                elif g > green_threshold:
                    pixdata[x, y] = bg_pixdata[x, y]
                    green_pixels.append([x, y])
            except:
                configuration.log_debug_out(configuration.inspect.stack()[0][3], "(x,y) = {0}".format((x, y)))

    # Save the image
    # saved_path = Utilities.save_image(filename=filename, img=img, outbox=outbox, image_type=image_type)

    # Stop and log the internal function time
    stop = timeit.default_timer()

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "It took {0} seconds to remove greenscreen".format(stop - start))
    return img


def green_screen_y_cb_cr(filename, image_type, background, path="", rgb_key=(80,200,100), outbox=configuration.get("outbox", "outbox1")):
    # Start the internal function timer
    start = timeit.default_timer()
    configuration.logging.debug("Opening {0} in green_screen_y_cb_cr".format(filename))

    # Open the image and background image and load the pixel data
    img = Image.open(path + filename)
    img = img.convert("RGB")
    bg_img = Image.open(background)
    bg_img = bg_img.convert("RGB")
    pixdata = img.load()
    bg_pixdata = bg_img.load()

    # Get the YCbCr values from the RGB key and set the tolerance
    # y_key, cb_key, cr_key = _ycc(0, 255, 0)
    r_key = rgb_key[0]
    g_key = rgb_key[1]
    b_key = rgb_key[2]
    cb_key = _ycc(r_key, g_key, b_key)[1]
    cr_key = _ycc(r_key, g_key, b_key)[2]
    tola, tolb = configuration.get("green_screen", "tolerance_high"), configuration.get("green_screen", "tolerance_low")

    # Replace all known green screen values
    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            # Get the RGB value and convert to YCbCr
            r, g, b = pixdata[x, y]
            y_p, cb_p, cr_p = _ycc(r, g, b)

            # Calculate the mask based on the key color differences and tolerances
            mask = colorclose(Cb_p=cb_p, Cr_p=cr_p, Cb_key=cb_key, Cr_key=cr_key, tola=tola, tolb=tolb)
            mask = 1.0 - mask

            # Get the background RGB value
            r_bg, g_bg, b_bg = bg_pixdata[x, y]

            # Calculate the portion of the background image that we will take based on the mask created earlier
            r = int(max(r - mask * r_key, 0) + mask * r_bg)
            g = int(max(g - mask * g_key, 0) + mask * g_bg)
            b = int(max(b - mask * b_key, 0) + mask * b_bg)

            # Set the pixel data to this calculation
            pixdata[x, y] = (r, g, b)

    # Save the image
    saved_path = Utilities.save_image(filename=filename, img=img, outbox=outbox, image_type=image_type)

    # Stop the internal function timer and log it
    stop = timeit.default_timer()

    configuration.logging.debug("It took {0} seconds to remove greenscreen with y/cb/cr".format(stop - start))
    return saved_path


# Determines how close the color is to the key value biased with given tolerances
def colorclose(Cb_p, Cr_p, Cb_key, Cr_key, tola, tolb):
    # Sqrt((Cb_Key - Cb_p) ^ 2 + (Cr_Key - Cr_p) ^ 2))
    temp = math.sqrt((Cb_key - Cb_p) ** 2 + (Cr_key - Cr_p) ** 2)
    if temp < tola:
        return 0.0
    elif temp < tolb:
        return (temp - tola) / (tolb - tola)
    else:
        return 1.0
