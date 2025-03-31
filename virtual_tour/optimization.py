import cv2
import numpy as np
import matplotlib.pyplot as plt

def load_image(path: str):
    """
    Load an image from disk.
    """
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError(f"Image not found at path: {path}")
    # Convert BGR (OpenCV default) to RGB for display
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def save_image(path: str, image):
    """
    Save an image to disk.
    """
    # Convert RGB back to BGR for saving
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(path, image_bgr)

def show_image(title: str, image):
    """
    Display an image using matplotlib.
    """
    plt.figure(figsize=(8, 6))
    plt.imshow(image)
    plt.title(title)
    plt.axis('off')
    plt.show()

def add_gaussian_noise(image, mean=0, sigma=25):
    """
    Add Gaussian noise to an image.
    
    :param image: Input image in RGB format.
    :param mean: Mean of the Gaussian noise.
    :param sigma: Standard deviation of the noise.
    :return: Noisy image.
    """
    noise = np.random.normal(mean, sigma, image.shape)
    noisy_image = image + noise
    # Clip the values to maintain valid pixel range [0, 255]
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
    return noisy_image

def adjust_brightness_contrast(image, brightness=0, contrast=1.0):
    """
    Adjust the brightness and contrast of an image.
    
    :param image: Input image in RGB format.
    :param brightness: Value to be added to each pixel.
    :param contrast: Scaling factor for contrast.
    :return: Adjusted image.
    """
    # Convert to float32 for precision in calculations
    new_image = image.astype(np.float32)
    new_image = new_image * contrast + brightness
    new_image = np.clip(new_image, 0, 255).astype(np.uint8)
    return new_image

def adjust_saturation(image, saturation_scale=1.0):
    """
    Adjust the saturation of an image.
    
    :param image: Input image in RGB format.
    :param saturation_scale: Multiplicative factor for saturation.
    :return: Image with adjusted saturation.
    """
    # Convert image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype(np.float32)
    # Scale the saturation channel
    hsv[..., 1] = hsv[..., 1] * saturation_scale
    hsv[..., 1] = np.clip(hsv[..., 1], 0, 255)
    # Convert back to RGB color space
    adjusted_img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
    return adjusted_img

def process_image(image_path: str, output_prefix: str = "output"):
    # Load the original image
    original_img = load_image(image_path)
    show_image("Original Image", original_img)
    save_image(f"{output_prefix}_original.jpg", original_img)

    # Step 1: Add Gaussian noise
    noisy_img = add_gaussian_noise(original_img, mean=0, sigma=25)
    show_image("Image with Gaussian Noise", noisy_img)
    save_image(f"{output_prefix}_noisy.jpg", noisy_img)

    # Step 2: Adjust brightness and contrast
    # Increase brightness by 30 and contrast by 1.2 times
    bright_contrast_img = adjust_brightness_contrast(noisy_img, brightness=30, contrast=1.2)
    show_image("Brightness & Contrast Adjusted", bright_contrast_img)
    save_image(f"{output_prefix}_bright_contrast.jpg", bright_contrast_img)

    # Step 3: Adjust saturation
    # Increase saturation by 1.5 times
    saturated_img = adjust_saturation(bright_contrast_img, saturation_scale=1.5)
    show_image("Saturation Adjusted", saturated_img)
    save_image(f"{output_prefix}_saturated.jpg", saturated_img)



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Image Optimization and Enhancement Pipeline")
    parser.add_argument("--image", type=str, default="input.jpg", help="Path to the input image")
    parser.add_argument("--output_prefix", type=str, default="output", help="Prefix for output image filenames")
    args = parser.parse_args()

    process_image(args.image, args.output_prefix)
