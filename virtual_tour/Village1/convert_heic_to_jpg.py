import pillow_heif
pillow_heif.register_heif_opener()  # Register HEIC support with Pillow

from PIL import Image
import sys
import os

def convert_heic_to_jpg(input_file, output_file=None):
    # Open the HEIC image file
    try:
        image = Image.open(input_file)
    except Exception as e:
        print(f"Error opening {input_file}: {e}")
        return

    # Determine output file name if not provided
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + ".jpg"

    # Save the image as JPEG
    try:
        image.save(output_file, "JPEG")
        print(f"Successfully converted {input_file} to {output_file}")
    except Exception as e:
        print(f"Error saving {output_file}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_heic_to_jpg.py <input_file.heic> [<output_file.jpg>]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    convert_heic_to_jpg(input_path, output_path)
