import os
from PIL import Image

def prepare_ar_textures():
    tex_dir = os.path.join("output", "textures")
    os.makedirs(tex_dir, exist_ok=True)

    bg_src = "JAI_3712.jpg"
    fg_src = os.path.join("output", "vandan_riddhi_cutout.png")

    bg_dst = os.path.join(tex_dir, "background_ar.jpg")
    fg_dst = os.path.join(tex_dir, "foreground_cutout_ar.png")

    print(f"Loading {bg_src} and {fg_src}...")
    im_bg = Image.open(bg_src)
    im_fg = Image.open(fg_src)

    orig_w, orig_h = im_bg.size
    print(f"Original master size: {orig_w}x{orig_h}")

    # Target: 2048 x 3072 (2:3 aspect ratio, perfectly matches 3712:5568 = 0.66667)
    target_h = 3072
    target_w = int(target_h * (orig_w / orig_h))
    # Make sure width is even
    if target_w % 2 != 0:
        target_w += 1

    print(f"Resampling to AR-optimized crisp texture resolution: {target_w}x{target_h} (Lanczos)...")
    im_bg_ar = im_bg.convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
    im_fg_ar = im_fg.resize((target_w, target_h), Image.Resampling.LANCZOS)

    print(f"Saving {bg_dst}...")
    im_bg_ar.save(bg_dst, format="JPEG", quality=95, optimize=True)

    print(f"Saving {fg_dst}...")
    im_fg_ar.save(fg_dst, format="PNG", optimize=True)

    print(f"AR Background size: {os.path.getsize(bg_dst):,} bytes")
    print(f"AR Foreground cutout size: {os.path.getsize(fg_dst):,} bytes")
    print("AR textures prepared successfully!")

if __name__ == "__main__":
    prepare_ar_textures()
