import cv2
from PIL import Image
import configuration
from email.mime.text import MIMEText
import smtplib


# OpenCV2 Implementation
def get_background(image, background=None, background_landscape=None):
    # Default to guitar background
    if background is None:
        background = configuration.get_wd("green_screen", "background")
    if background_landscape is None:
        background_landscape = configuration.get_wd("green_screen", "background_land")

    oriimage = cv2.imread(image)
    bg_image = cv2.imread(background)

    # Determine if we need to resize
    im_height, im_width = oriimage.shape[:2]
    bg_height, bg_width = bg_image.shape[:2]

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Image Size")
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "im_height = {0}, im_width = {1}".format(im_height, im_width))

    # Resize to background size
    if bg_height > im_height:
        background = background_landscape
        bg_image = cv2.imread(background)
        bg_height, bg_width = bg_image.shape[:2]

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Using background image at {0}".format(background))
    if bg_height != im_height or bg_width != im_width:
        bg_image = cv2.resize(bg_image, (im_width, im_height))
        cv2.imwrite(background + "_sized.png", bg_image)
        background += "_sized.png"

    bg_height, bg_width = bg_image.shape[:2]

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Background Size")
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "bg_height = {0}, bg_width = {1}".format(bg_height, bg_width))

    return background


# Updated to use Pillow instead of OpenCV2
def get_background_from_image(image, background=None, background_landscape=None):
    if background is None:
        background = configuration.get_wd("green_screen", "background")
    if background_landscape is None:
        background_landscape = configuration.get_wd("green_screen", "background_land")

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Opening background = {bg}".format(bg=background))
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Opening background_landscape = {bg}".format(bg=background_landscape))

    # # Check if we have already created this background and if we have do either of the _sized images match our current images size
    # # If so we can just use this one instead of resizing
    # bg_previous_size = configuration.working_directory + background + "_sized.png"
    # bg_previous_land_size = configuration.working_directory + background_landscape + "_sized.png"
    # if os.path.isfile(bg_previous_size):
    #     bg_image = Image.open(bg_previous_size)
    #     if bg_image.size == image.size:
    #         return bg_image
    #
    # if os.path.isfile(bg_previous_land_size):
    #     bg_image = Image.open(bg_previous_land_size)
    #     if bg_image.size == image.size:
    #         return bg_image

    oriimage = image
    bg_image = Image.open(background)

    # Determine if we need to resize
    im_width, im_height = oriimage.size
    bg_width, bg_height = bg_image.size

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Image Size")
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "im_height = {0}, im_width = {1}".format(im_height, im_width))

    # Resize to background size
    if bg_height > im_height:
        background = background_landscape
        bg_image = Image.open(background)
        bg_width, bg_height = bg_image.size

    if bg_height != im_height or bg_width != im_width:
        configuration.log_debug_out(configuration.inspect.stack()[0][3], "Resizing background")
        bg_image = bg_image.resize((im_width, im_height), Image.BICUBIC)

    bg_height, bg_width = bg_image.size

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Background Size")
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "bg_height = {0}, bg_width = {1}".format(bg_height, bg_width))

    # configuration.log_debug_out(configuration.inspect.stack()[0][3], "Using background image at {0}".format(background))

    return bg_image


# Checks ftp tree for the existence of the path and creates it if necessary
def make_dir_path(session, path):
    dir_path = path.split('/')

    for d in dir_path:
        found = False
        if string_is_none_or_empty(d):
            continue
        filelist = []
        session.retrlines('LIST', filelist.append)
        for f in filelist:
            if f.split()[-1] == d and f.lower().startswith('d'):
                found = True
                break

        if not found:
            session.mkd(d)
        session.cwd(d)


def send_email(email_to, email_from, email_subject, email_body, cc_email=""):
    msg = MIMEText(email_body)

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = email_subject
    msg['From'] = email_from
    msg['To'] = email_to

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(configuration.get("smtp", "relay_address"))
    s.sendmail(email_from, [email_to], msg.as_string())
    s.quit()


def string_is_none_or_empty(self):
    return (self is None) or (self == "")


def add_image_height(img, height):
    # pixdata = img.load()
    # arr = []
    # for x in range(img.size[0]):
    #     row = []
    #     for y in range(img.size[1]):
    #         p = pixdata[x, y]
    #         row.append(p)
    #     arr.append(row)
    #
    # for x in range(height):
    #     arr.append([0] * len(arr[0]))
    # return Image.fromarray(np.array(arr))
    if type(img) == type(str):
        i = Image.open(img)
    else:
        i = img
    img = i.convert('RGBA')
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "img.size = {0}".format(i.size))
    image_width, image_height = i.size
    new_image = Image.new('RGBA', (image_width + height, image_height))
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "new_image.size = {0}".format(new_image.size))
    pixeldata = new_image.load()

    for x in range(image_width):
        for y in range(image_height):
            pixeldata[x, y] = (100, 255, 100, 1)

    new_image.paste(img, (height-1, 0))
    # new_image.save(os.path.expanduser("~/Desktop/bigger_image.jpg"))
    return new_image
