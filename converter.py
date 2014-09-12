from PIL import Image
import argparse
import sys


def load_image(filename, target_width, target_height):
    """
    Loads an image, resized it to the target dimensions and returns it's data.
    """

    image = Image.open(filename, 'r')
    image = image.resize((target_width, target_height), Image.NEAREST)
    image_data = image.load()

    return image.size[0], image.size[1], image_data


def get_pixel_intensity(pixel, invert=False, max_value=255):
    """
    Gets the average intensity of a pixel.
    """
    intensity = 0

    # Pixel is multi channel
    if type(pixel) is list or type(pixel) is tuple:
        for channel_intensity in pixel:
            intensity += channel_intensity
        intensity /= len(pixel)
    # Pixel is single channel
    elif type(pixel) is int or type(pixel) is float:
        intensity = pixel
    # Pixel is magic
    else:
        raise ValueError('Not a clue what format the pixel data is: ' + str(type(pixel)))

    if invert:
        return max_value - intensity
    else:
        return intensity


def get_average_pixel_intensity(width, height, pixel_data, invert):
    """
    Gets the average intensity over all pixels.
    """

    avg_intensity = 0

    for x in range(0, width):
        for y in range(0, height):
            avg_intensity += get_pixel_intensity(pixel_data[x, y], invert)

    avg_intensity = avg_intensity / (width * height)

    return avg_intensity

def output_image_c_array(width, height, pixel_data, crossover, invert):
    """
    Outputs the data in a C bitmap array format.
    """

    print '{'

    for y in range(0, height):
        next_line = ''
        next_value = 0

        for x in range(0, width):
            if x % 8 == 0 and x > 0:
                next_line += str('0x%0.2X' % next_value).lower() + ","
                next_value = 0

            if get_pixel_intensity(pixel_data[x, y], invert) > crossover:
                next_value += 2 ** (7 - (x % 8))

        print next_line

    print '};'

def convert(args):
    """
    Runs an image conversion.
    """

    width, height, image_data = load_image(args.image, args.width, args.height)
    crossover_intensity = get_average_pixel_intensity(width, height, image_data, args.invert)
    output_image_c_array(width, height, image_data, crossover_intensity, args.invert)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert a bitmap image to a C array for GLCDs')

    parser.add_argument(
            '-i', '--invert',
            action='store_true',
            help='Invert image intensity')

    parser.add_argument(
            '--width',
            default=64,
            type=int,
            help='Width of the output image')

    parser.add_argument(
            '--height',
            default=128,
            type=int,
            help='Height of the output image')

    parser.add_argument(
            '-f', '--image',
            type=str,
            help='Image file to convert')

    args = parser.parse_args()

    convert(args)
