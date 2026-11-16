import cv2
import numpy as np
from PIL import Image

card = Image.open("card_front.jpg")
cw, ch = card.size
card_np = np.array(card)

# Let's inspect where the garden photo is inside card_front.jpg
# The garden photo has green tones (high green, lower red/blue compared to the cream/pink border)
# Or let's match features / template match with JAI_3712.jpg
orig = Image.open("JAI_3712.jpg")
ow, oh = orig.size

print(f"Card size: {cw}x{ch}, Orig size: {ow}x{oh}")

# Resize orig to test scales
# In the card, the couple is in the center
# Let's crop center vertical region of card
# Usually arch is around Y: 190 to 740, X: 120 to 600
# Let's save a visual grid over card_front.jpg to accurately inspect coordinates
grid_img = card_np.copy()
for y in range(0, ch, 50):
    cv2.line(grid_img, (0, y), (cw, y), (0, 0, 255), 1)
    cv2.putText(grid_img, str(y), (10, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

for x in range(0, cw, 50):
    cv2.line(grid_img, (x, 0), (x, ch), (255, 0, 0), 1)
    cv2.putText(grid_img, str(x), (x + 5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

cv2.imwrite("output/card_grid.jpg", cv2.cvtColor(grid_img, cv2.COLOR_RGB2BGR))
print("Grid saved to output/card_grid.jpg")
