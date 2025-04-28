#  Prim Rajasurang Wongkrasaemongkol 
#
#  Author: Prim Rajasurang Wongkrasaemongkol
#
#  Preprocess_panorama.py
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
import os
from cv2 import dnn_superres

def preprocess(input_path,
               output_path,
               sr_model_path="EDSR_x4.pb",
               clip_limit=2.0,
               tile_grid_size=(8,8)):
    # Load
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Could not read {input_path}")

    # Lighting/contrast: CLAHE on L channel
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    cl = clahe.apply(l)
    lab = cv2.merge((cl, a, b))
    img_clahe = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # Super‑resolution: EDSR ×4
    sr = dnn_superres.DnnSuperResImpl_create()
    sr.readModel(sr_model_path)
    sr.setModel("edsr", 4)
    img_up = sr.upsample(img_clahe)

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img_up)
    print(f"Preprocessed image saved to {output_path}")

if __name__ == "__main__":
    # adjust paths as needed
    preprocess(
      input_path="static/panoramas/village1.JPG",
      output_path="static/panoramas/panorama_processed.jpg",
      sr_model_path="EDSR_x4.pb"
    )
