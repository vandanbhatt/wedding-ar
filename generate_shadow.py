import os
import cv2
import numpy as np
from PIL import Image

def generate_soft_shadow():
    mask_path = os.path.join("output", "mask_preview.png")
    shadow_path = os.path.join("output", "textures", "couple_shadow.png")

    print(f"Loading mask from {mask_path}...")
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    h, w = mask.shape
    print(f"Mask size: {w}x{h}")

    # Resize to AR texture size (2048 x 3072)
    target_w, target_h = 2048, 3072
    mask_ar = cv2.resize(mask, (target_w, target_h), interpolation=cv2.INTER_AREA)

    # Blur to create soft ambient drop shadow
    # Offset shadow slightly downwards (Y direction in image)
    # Downward shift of ~25 pixels
    M = np.float32([[1, 0, 0], [0, 1, 30]])
    shifted_mask = cv2.warpAffine(mask_ar, M, (target_w, target_h), borderValue=0)

    # Large gaussian blur for soft diffuse shadow
    blurred = cv2.GaussianBlur(shifted_mask, (101, 101), sigmaX=35, sigmaY=35)

    # Scale alpha to subtle 30% max opacity (75/255)
    shadow_alpha = (blurred.astype(np.float32) / 255.0 * 85.0).astype(np.uint8)

    # Black RGB with shadow_alpha
    shadow_rgba = np.zeros((target_h, target_w, 4), dtype=np.uint8)
    shadow_rgba[:, :, 3] = shadow_alpha

    print(f"Saving shadow texture to {shadow_path}...")
    Image.fromarray(shadow_rgba, mode="RGBA").save(shadow_path, format="PNG", optimize=True)
    print(f"Shadow texture saved! Size: {os.path.getsize(shadow_path):,} bytes")

if __name__ == "__main__":
    generate_soft_shadow()
