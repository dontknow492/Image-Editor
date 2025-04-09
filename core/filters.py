from loguru import logger
import cv2 as cv
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

def filter_blur(image: Image.Image,  radius: int):

    """
    Applies a Gaussian blur to the image.

    Args:
        image (PIL.Image.Image): The input image to blur.
        radius (int): The radius of the Gaussian blur.

    Returns:
        PIL.Image.Image: The blurred image.
    """
    logger.info(f"Applying Gaussian blur with radius {radius}")
    return image.filter(ImageFilter.GaussianBlur(radius=radius))

def filter_contour(image: Image.Image):
    """
    Enhances the edges in the image.

    Args:
        image (PIL.Image.Image): The input image to enhance edges.

    Returns:
        PIL.Image.Image: The image with enhanced edges.
    """
    logger.info("Enhancing edges")
    return image.filter(ImageFilter.CONTOUR)

def filter_detail(image: Image.Image):
    """
    Enhances the details in the image.

    Args:
        image (PIL.Image.Image): The input image to enhance details.

    Returns:
        PIL.Image.Image: The image with enhanced details.
    """
    logger.info("Enhancing details")
    return image.filter(ImageFilter.DETAIL)

def filter_edge_enhance(image: Image.Image):
    """
    Enhances the edges in the image.

    Args:
        image (PIL.Image.Image): The input image to enhance edges.

    Returns:
        PIL.Image.Image: The image with enhanced edges.
    """
    logger.info("Enhancing edges")
    return image.filter(ImageFilter.EDGE_ENHANCE)

def filter_edge_enhance_more(image: Image.Image):
    """
    Enhances the edges in the image more.

    Args:
        image (PIL.Image.Image): The input image to enhance edges.

    Returns:
        PIL.Image.Image: The image with enhanced edges.
    """
    logger.info("Enhancing edges more")
    return image.filter(ImageFilter.EDGE_ENHANCE_MORE)

def filter_emboss(image: Image.Image):
    """
    Embosses the image.

    Args:
        image (PIL.Image.Image): The input image to emboss.

    Returns:
        PIL.Image.Image: The embossed image.
    """
    logger.info("Embossing image")
    return image.filter(ImageFilter.EMBOSS)

def filter_find_edges(image: Image.Image):
    """
    Finds edges in the image.

    Args:
        image (PIL.Image.Image): The input image to find edges.

    Returns:
        PIL.Image.Image: The image with found edges.
    """
    logger.info("Finding edges")
    return image.filter(ImageFilter.FIND_EDGES)

def filter_sharpen(image: Image.Image, factor: float):
    """
    Sharpens the image by enhancing edges.

    Args:
        image (PIL.Image.Image): The input image to sharpen.
        factor (float): The sharpening factor.

    Returns:
        PIL.Image.Image: The sharpened image.
    """
    logger.info(f"Sharpening image with factor {factor}")
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(factor)

def filter_smooth(image: Image.Image):
    """
    Smooths the image.

    Args:
        image (PIL.Image.Image): The input image to smooth.

    Returns:
        PIL.Image.Image: The smoothed image.
    """
    logger.info("Smoothing image")
    return image.filter(ImageFilter.SMOOTH)

def filter_smooth_more(image: Image.Image):
    """
    Smooths the image more.

    Args:
        image (PIL.Image.Image): The input image to smooth.

    Returns:
        PIL.Image.Image: The smoothed image.
    """
    logger.info("Smoothing image more")
    return image.filter(ImageFilter.SMOOTH_MORE)

