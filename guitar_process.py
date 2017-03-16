import ErrorHandler
import Utilities
import configuration
import timeit
import green_screen as gs
import guitar_rotation
from PIL import Image
import os

# Get all sizes that this image will need
sizes = dict(configuration.config.items('sizes'))

# Get the max and min rotation angles from the configuration file
min_angle = configuration.getint("rotation", "rotation_min_angle")
max_angle = configuration.getint("rotation", "rotation_max_angle")


def process_guitar(filename):
    try:
        img = Image.open(filename)
    except:
        configuration.log_debug_out(configuration.inspect.stack()[0][3], "Could not find image at path {0}".format(filename))
        ErrorHandler.sys_exit(configuration.EXIT_STATUS.FILE_NOT_FOUND)

    # Fix rotation angle if we think it's landscape
    if img.size[:2][0] > img.size[:2][1]:
        img = img.rotate(90, expand=True)

    save_path = "{0}/{1}".format(configuration.get("guitar", "save_base_dir"), filename.split('/')[-1])
    img.save(save_path)

    # Process the guitar
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Processing {0}".format(filename))
    background = Utilities.get_background_from_image(img)
    image = gs.green_screen_removal_2015(image=img, background=background)
    watermark_image = add_watermark(image=image, image_type="guitar")
    make_guitar_images(image=watermark_image, filename=filename)


def make_guitar_images(image, filename, outbox=configuration.get("outbox", "outbox1")):
    # Log start time and start internal timer for this method
    configuration.logging.info("Starting image thumbnails for {0}".format(image))
    start = timeit.default_timer()

    try:
        guitar_model, guitar_serial, guitar_shot, color = filename.split('/')[-1].split('--')
    except:
        guitar_model, guitar_serial, guitar_shot = filename.split('/')[-1].split('--')
    file_type = filename.split('.')[-1]
    base_dir = "{0}/{1}/{2}/{3}".format(outbox, guitar_model[0], guitar_model, guitar_serial)

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    image.save("{0}/{1}--{2}.{3}".format(base_dir, guitar_serial, guitar_shot, file_type))

    # Loop through each size
    for s in sizes.keys():
        si = sizes[s].split('x')
        size = (int(si[0]), int(si[1]))
        configuration.log_debug_out(configuration.inspect.stack()[0][3], "Resizing to {0}".format(size))
        configuration.log_debug_out(configuration.inspect.stack()[0][3], "{0} = {1}".format(s, size))
        img = image.copy()
        if s == "transparent" and guitar_shot in configuration.get("transparent", 'transparent_shots').split(','):
            img = make_transparent(filename)
        elif s == "landscape":
            img = img.rotate(-90, expand=True)
            height = img.size[0]
            width = img.size[1]

            half_the_width = width / 2
            half_the_height = height / 2

            to_remove = -(height / 2 - width)

            img = img.crop(
                (
                    half_the_height - half_the_height,
                    half_the_width - ((width - to_remove) / 2),
                    half_the_height + half_the_height,
                    half_the_width + ((width - to_remove) / 2)
                )
            )

        # Thumbnail using antialias instead of bicubic
        img.thumbnail(size, Image.ANTIALIAS)

        # Save image with image previous image file type
        configuration.log_debug_out(configuration.inspect.stack()[0][3], "Uploading non-transparent shot")
        save_path = "{0}/{1}-{2}-{3}.{4}".format(base_dir, guitar_serial, guitar_shot, s, "jpg")
        configuration.log_debug_out(configuration.inspect.stack()[0][3], "Saving to {0}".format(save_path))

        img.save(save_path)

        configuration.log_debug_out(configuration.inspect.stack()[0][3], "Uploading {0} with size {1}".format(filename, s))

    # Stop the timer and log time taken for this method
    stop = timeit.default_timer()
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "It took {0} seconds to thumbnail the image".format(stop - start))


