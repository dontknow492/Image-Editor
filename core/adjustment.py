import numpy as np
from PIL import Image, ImageEnhance
from loguru import logger
import cv2 as cv


def _ensure_valid_mode(image: Image.Image) -> Image.Image:
    """
    Ensures that the image is in a suitable mode (RGB, RGBA, or L for grayscale).
    This function prevents unnecessary conversions and preserves the original format.
    """
    if image.mode in ["RGB", "L", "RGBA"]:
        return image
    return image.convert("RGB")


def convert_to_hsv(image: Image.Image) -> Image.Image:
    """
    Converts an image to the HSV color space.

    Args:
        image (PIL.Image.Image): The input image to convert.

    Returns:
        PIL.Image.Image: The image in HSV color space.
    """
    if image.mode != "HSV":
        image = image.convert("HSV")
    return image


def update_rgb(image: Image.Image, r: int, g: int, b: int) -> Image.Image:
    """
    Adjusts the intensity of Red, Green, and Blue channels by adding specific values.

    Args:
        image (PIL.Image.Image): Input image.
        r (int): Red channel adjustment value (-255 to 255).
        g (int): Green channel adjustment value (-255 to 255).
        b (int): Blue channel adjustment value (-255 to 255).

    Returns:
        PIL.Image.Image: RGB adjusted image.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")
    logger.info(f"Adjusting RGB by ({r}, {g}, {b})")
    image_array = np.array(image, dtype=np.int16)

    # Adjust RGB values and clip to [0, 255]
    image_array[..., 0] = np.clip(image_array[..., 0] + r, 0, 255)
    image_array[..., 1] = np.clip(image_array[..., 1] + g, 0, 255)
    image_array[..., 2] = np.clip(image_array[..., 2] + b, 0, 255)

    return Image.fromarray(image_array.astype(np.uint8), mode=image.mode)

def adjust_red(image: Image.Image, red_intensity: int) -> Image.Image:
    """
    Adjusts the red channel of an image by adding a specific intensity value.

    Args:
        image (PIL.Image.Image): Input image.
        red_intensity (int): Intensity value to add to the red channel (-255 to 255).

    Returns:
        PIL.Image.Image: Red adjusted image.
    """
    return update_rgb(image, red_intensity, 0, 0)

def adjust_green(image: Image.Image, green_intensity: int) -> Image.Image:
    """
    Adjusts the green channel of an image by adding a specific intensity value.

    Args:
        image (PIL.Image.Image): Input image.
        green_intensity (int): Intensity value to add to the green channel (-255 to 255).

    Returns:
        PIL.Image.Image: Green adjusted image.
    """
    return update_rgb(image, 0, green_intensity, 0)

def adjust_blue(image: Image.Image, blue_intensity: int) -> Image.Image:
    """
    Adjusts the blue channel of an image by adding a specific intensity value.

    Args:
        image (PIL.Image.Image): Input image.
        blue_intensity (int): Intensity value to add to the blue channel (-255 to 255).

    Returns:
        PIL.Image.Image: Blue adjusted image.
    """
    return update_rgb(image, 0, 0, blue_intensity)

def adjust_temperature(image: Image.Image, temperature_shift: int) -> Image.Image:
    """
    Adjusts the color temperature by shifting red and blue channels.

    Args:
        image (PIL.Image.Image): The input image to adjust.
        temperature_shift (float): Shift value (>0 for cooler, <0 for warmer).

    Returns:
        PIL.Image.Image: The image with adjusted temperature.
    """

    logger.info(f"Adjusting temperature by shift: {temperature_shift}")
    return update_rgb(image, temperature_shift, 0, -temperature_shift)


def adjust_brightness(image: Image.Image, brightness_factor: float) -> Image.Image:
    """
    Adjusts the brightness of an image by multiplying pixel values with a factor.

    Args:
        image (PIL.Image.Image): Input image.
        brightness_factor (float): Factor for brightness (0.0 - dark, 1.0 - original, >1.0 - bright).

    Returns:
        PIL.Image.Image: Brightness-adjusted image.
    """
    image = _ensure_valid_mode(image)
    logger.info(f"Adjusting brightness by factor {brightness_factor}")
    image_array = np.array(image, dtype=np.float32) * brightness_factor
    return Image.fromarray(np.clip(image_array, 0, 255).astype(np.uint8), mode=image.mode)


def adjust_contrast(image: Image.Image, contrast_factor: float) -> Image.Image:
    """
    Adjusts image contrast by scaling pixel values relative to the midpoint (128).

    Args:
        image (PIL.Image.Image): Input image.
        contrast_factor (float): Contrast multiplier (0.0 - flat, 1.0 - original, >1.0 - high contrast).

    Returns:
        PIL.Image.Image: Contrast-adjusted image.
    """
    image = _ensure_valid_mode(image)
    logger.info(f"Adjusting contrast by factor {contrast_factor}")
    image_array = np.array(image, dtype=np.float32)
    image_array = np.clip((image_array - 128) * contrast_factor + 128, 0, 255)
    return Image.fromarray(image_array.astype(np.uint8), mode=image.mode)


def adjust_saturation(image: Image.Image, saturation_factor: float) -> Image.Image:
    """
    Adjusts the saturation of an image using the HSV color space.

    Args:
        image (PIL.Image.Image): Input image.
        saturation_factor (float): Saturation multiplier (0.0 - grayscale, 1.0 - original, >1.0 - more color).

    Returns:
        PIL.Image.Image: Saturation-adjusted image.
    """
    image = convert_to_hsv(image)

    image_array = np.array(image, dtype=np.float32)
    image_array[..., 1] = np.clip(image_array[..., 1] * saturation_factor, 0, 255)
    return Image.fromarray(image_array.astype(np.uint8), mode="HSV").convert("RGB")


def adjust_hue(image: Image.Image, hue_shift: float) -> Image.Image:
    """
    Adjusts the hue of an image by shifting the hue channel in HSV space.

    Args:
        image (PIL.Image.Image): Input image.
        hue_shift (float): Hue shift value (-180 to 180).

    Returns:
        PIL.Image.Image: Hue-adjusted image.
    """
    image = convert_to_hsv(image)
    image_array = np.array(image, dtype=np.float32)
    image_array[..., 0] = (image_array[..., 0] + hue_shift) % 180
    image = Image.fromarray(image_array.astype(np.uint8), mode="HSV")
    return image.convert("RGB")


def adjust_sharpness(image: Image.Image, sharpness_factor: float) -> Image.Image:
    """
    Adjusts the sharpness using PIL's ImageEnhance.

    Args:
        image (PIL.Image.Image): The input image to adjust.
        sharpness_factor (float): Enhancement factor (>1.0 for sharper, <1.0 for blurrier).

    Returns:
        PIL.Image.Image: The image with adjusted sharpness.
    """
    image = _ensure_valid_mode(image)  # Ensure RGB mode for consistency
    logger.info(f"Adjusting sharpness by factor {sharpness_factor}")
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(sharpness_factor)


def adjust_exposure(image: Image.Image, exposure_factor: float) -> Image.Image:
    """
    Adjusts the exposure by scaling RGB values.

    Args:
        image (PIL.Image.Image): The input image to adjust.
        exposure_factor (float): Scaling factor (>1.0 for brighter, <1.0 for darker).

    Returns:
        PIL.Image.Image: The image with adjusted exposure.
    """
    image = _ensure_valid_mode(image)  # Ensure RGB mode
    logger.info(f"Adjusting exposure by factor {exposure_factor}")
    image_array = np.array(image, dtype=np.float32)  # Use float32 for precision

    image_array = np.clip(image_array * exposure_factor, 0, 255)
    return Image.fromarray(image_array.astype(np.uint8))


def adjust_gamma(image: Image.Image, gamma: float) -> Image.Image:
    """
    Adjusts the gamma by applying a power-law transformation.

    Args:
        image (PIL.Image.Image): The input image to adjust.
        gamma (float): Gamma value (>1.0 for brighter, <1.0 for darker).

    Returns:
        PIL.Image.Image: The image with adjusted gamma.
    """
    image = _ensure_valid_mode(image)  # Ensure RGB mode
    logger.info(f"Adjusting gamma by {gamma}")
    image_array = np.array(image, dtype=np.float32)  # Use float32 for precision

    image_array = np.clip(255 * (image_array / 255) ** gamma, 0, 255)  # Normalize, apply gamma
    return Image.fromarray(image_array.astype(np.uint8))


def adjust_vignette(image: Image.Image, vignette_strength: float) -> Image.Image:
    """
    Applies a vignette effect, darkening the edges.

    Args:
        image (PIL.Image.Image): The input image to adjust.
        vignette_strength (float): Strength of vignette (>=0, higher for stronger effect).

    Returns:
        PIL.Image.Image: The image with vignette effect.
    """
    image = _ensure_valid_mode(image)  # Ensure RGB mode
    logger.info(f"Adjusting vignette by strength {vignette_strength}")
    image_array = np.array(image, dtype=np.float32)  # Use float32 for precision

    height, width = image_array.shape[:2]
    x, y = np.meshgrid(np.linspace(-1, 1, width), np.linspace(-1, 1, height))
    mask = 1 - np.sqrt(x ** 2 + y ** 2) * vignette_strength
    mask = np.clip(mask, 0, 1)

    image_array *= mask[:, :, np.newaxis]
    image_array = np.clip(image_array, 0, 255)
    return Image.fromarray(image_array.astype(np.uint8))


def adjust_blur(image: Image.Image, blur_radius: float) -> Image.Image:
    """
    Applies a Gaussian blur effect.

    Args:
        image (PIL.Image.Image): The input image to adjust.
        blur_radius (float): Sigma for Gaussian blur (>=0, higher for more blur).

    Returns:
        PIL.Image.Image: The blurred image.
    """
    image = _ensure_valid_mode(image)  # Ensure RGB mode
    logger.info(f"Adjusting blur by radius {blur_radius}")
    image_array = np.array(image, dtype=np.uint8)  # OpenCV expects uint8

    image_array = cv.GaussianBlur(image_array, (3, 3), blur_radius)
    return Image.fromarray(image_array)


def adjust_noise(image: Image.Image, noise_level: float) -> Image.Image:
    """
    Adds Gaussian noise to the image.

    Args:
        image (PIL.Image.Image): The input image to adjust.
        noise_level (float): Standard deviation of noise (>=0, higher for more noise).

    Returns:
        PIL.Image.Image: The image with added noise.
    """
    image = _ensure_valid_mode(image)  # Ensure RGB mode
    logger.info(f"Adjusting noise by level {noise_level}")
    image_array = np.array(image, dtype=np.float32)  # Use float32 for precision

    noise = np.random.normal(0, noise_level, image_array.shape)
    image_array = np.clip(image_array + noise, 0, 255)
    return Image.fromarray(image_array.astype(np.uint8))


def adjust_shadows(image: Image.Image, shadow_intensity: float) -> Image.Image:
    """
    Adjusts shadow areas by darkening the image.

    Args:
        image (PIL.Image.Image): The input image to adjust.
        shadow_intensity (float): Intensity of shadow effect (0 to 1).

    Returns:
        PIL.Image.Image: The image with adjusted shadows.
    """
    image = _ensure_valid_mode(image)  # Ensure RGB mode
    logger.info(f"Adjusting shadows by intensity {shadow_intensity}")
    image_array = np.array(image, dtype=np.float32)  # Use float32 for precision

    image_array = np.clip(image_array * (1 - shadow_intensity), 0, 255)
    return Image.fromarray(image_array.astype(np.uint8))


def adjust_highlight(image: Image.Image, highlight_intensity: float) -> Image.Image:
    """
    Adjusts highlight areas by brightening lighter regions.

    Args:
        image (PIL.Image.Image): The input image to adjust.
        highlight_intensity (float): Intensity of highlight effect (0 to 1).

    Returns:
        PIL.Image.Image: The image with adjusted highlights.
    """
    image = _ensure_valid_mode(image)  # Ensure RGB mode
    logger.info(f"Adjusting highlights by intensity {highlight_intensity}")
    image_array = np.array(image, dtype=np.float32)  # Use float32 for precision

    image_array = np.clip(image_array + (255 - image_array) * highlight_intensity, 0, 255)
    return Image.fromarray(image_array.astype(np.uint8))


if __name__ == "__main__":
    img = Image.open(r"D:\Program\Image Editor\samples\image.jpg")
    # img = img.convert("L")
    # img = img.convert("RGB")
    #
    # array = np.array(img)
    # logger.info(array.ndim)
    # logger.info(array.shape)
    img = adjust_brightness(img, 2)
    # img = adjust_brightness(img, -0.3)
    # img = update_rgb(img, 0, 0, 100)
    # img = update_rgb(img, 0, 0, -100)
    # img.show("rgb")
    # img = adjust_contrast(img, 2)
    # img.show("contrast")
    # img = adjust_saturation(img, 0)
    # img.show("saturation")
    # img = adjust_hue(img, 30)
    # img.show("hue")
    # img = adjust_temperature(img, -50)
    # img.show("temperature")
    # img = adjust_sharpness(img, 2)
    # img.show("sharpness")
    # img = adjust_exposure(img, 1.5)
    # img.show("exposure")
    # img = adjust_gamma(img, 6.8)
    # img.show("gamma")
    # img = adjust_highlight(img, -0.5)
    # img.show("highlights")

    img.show()
