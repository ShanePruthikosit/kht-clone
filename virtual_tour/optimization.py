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

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Image Optimization and Enhancement Pipeline")
    parser.add_argument("--image", type=str, default="input.jpg", help="Path to the input image")
    parser.add_argument("--output_prefix", type=str, default="output", help="Prefix for output image filenames")
    args = parser.parse_args()