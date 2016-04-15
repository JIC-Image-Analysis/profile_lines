"""Profile lines."""

import argparse
from collections import namedtuple

import numpy as np
import skimage.morphology

from jicbioimage.core.image import Image
from jicbioimage.core.transform import transformation
from jicbioimage.segment import connected_components
from jicbioimage.transform import dilate_binary, remove_small_objects

Datum = namedtuple("datum", "time, intensity, series")


@transformation
def convert_to_grayscale(rgb_image):
    return rgb_image[:, :, 0]


@transformation
def convert_to_signal(line_image):
    """Convert RGB line_image into binary image where True denotes signal."""

    grayscale_image = convert_to_grayscale(line_image)
    inverted = 255 - grayscale_image

    return inverted > 0


@transformation
def skeletonize(image):
    return skimage.morphology.skeletonize(image)


def csv_header():
    return ",".join(Datum._fields) + "\n"


def yield_data(line_profile, series):
    for time, intensity in enumerate(line_profile):
        yield Datum(str(time), str(intensity), str(series))


def csv_lines(line_profile, series):
    return [",".join(d) for d in yield_data(line_profile, series)]


def csv_body(line_profile, series):
    return "\n".join(csv_lines(line_profile, series)) + "\n"


def save_line_profile(filename, line_profile, series):
    with open(filename, 'w') as f:
        f.write(csv_header())
        f.write(csv_body(line_profile, series))


def segment(line_image, dilation):
    lines = convert_to_signal(line_image)
    lines = skeletonize(lines)
    lines = remove_small_objects(lines, min_size=10, connectivity=2)
    lines = dilate_binary(lines, selem=np.ones((1, dilation)))
    segmentation = connected_components(lines, background=0)
    return segmentation


def yield_line_masks(segmented_lines):
    for i in segmented_lines.identifiers:
        region = segmented_lines.region_by_identifier(i)
        yield region


def sample_image_from_lines(image_file, lines_file, dilation, reduce_method):

    data_image = Image.from_file(image_file)
    line_image = Image.from_file(lines_file)

    segmented_lines = segment(line_image, dilation)

    with open("all_series.csv", "w") as fh:
        fh.write(csv_header())
        for n, line_region in enumerate(yield_line_masks(segmented_lines)):
            line_intensity = data_image * line_region
            if reduce_method == "max":
                line_profile = np.amax(line_intensity, axis=1)
            elif reduce_method == "mean":
                sum_intensity = np.sum(line_intensity, axis=1)
                sum_rows = np.sum(line_region, axis=1)
                line_profile = sum_intensity / sum_rows
            else:
                err_msg = "Unknown reduce method: {}".format(reduce_method)
                raise(RuntimeError(err_msg))

            series_filename = "series_{:02d}.csv".format(n)
            save_line_profile(series_filename, line_profile, n)

            fh.write(csv_body(line_profile, n))


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('kymograph_file', help='Image containing kymograph')
    parser.add_argument('line_file', help='Iamge containing lines')
    parser.add_argument('-d', '--dilation', default=2, type=int,
                        help='Dilation of line')
    parser.add_argument('-r', '--reduce-method', default="max",
                        choices=("max", "mean"),
                        help='Method to reduce row to single value')

    args = parser.parse_args()

    sample_image_from_lines(args.kymograph_file, args.line_file,
                            args.dilation, args.reduce_method)

if __name__ == '__main__':
    main()
