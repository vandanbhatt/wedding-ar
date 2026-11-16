import cv2
import numpy as np

back = cv2.imread("card_back.jpg")
gray = cv2.cvtColor(back, cv2.COLOR_BGR2GRAY)

# White box threshold: high brightness (>250) in center region
h, w = gray.shape
center_crop = gray[int(h*0.3):int(h*0.7), int(w*0.2):int(w*0.8)]
_, thresh = cv2.threshold(center_crop, 245, 255, cv2.THRESH_BINARY)

contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
best = max(contours, key=cv2.contourArea)
cx, cy, cw, ch = cv2.boundingRect(best)

# Offset back to full image coordinates
real_x = cx + int(w * 0.2)
real_y = cy + int(h * 0.3)
print(f"White square box on card_back.jpg:")
print(f"X: {real_x} -> {real_x + cw} (width: {cw})")
print(f"Y: {real_y} -> {real_y + ch} (height: {ch})")
