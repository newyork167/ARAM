from PIL import Image, ImageFilter
import timeit
import configuration


def load_files():
    image_path = configuration.get("testing", "inbox")
    # test_green_screen_removal(image_path)
    test_green_screen_removal2(image_path)


def test_green_screen_removal(img):
    # parse through file list in the current directory
    start = timeit.default_timer()
    img = img.convert("RGBA")
    pixdata = img.load()

    red_threshold = 110
    green_threshold = 112
    blue_threshold = 120
    blue_green_diff_threshold = 50
    red_green_diff_threshold = 50

    # Replace all known green screen values
    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            # Initialize variables
            r1 = r2 = g1 = g2 = b1 = b2 = a1 = a2 = None
            # Get current pixel
            r, g, b, a = img.getpixel((x, y))
            # Get next pixel
            if x < img.size[0] and y + 1 < img.size[1]:
                r2, g2, b2, a2 = img.getpixel((x, y+1))

            # if ((r <= red_threshold) and (g > green_threshold) and (b < blue_threshold) and (b < g) and (r < g)) \
            #         or (g - b > blue_green_diff_threshold and r <= 150 and g >= 100):
            # if (g - b > blue_green_diff_threshold and r <= 150 and g >= 100):
            if ((g - b) > blue_green_diff_threshold and (g - r) > red_green_diff_threshold and g >= 100) or ((r <= red_threshold) and (g > green_threshold) and (b < blue_threshold)):
                set_pix_data = True
                if g2 is not None:
                    if not (r2 <= red_threshold) and (g2 > green_threshold) and (b2 < blue_threshold) and (b2 < g2) and (r2 < g2):
                        set_pix_data = False
                if set_pix_data:
                    pixdata[x, y] = (255, 255, 255, 0)
                else:
                    pixdata[x, y] = (r2, g2, b2, a2)
                # Remove anti-aliasing outline of body.
            elif r == 0 and g == 0 and b == 0:
                pixdata[x, y] = (255, 255, 255, 0)

    img2 = img.filter(ImageFilter.GaussianBlur(radius=1))
    img2.save(configuration.get("outbox", "test_outbox"), "PNG")
    stop = timeit.default_timer()

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "It took {0} seconds".format(stop - start))
    # sys.exit(-1)


def test_green_screen_removal2(img):
    # parse through file list in the current directory
    start = timeit.default_timer()
    img = img.convert("RGBA")
    pixdata = img.load()

    green_offset = 39

    # Replace all known green screen values
    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            r, g, b, a = img.getpixel((x, y))
            non_green_max = r if r > b else b
            green_threshold = (non_green_max + green_offset)

            # if ((r <= 110) and (g > 112) and (b < 120) and (b < g)) \
            #         or (g - b > 50 and r <= 110 and g >= 100):
            if g > green_threshold:
                pixdata[x, y] = (255, 255, 255, 0)
                # Remove anti-aliasing outline of body.
            elif r == 0 and g == 0 and b == 0:
                pixdata[x, y] = (255, 255, 255, 0)

    img2 = img.filter(ImageFilter.GaussianBlur(radius=1))
    img2.save(configuration.get("outbox", "test_outbox"), "PNG")
    stop = timeit.default_timer()

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "It took {0} seconds".format(stop - start))
    # sys.exit(-1)