def filter_pixelation(image, pixel_size=10):
    """
    Apply pixelation effect to an image.

    Args:
        image: Input image (numpy array) in BGR format
        pixel_size: Size of pixelation blocks (default=10)

    Returns:
        Pixelated image as numpy array

    Raises:
        ValueError: If image is None or pixel_size is invalid
    """
    image = np.array(image, np.uint8)

    # Get image dimensions
    h, w = image.shape[:2]

    # Ensure dimensions are valid for resizing
    if h < pixel_size or w < pixel_size:
        raise ValueError("pixel_size must be smaller than image dimensions")

    # Downscale image
    temp = cv.resize(image,
            (w // pixel_size, h // pixel_size),
            interpolation=cv.INTER_LINEAR)

    # Upscale back to original size with nearest neighbor interpolation
    pixelated = cv.resize(temp,
            (w, h),
            interpolation=cv.INTER_NEAREST)

    return Image.fromarray(pixelated)

def filter_glitch(image: Image.Image) -> Image.Image:
    """
    Apply a glitch effect to the image.

    Args:
        image (Image.Image): Input image in PIL format.

    Returns:
        Image.Image: Glitched image in PIL format.

    Raises:
        ValueError: If image is None.
    """
    if image is None:
        raise ValueError("Input image cannot be None")

    # Convert PIL image to NumPy array
    image_np = np.array(image, dtype=np.uint8)

    # Get image dimensions
    h, w, c = image_np.shape

    # Create a copy for glitch effect
    glitched = np.copy(image_np)

    # Randomly shift different color channels
    for i in range(c):  # Iterate over RGB channels
        shift = np.random.randint(-w // 10, w // 10)  # Random shift up to 10% of width
        glitched[:, :, i] = np.roll(image_np[:, :, i], shift, axis=1)

    # Convert back to PIL Image and return
    return Image.fromarray(glitched)

def filter_invert(image: Image.Image):
    """
    Inverts the colors of the image.

    Args:
        image (PIL.Image.Image): The input image to invert.

    Returns:
        PIL.Image.Image: The inverted image.
    """
    logger.info("Inverting image colors")
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    return ImageOps.invert(image)

def filter_cartoon(image: Image.Image):
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    image = np.array(image)
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.medianBlur(gray, 5)
    edges = cv.adaptiveThreshold(blurred, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 9, 9)

    color = cv.bilateralFilter(image, 9, 300, 300)
    cartoon = cv.bitwise_and(color, color, mask=edges)
    return Image.fromarray(cartoon)

def filter_sepia(image: Image.Image):
    """
    Applies a sepia effect to the image.

    Args:
        image (PIL.Image.Image): The input image to apply the sepia effect.

    Returns:
        PIL.Image.Image: The image with the sepia effect applied.
    """
    logger.info("Applying sepia effect")
    # Convert image to RGB if it's not already
    if image.mode != 'RGB':
        image = image.convert('RGB')

    image = np.array(image, dtype=np.float32)
    # Define sepia matrix
    sepia_filter = np.array([[0.272, 0.534, 0.131],
                                [0.349, 0.686, 0.168],
                                [0.393, 0.769, 0.189]])

    # Apply sepia effect
    sepia_image = cv.transform(image, sepia_filter)
    image = np.clip(sepia_image, 0, 255).astype(np.uint8)
    return Image.fromarray(image)

def filter_grayscale(image: Image.Image):
    """
    Converts the image to grayscale.

    Args:
        image (PIL.Image.Image): The input image to convert to grayscale.

    Returns:
        PIL.Image.Image: The grayscale image.
    """
    logger.info("Converting image to grayscale")
    return image.convert("L").convert("RGB") #for 3 channel

if __name__ == "__main__":
    img = Image.open(r"D:\Java\DukeWithHelmet.png")
    img = filter_cartoon(img)
    # img = filter_invert(img)
    # img = filter_pixelation(img, 2)
    # img =  filter_glitch(img)
    # img = filter_sepia(img)
    # img = img.convert("L")
    # img = filter_blur(img, 1.5)
    # img = filter_contour(img)
    # img = filter_detail(img)
    # img = filter_edge_enhance(img)
    # img = filter_edge_enhance_more(img)
    # img = filter_emboss(img)
    # img = filter_find_edges(img)
    # img = filter_sharpen(img, 2)
    img.show()
