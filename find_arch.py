import cv2
import numpy as np
from PIL import Image

card = cv2.imread("card_front.jpg")
hsv = cv2.cvtColor(card, cv2.COLOR_BGR2HSV)

# Green garden mask: H between 25 and 90, S > 30, V > 30
green_mask = cv2.inRange(hsv, (25, 25, 25), (90, 255, 255))

# Also bridal red: H between 0..10 and 170..180, S > 50
red_mask1 = cv2.inRange(hsv, (0, 50, 50), (12, 255, 255))
red_mask2 = cv2.inRange(hsv, (168, 50, 50), (180, 255, 255))

photo_elements = green_mask | red_mask1 | red_mask2

# Morphological close to bridge gaps
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
closed = cv2.morphologyEx(photo_elements, cv2.MORPH_CLOSE, kernel)

# Find external contours
contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
best_contour = max(contours, key=cv2.contourArea)
x, y, w, h = cv2.boundingRect(best_contour)

print(f"Detected photo window bounding box:")
print(f"X: {x} -> {x+w} (width: {w})")
print(f"Y: {y} -> {y+h} (height: {h})")

# Let's inspect the exact arch coordinates:
# Arch top center, arch bottom
# Let's check card dimensions
cw, ch = card.shape[1], card.shape[0]
print(f"Card dimensions: {cw}x{ch}")
print(f"Relative X: {x/cw:.4f} to {(x+w)/cw:.4f}, center X: {(x+w/2)/cw:.4f}")
print(f"Relative Y: {y/ch:.4f} to {(y+h)/ch:.4f}, center Y: {(y+h/2)/ch:.4f}")
print(f"Relative Width: {w/cw:.4f}, Relative Height: {h/ch:.4f}")