def add_watermark(image, image_type, watermark=configuration.get("watermark", "basic_watermark_path")):
    # Open image and get height and width
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Image size = {0}".format(image.size))

    # If this is a guitar we want it to be portrait
    if image_type == "guitar":
        # And it's length is greater than the width we add an EXIFTAG for rotation so that it shows with the correct orientation
        if image.size[:2][0] > image.size[:2][1]:
            configuration.log_debug_out(configuration.inspect.stack()[0][3], "Rotating image for watermark")
            image = image.rotate(90, expand=True)
    img_width, img_height = image.size
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Image size before = {0}".format(image.size))

    # Get watermark info
    watermark_image = Image.open(watermark)
    watermark_width, watermark_height = watermark_image.size

    scale = configuration.getfloat("watermark", "watermark_scale")
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Resizing watermark for guitar gallery")
    new_size = int(scale * watermark_width), int(scale * watermark_height)

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "new_size = {0}".format(new_size))
    watermark_image = watermark_image.resize(new_size, Image.ANTIALIAS)
    watermark_height, watermark_width = watermark_image.size

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "watermark_image.size = {0}".format(watermark_image.size))
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Watermark height = {0}, nWatermark Width = {1}".format(watermark_height, watermark_width))

    # Paste the watermark at the y value
    # The x value comes from half the watermark width being subtracted from half the width of the image
    # This centers the watermark on the image
    # image.paste(watermark_image, (int((img_height / 2) - (watermark_width / 2)), int(img_width - int(watermark_height / 3.0))), watermark_image)
    # Paste (x, y)
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "(int((float(img_width) / 2) - (float(watermark_width))), int(img_height + (1.5 * watermark_height))) = {0}".format((int((float(img_width) / 2) - (float(watermark_width))), int(img_height - (1.5 * watermark_height)))))
    # image.paste(watermark_image, (int((float(img_width) / 2) - (float(watermark_width))), int(img_height + (1.5 * watermark_height))), watermark_image)
    # image.size = (4480, 6820)
    # watermark_image.size = (467, 112)
    # (4480/2) - (467/2) = 2007
    # 6820 - 112 - 10 = 6698
    # The 10 is for a padding on the bottom of the image
    # image.paste(watermark_image,  (2007, image.size[1] - watermark_image.size[1] - 10), watermark_image)
    image.paste(watermark_image, (int((image.size[0] / 2.0) - (watermark_image.size[0] / 2.0)), image.size[1] - watermark_image.size[1] - 10), watermark_image)

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Image size after adding watermark {0}".format(image.size))

    return image


def replace_background(img, replacement, green_offset=configuration.getint("green_screen", "offset")):
    # Start internal function timer
    start = timeit.default_timer()
    # configuration.log_debug_out(configuration.inspect.stack()[0][3], "Opening {0}".format(filename))
    if isinstance(img, str):
        image = Image.open(img)
    else:
        image = img
    image = image.convert("RGBA")

    if image.size[:2][0] > image.size[:2][1]:
        image = image.rotate(90, expand=True)

    # Open the image and load the pixels
    # img = Image.open(filename)
    # img = img.convert("RGBA")
    pixdata = image.load()

    # if len(gs.green_pixels) > 0:
    if False:
        for (x, y) in gs.green_pixels:
            try:
                pixdata[x, y] = replacement
            except:
                pass
    else:
        # Replace all known green screen values with transparent values (0, 0, 0)
        for y in xrange(image.size[1]):
            for x in xrange(image.size[0]):
                try:
                    r, g, b, a = pixdata[x, y]
                except:
                    r, g, b = pixdata[x, y]

                # This is based off of the 2015 green screen removal code from Joe Lester
                # Calculate the non green max and the threshold from the offset
                non_green_max = max(r, b)
                green_threshold = (non_green_max + green_offset)

                # If the green pixel is greater than the threshold we make it transparent (0, 0, 0, 0)
                if g > green_threshold:
                    pixdata[x, y] = replacement

    # # Save the image
    # saved_path = Utilities.save_image(filename=filename, img=img, outbox=outbox, image_type=image_type)

    # Stop the internal function timer and log it
    stop = timeit.default_timer()

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "It took {0} seconds to replace greenscreen".format(stop - start))

    # Return the new image
    return image


# Makes photo transparent
def make_transparent(image, green_offset=configuration.getint("green_screen", "offset")):
    return replace_background(img=image, replacement=(255, 255, 255, 0), green_offset=green_offset)


def make_white_background(image, green_offset=configuration.getint("green_screen", "offset")):
    return replace_background(img=image, replacement=(255, 255, 255, 1), green_offset=green_offset)
