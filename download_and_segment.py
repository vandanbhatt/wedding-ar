import os
import sys
import time
import requests
import numpy as np
from PIL import Image
import cv2
import onnxruntime as ort

MODEL_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "u2net_human_seg.onnx")

def download_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 100_000_000:
        print(f"Model already exists at {MODEL_PATH} ({os.path.getsize(MODEL_PATH):,} bytes).")
        return

    print(f"Downloading model from {MODEL_URL}...", flush=True)
    t0 = time.time()
    response = requests.get(MODEL_URL, stream=True, timeout=30)
    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0
    chunk_size = 1024 * 1024  # 1MB chunks

    with open(MODEL_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                pct = (downloaded / total_size * 100) if total_size else 0
                mb_down = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                elapsed = time.time() - t0
                speed = mb_down / elapsed if elapsed > 0 else 0
                print(f"\rDownloading: {mb_down:.1f}/{mb_total:.1f} MB ({pct:.1f}%) at {speed:.2f} MB/s", end="", flush=True)

    print(f"\nDownload finished in {time.time()-t0:.2f}s!")

def normalize_input(img, size=(320, 320)):
    im = img.convert("RGB").resize(size, Image.Resampling.LANCZOS)
    im_ary = np.array(im, dtype=np.float32) / 255.0

    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    tmpImg = (im_ary - mean) / std
    tmpImg = tmpImg.transpose((2, 0, 1))
    return np.expand_dims(tmpImg, 0).astype(np.float32)

def run_segmentation():
    download_model()

    input_img_path = "JAI_3712.jpg"
    out_dir = "output"
    os.makedirs(out_dir, exist_ok=True)
    out_cutout_path = os.path.join(out_dir, "vandan_riddhi_cutout.png")
    out_mask_path = os.path.join(out_dir, "mask_preview.png")
    out_verify_path = os.path.join(out_dir, "segmentation_preview.jpg")

    print(f"Loading {input_img_path}...", flush=True)
    orig_img = Image.open(input_img_path)
    w, h = orig_img.size
    print(f"Image dimensions: {w}x{h}, Mode: {orig_img.mode}")

    print("Initializing ONNX InferenceSession...", flush=True)
    t0 = time.time()
    sess_opts = ort.SessionOptions()
    sess_opts.intra_op_num_threads = 4
    session = ort.InferenceSession(MODEL_PATH, sess_options=sess_opts, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    print(f"ONNX session ready in {time.time()-t0:.2f}s, input name: {input_name}")

    print("Preprocessing image...", flush=True)
    inp = normalize_input(orig_img, size=(320, 320))

    print("Running neural network inference...", flush=True)
    t1 = time.time()
    ort_outs = session.run(None, {input_name: inp})
    print(f"Inference complete in {time.time()-t1:.2f}s!")

    pred = ort_outs[0][:, 0, :, :]
    ma = np.max(pred)
    mi = np.min(pred)
    if ma - mi > 0:
        pred = (pred - mi) / (ma - mi)
    pred = np.squeeze(pred)

    raw_mask_small = (pred * 255).astype(np.uint8)
    
    # Resize mask to original full resolution (w, h)
    print("Upscaling mask to original high-res dimensions...", flush=True)
    mask_full = cv2.resize(raw_mask_small, (w, h), interpolation=cv2.INTER_LANCZOS4)

    # OpenCV edge refinement: slight soft thresholding to avoid fringe
    # Soft alpha feathering: keep solid foreground > 200, background < 30, smooth transition in between
    # Apply subtle guided filter / bilateral smoothing on the alpha edge to match photographic edges
    print("Refining mask alpha edges with OpenCV...", flush=True)
    _, binary_thresh = cv2.threshold(mask_full, 240, 255, cv2.THRESH_BINARY)
    # Remove small isolated noise dots in background
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask_cleaned = cv2.morphologyEx(mask_full, cv2.MORPH_CLOSE, kernel)
    
    # Save the grayscale mask preview
    print(f"Saving mask preview to {out_mask_path}...", flush=True)
    cv2.imwrite(out_mask_path, mask_cleaned)

    # Construct Cutout: exactly original RGB pixels + refined alpha channel
    print("Assembling cutout with original unchanged RGB pixels...", flush=True)
    orig_rgb = orig_img.convert("RGB")
    orig_np = np.array(orig_rgb)
    
    # Combine RGB + Alpha
    rgba = np.dstack([orig_np, mask_cleaned])
    cutout_img = Image.fromarray(rgba, mode="RGBA")
    
    print(f"Saving high-resolution cutout to {out_cutout_path}...", flush=True)
    cutout_img.save(out_cutout_path, format="PNG")
    print(f"Cutout saved! Size: {os.path.getsize(out_cutout_path):,} bytes")

    # Generate a composite preview on light neutral background and dark background
    print(f"Generating verification preview at {out_verify_path}...", flush=True)
    preview_scale = 1200 / max(w, h)
    pw, ph = int(w * preview_scale), int(h * preview_scale)
    preview_rgb = cv2.resize(orig_np, (pw, ph), interpolation=cv2.INTER_AREA)
    preview_mask = cv2.resize(mask_cleaned, (pw, ph), interpolation=cv2.INTER_AREA) / 255.0

    # Composite on white & checkerboard
    bg_white = np.ones_like(preview_rgb) * 255
    comp_white = (preview_rgb * preview_mask[:, :, None] + bg_white * (1.0 - preview_mask[:, :, None])).astype(np.uint8)

    # Concatenate side by side: [Original | Mask | Cutout on White]
    mask_3ch = np.repeat((preview_mask * 255).astype(np.uint8)[:, :, None], 3, axis=2)
    preview_strip = np.hstack([preview_rgb, mask_3ch, comp_white])
    # Convert RGB to BGR for cv2.imwrite
    cv2.imwrite(out_verify_path, cv2.cvtColor(preview_strip, cv2.COLOR_RGB2BGR))
    print(f"Verification preview saved at {out_verify_path}!")

if __name__ == "__main__":
    run_segmentation()
