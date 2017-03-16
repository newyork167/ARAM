import cv2
import numpy as np
from math import *
from scipy import ndimage
import configuration


# Get the min and max angle for rotation
min_angle = configuration.getint("rotation", "rotation_min_angle")
max_angle = configuration.getint("rotation", "rotation_max_angle")


# Helper method for rotating an image with OpenCV2
def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape)[:2] / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[:2], flags=cv2.INTER_LINEAR)
    return result


# Truncate the angle to the first quadrant
def angle_trunc(a):
    while a < 0.0:
        a += pi * 2
    return a


# Helper method to determine the angle between two points
def get_angle_between_points(x_orig, y_orig, x_landmark, y_landmark):
    deltaY = y_landmark - y_orig
    deltaX = x_landmark - x_orig
    return angle_trunc(atan2(deltaY, deltaX))


# Calculate the rotation angle
# Detects the borders of the guitar and takes the most common orientation
def get_rotation_angle(file):
    img = cv2.imread(file).copy()
    im_height, im_width = img.shape[:2]

    # If the photo is rotated
    if im_width > im_height:
        # img = rotate_image(img, 90)
        img = ndimage.rotate(img, 90)

    # Convert the image to gray to help with edge detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Check if we have found an angle
    angle_found = False
    angles = []
    angle_to_rotate = 0

    # Calculate the hough lines from the image
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    # Loop throgh the found lines in the image
    for rho, theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * a)
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * a)

        # Calculate the angle beteen two points on the line
        angle_to_rotate = get_angle_between_points(x1, y1, x2, y2)

        # If the angle is greater than pi restrict it to the first half
        if angle_to_rotate > pi:
            angle_to_rotate = pi - angle_to_rotate
        # Else if the angle is less than pi bring it back to the upper half
        elif angle_to_rotate < pi:
            angle_to_rotate = pi + angle_to_rotate

        # Add this angle to the list of angles
        angles.append(get_angle_between_points(x1, y1, x2, y2))

        # DEBUG -- If we haven't found an angle force it true
        if not angle_found or angle_to_rotate > angle_found:
            angle_found = angle_to_rotate
            angle_found = True
            # print("New angle_to_rotate: {0}".format(angle_to_rotate))
        # print("Angle of line: {0}".format(angle_to_rotate))

        # For debugging add the calculate line to the image
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    # Determine the average angle from the max of the set
    angles_mode = max(set(angles), key=angles.count)

    # print "Average Angle: {0}".format(sum(angles)/len(angles))
    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Mode of angles: {0}".format(angles_mode))

    # Restrict the angle to the first quadrant
    final_angle_to_rotate = (pi/2) - angles_mode
    final_angle_to_rotate = angles_mode

    configuration.log_debug_out(configuration.inspect.stack()[0][3], "Final angle_to_rotate: {0}".format(final_angle_to_rotate))
    # cv2.imwrite(file + '_houghlines.jpg', img)
    # If the rotation angle falls within the min and max angles write the rotated file
    # if min_angle < final_angle_to_rotate < max_angle:
    #     cv2.imwrite(file + '_original.png', cv2.imread(file).copy())

    # img2 = cv2.imread(file + '_original.png', 0)
    # rotated = ndimage.rotate(img2, degrees(final_angle_to_rotate))
    # cv2.imwrite(file + '_rotated.png', rotated)
    configuration.log_debug_out(configuration.inspect.stack()[0][3], final_angle_to_rotate)
    return final_angle_to_rotate
