import cv2
import numpy as np
import qrcode
from PIL import Image

def generate_card_back(url="https://vandanbhatt.github.io/wedding-ar/"):
    back_img = Image.open("card_back.jpg").convert("RGB")
    bw, bh = back_img.size

    # Box coordinates found earlier: X: 227..499, Y: 378..645
    box_x = 227
    box_y = 378
    box_w = 499 - 227  # 272
    box_h = 645 - 378  # 267

    # Generate QR Code with champagne-gold / deep bronze tint to match the card's luxury theme
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # QR color: elegant deep bronze / gold #4A3B2C or classic black
    qr_img = qr.make_image(fill_color="#3A2E20", back_color="#FFFFFF").convert("RGB")

    # Resize QR to fit nicely inside the box with small padding
    padding = 10
    target_qr_size = min(box_w, box_h) - padding * 2  # ~247px
    qr_resized = qr_img.resize((target_qr_size, target_qr_size), Image.Resampling.LANCZOS)

    # Paste centered in box
    paste_x = box_x + (box_w - target_qr_size) // 2
    paste_y = box_y + (box_h - target_qr_size) // 2

    back_composite = back_img.copy()
    back_composite.paste(qr_resized, (paste_x, paste_y))

    out_path = "output/vandan_riddhi_card_back_with_qr.png"
    back_composite.save(out_path, format="PNG", quality=100)
    print(f"Card back with QR code saved to {out_path}!")

if __name__ == "__main__":
    generate_card_back()
