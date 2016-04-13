"""Profile lines."""

import argparse

import numpy as np
import skimage.morphology

from jicbioimage.core.image import Image
from jicbioimage.core.transform import transformation
from jicbioimage.segment import connected_components

@transformation
def convert_to_grayscale(rgb_image):

    return rgb_image[:,:,0]

@transformation
def convert_to_signal(line_image):
    """Convert RGB line_image into binary image where True denotes signal."""

    grayscale_image = convert_to_grayscale(line_image)
    inverted = 255 - grayscale_image

    return inverted > 0

@transformation
def skeletonize(image):
    return skimage.morphology.skeletonize(image)

def convert_to_1d(image):
    """Return 1d array derived from data in input grayscale image."""

    # Derive via projection
    return np.amax(image, axis=1)

def line_profile_from_image_and_region(data_image, line_region):
    """Return 1d profile derived by sampling data_image from the True elements
    of line_region."""

    masked_data = np.multiply(data_image, line_region)
    line_profile = convert_to_1d(masked_data)

    return line_profile

def save_line_profile(filename, line_profile):

    line_strings = ["{},{}".format(str(t), str(d)) 
        for t, d in list(enumerate(line_profile))]

    with open(filename, 'w') as f:
        f.write('time,intensity\n')
        f.write('\n'.join(line_strings))

def segment(line_image):
    lines = convert_to_signal(line_image)
    lines = skeletonize(lines)
    segmentation = connected_components(lines, background=0)
    return segmentation

def yield_line_masks(segmented_lines):
    for i in segmented_lines.identifiers:
        region = segmented_lines.region_by_identifier(i)
        yield region

def sample_image_from_lines(image_file, lines_file):

    data_image = Image.from_file(image_file)
    line_image = Image.from_file(lines_file)

    segmented_lines = segment(line_image)

    for n, line_region in enumerate(yield_line_masks(segmented_lines)):
        line_profile = line_profile_from_image_and_region(data_image, line_region)
        filename = "series_{}.csv".format(n)
        save_line_profile(filename, line_profile)

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('kymograph_file', help='Image containing kymograph')
    parser.add_argument('line_file', help='Iamge containing lines')

    args = parser.parse_args()

    sample_image_from_lines(args.kymograph_file, args.line_file)

if __name__ == '__main__':
    main()
