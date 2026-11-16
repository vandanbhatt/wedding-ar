import cv2
import numpy as np
from PIL import Image

def prepare_card_aligned_cutout():
    # Load card front
    card = Image.open("card_front.jpg").convert("RGB")
    cw, ch = card.size

    # Load master cutout (3712 x 5568)
    master_cutout = Image.open("output/vandan_riddhi_cutout.png")
    mw, mh = master_cutout.size

    # From SIFT affine alignment:
    # Scale from orig to card: 0.129743
    # Top-left of orig on card: tx = 121.68, ty = 139.27
    scale = 0.129743
    tx = 121.68
    ty = 139.27

    scaled_w = int(round(mw * scale))  # 482
    scaled_h = int(round(mh * scale))  # 722

    print(f"Resizing master cutout to {scaled_w}x{scaled_h}...")
    scaled_cutout = master_cutout.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)

    # Place onto card-sized transparent canvas
    card_cutout = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    card_cutout.paste(scaled_cutout, (int(round(tx)), int(round(ty))), scaled_cutout)

    # Now mask with the arch boundary:
    # On card_front.jpg, the arch bottom is at Y = 764
    # The couple shouldn't extend below Y = 764 into the text "Vandan & Riddhi"
    card_cutout_np = np.array(card_cutout)
    
    # Clip below Y = 764 with a smooth 10px feather
    y_cut = 764
    feather = 10
    for y in range(y_cut - feather, min(ch, y_cut + feather)):
        alpha_factor = 1.0 - max(0.0, min(1.0, (y - (y_cut - feather)) / (feather * 2)))
        card_cutout_np[y, :, 3] = (card_cutout_np[y, :, 3].astype(np.float32) * alpha_factor).astype(np.uint8)
    card_cutout_np[y_cut + feather:, :, 3] = 0

    out_cutout_card = "output/textures/couple_card_aligned.png"
    Image.fromarray(card_cutout_np, mode="RGBA").save(out_cutout_card, format="PNG", optimize=True)
    print(f"Card-aligned cutout saved to {out_cutout_card}!")

    # Also save card front texture in textures dir
    card_tex_path = "output/textures/card_front_ar.jpg"
    card.save(card_tex_path, format="JPEG", quality=95)
    print(f"Card front texture saved to {card_tex_path}!")

if __name__ == "__main__":
    prepare_card_aligned_cutout()
