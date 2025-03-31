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