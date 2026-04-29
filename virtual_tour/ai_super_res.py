#  Prim Rajasurang Wongkrasaemongkol 
#  
#  Author: Prim Rajasurang Wongkrasaemongkol
#
#  AI-enhanced image processing pipeline for loading, upscaling, and displaying images.
#  
#  Copyright 2 All rights reserved.
#  
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  
#   https://www.apache.org/licenses/LICENSE-2.0
#  
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import cv2
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

def ai_super_resolution(image, model_path='ESPCN_x4.pb', scale=4):
    """
    Enhance image details using AI-based super resolution from OpenCV's DNN module.
    
    :param image: Input image in RGB format.
    :param model_path: Path to the pre-trained model file.
    :param scale: Upscaling factor.
    :return: Super-resolved image.
    """
    try:
        # Initialize the DNN Super Resolution object from OpenCV
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        sr.readModel(model_path)
        # You can use models like 'espcn', 'edsr', 'fsrcnn', etc.
        sr.setModel("espcn", scale)
        # OpenCV expects BGR format for processing
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        result_bgr = sr.upsample(image_bgr)
        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        return result_rgb
    except Exception as e:
        print("AI super resolution failed. Check the model file and configuration.")
        print("Error:", e)
        return image
    
def process_image(image_path: str, output_prefix: str = "output"):
    # Load the original image
    original_img = load_image(image_path)
    show_image("Original Image", original_img)
    save_image(f"{output_prefix}_original.jpg", original_img)
    
    super_res_img = ai_super_resolution(original_img, model_path='ESPCN_x4.pb', scale=4)
    show_image("AI Enhanced (Super Resolution)", super_res_img)
    save_image(f"{output_prefix}_ai_super_res.jpg", super_res_img)

    print("Image processing pipeline complete. Check output images saved with prefix:", output_prefix)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Image Optimization and Enhancement Pipeline")
    parser.add_argument("--image", type=str, default="input.jpg", help="Path to the input image")
    parser.add_argument("--output_prefix", type=str, default="output", help="Prefix for output image filenames")
    args = parser.parse_args()

    process_image(args.image, args.output_prefix)
