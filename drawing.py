import numpy as np
from PIL import Image, ImageOps, ImageChops, ImageFilter
from PySide6.QtGui import QPixmap, QImage

def addition(a: Image.Image, b:Image.Image) -> Image.Image:
    a_i = ImageOps.invert(a)
    b_i = ImageOps.invert(b)

    result = ImageChops.add(a_i, b_i)
    result = ImageOps.invert(result)

    return result 

def rasterize(input: Image.Image, edge: float = None) -> Image.Image:
    if edge is None:
        edge = 2
        
    width, height = input.size
    input = input.resize((int(width * edge), int(height * edge)), resample=Image.NEAREST)
    input = input.filter(ImageFilter.MedianFilter())
    input = input.resize((width, height), resample=Image.ADAPTIVE)

    return input

def thresholding(input: Image.Image, threshold: int = None) -> Image.Image:
    if threshold is None:
        threshold = 128

    output = input.convert("L")

    pixel_data = output.getdata()
    modified_pixels = []

    for pixel in pixel_data:
        if(pixel >= threshold):
            modified_pixels.append(255)
        else:
            modified_pixels.append(0)

    output.putdata(modified_pixels)
    return output

def prewitt(input: Image.Image, power: float = None) -> Image.Image:
    input = input.convert('L')
    image = np.array(input).astype(np.uint8)

    if power is None:
        power = 1.0

    # Prewitt Operator
    h, w = image.shape
    horizontal = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
    vertical = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])

    newgradientImage = np.zeros((h, w))

    # offset by 1
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            horizontalGrad = (horizontal[0, 0] * image[i - 1, j - 1]) + \
                            (horizontal[0, 1] * image[i - 1, j]) + \
                            (horizontal[0, 2] * image[i - 1, j + 1]) + \
                            (horizontal[1, 0] * image[i, j - 1]) + \
                            (horizontal[1, 1] * image[i, j]) + \
                            (horizontal[1, 2] * image[i, j + 1]) + \
                            (horizontal[2, 0] * image[i + 1, j - 1]) + \
                            (horizontal[2, 1] * image[i + 1, j]) + \
                            (horizontal[2, 2] * image[i + 1, j + 1])

            verticalGrad = (vertical[0, 0] * image[i - 1, j - 1]) + \
                        (vertical[0, 1] * image[i - 1, j]) + \
                        (vertical[0, 2] * image[i - 1, j + 1]) + \
                        (vertical[1, 0] * image[i, j - 1]) + \
                        (vertical[1, 1] * image[i, j]) + \
                        (vertical[1, 2] * image[i, j + 1]) + \
                        (vertical[2, 0] * image[i + 1, j - 1]) + \
                        (vertical[2, 1] * image[i + 1, j]) + \
                        (vertical[2, 2] * image[i + 1, j + 1])

            # Edge Magnitude
            mag = np.sqrt(pow(horizontalGrad, 2.0) + pow(verticalGrad, 2.0)) * power
            newgradientImage[i - 1, j - 1] = mag

    image = Image.fromarray(newgradientImage)
    image = image.convert("L")
    image = ImageOps.invert(image)

    return image

def alpha_removal(input: Image.Image) -> Image.Image:
    input = input.convert("RGBA")

    pixel_data = input.getdata()
    modified_pixels = []

    for pixel in pixel_data:
        red, green, blue, alpha = pixel

        if alpha < 255:
            value = (255 - alpha)
            modified_pixels.append((red + value, green + value, blue + value))
        else:
            modified_pixels.append((red, green, blue))

    input = Image.new("RGB", input.size)
    input.putdata(modified_pixels)

    return input

def resize(input: Image.Image, factor: float):
    width, height = input.size
    return input.resize((int(width * factor), int(height * factor)))

def lineart(input: Image.Image, power: float = None, threshold: int = None) -> Image.Image:
    if threshold is None: 
        threshold = 128

    if power is None: 
        power = 1

    dark = thresholding(input, 92)
    dark = rasterize(dark)

    prewitt_edge = prewitt(input, power)
    prewitt_edge = thresholding(prewitt_edge, threshold)
    prewitt_edge = rasterize(prewitt_edge)
    result = addition(dark, prewitt_edge)

    return result

def white_alpha(input: Image.Image) -> Image.Image:
    input = input.convert("RGBA")

    pixel_data = input.getdata()
    modified_pixels = []

    for pixel in pixel_data:
        red, green, blue, _ = pixel
        alpha = 255 - (red + green + blue) / 3
        modified_pixels.append((0, 0, 0, int(alpha)))

    input.putdata(modified_pixels)

    return input

def pil_to_pixmap(input : Image.Image) -> QPixmap:
    image_data = input.convert("RGBA").tobytes("raw", "RGBA")
    qimage = QImage(image_data, input.size[0], input.size[1], QImage.Format_RGBA8888)
    pixmap = QPixmap.fromImage(qimage)
    
    return pixmap