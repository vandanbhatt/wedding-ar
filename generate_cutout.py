import os
import sys
import time
import numpy as np
from PIL import Image

def process():
    input_path = "JAI_3712.jpg"
    out_dir = "output"
    os.makedirs(out_dir, exist_ok=True)
    out_cutout = os.path.join(out_dir, "vandan_riddhi_cutout.png")
    out_mask = os.path.join(out_dir, "mask_preview.png")

    print(f"Loading original image: {input_path}...", flush=True)
    t0 = time.time()
    orig = Image.open(input_path)
    # Ensure RGB
    orig_rgb = orig.convert("RGB")
    w, h = orig_rgb.size
    print(f"Original image dimensions: {w}x{h} (loaded in {time.time()-t0:.2f}s)", flush=True)

    print("Importing rembg...", flush=True)
    t1 = time.time()
    from rembg import remove, new_session
    print(f"Rembg imported in {time.time()-t1:.2f}s", flush=True)

    # Use u2net_human_seg or u2net
    # Let's try u2net_human_seg first, or u2net
    model_name = "u2net_human_seg"
    print(f"Creating session for {model_name}...", flush=True)
    t2 = time.time()
    try:
        session = new_session(model_name)
        print(f"Session {model_name} initialized in {time.time()-t2:.2f}s", flush=True)
    except Exception as e:
        print(f"Failed to create session with {model_name}: {e}. Falling back to u2net...", flush=True)
        model_name = "u2net"
        session = new_session(model_name)
        print(f"Session {model_name} initialized in {time.time()-t2:.2f}s", flush=True)

    print("Generating alpha mask (only_mask=True)...", flush=True)
    t3 = time.time()
    # Using only_mask=True extracts the raw mask without modifying any RGB pixels
    mask = remove(orig_rgb, session=session, only_mask=True)
    print(f"Mask generated in {time.time()-t3:.2f}s. Mask size: {mask.size}", flush=True)

    # Convert mask to grayscale (L)
    if mask.mode != "L":
        mask = mask.convert("L")

    # If mask size doesn't match orig size (should match, but verify)
    if mask.size != (w, h):
        print(f"Resizing mask from {mask.size} to {(w, h)}...", flush=True)
        mask = mask.resize((w, h), Image.Resampling.LANCZOS)

    # Save mask preview
    print(f"Saving mask preview to {out_mask}...", flush=True)
    mask.save(out_mask)

    # Construct cutout: exactly original RGB pixels + the alpha channel
    print("Constructing RGBA cutout with unmodified original RGB pixels...", flush=True)
    cutout = Image.new("RGBA", (w, h))
    cutout.paste(orig_rgb, (0, 0))
    cutout.putalpha(mask)

    print(f"Saving cutout PNG to {out_cutout}...", flush=True)
    cutout.save(out_cutout, format="PNG")
    print(f"Cutout saved successfully! File size: {os.path.getsize(out_cutout):,} bytes", flush=True)
    print(f"Total time: {time.time()-t0:.2f}s", flush=True)

if __name__ == "__main__":
    process()
