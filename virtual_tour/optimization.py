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

def process_image(image_path: str, output_prefix: str = "output"):
    # Load the original image
    original_img = load_image(image_path)
    show_image("Original Image", original_img)
    save_image(f"{output_prefix}_original.jpg", original_img)

    # Step 1: Add Gaussian noise
    noisy_img = add_gaussian_noise(original_img, mean=0, sigma=25)
    show_image("Image with Gaussian Noise", noisy_img)
    save_image(f"{output_prefix}_noisy.jpg", noisy_img)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Image Optimization and Enhancement Pipeline")
    parser.add_argument("--image", type=str, default="input.jpg", help="Path to the input image")
    parser.add_argument("--output_prefix", type=str, default="output", help="Prefix for output image filenames")
    args = parser.parse_args()

    process_image(args.image, args.output_prefix)
