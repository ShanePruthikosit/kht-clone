#  Prim Rajasurang Wongkrasaemongkol 
#  
#  Author: Prim Rajasurang Wongkrasaemongkol
#
#  Convert HEIC to JPG image processing 
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
import pyheif
from PIL import Image
import os
import sys

def convert_heic_to_jpg(input_file, output_file=None):
    # Read the HEIC file using pyheif
    heif_file = pyheif.read(input_file)
    
    # Convert the HEIC file data to a PIL Image object
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    
    # If no output file is specified, change the extension to .jpg
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + ".jpg"
    
    # Save the image as JPEG
    image.save(output_file, "JPEG")
    print(f"Converted {input_file} to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python heic_to_jpg.py <input_file.heic> [<output_file.jpg>]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_heic_to_jpg(input_path, output_path)
