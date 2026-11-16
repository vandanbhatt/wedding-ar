"""
1. Update card back with the latest uploaded QR code image
2. Render all final preview images
3. Copy all FINAL deliverable photos to Desktop in a 'Wedding AR Photos' folder
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import shutil, os, numpy as np

DESKTOP   = os.path.expanduser('~/Desktop')
OUT_FOLDER= os.path.join(DESKTOP, 'Vandan & Riddhi - Wedding AR')
os.makedirs(OUT_FOLDER, exist_ok=True)

NEW_QR    = r'C:/Users/vanda/.gemini/antigravity/brain/3133c024-35e5-486e-ba77-581008b91f2d/.user_uploaded/media_1794872090327_0c2da765.png'
CARD_BACK_SRC = 'output/vandan_riddhi_card_back_with_qr.png'  # original card back layout
CARD_BACK_OUT = 'output/vandan_riddhi_card_back_final.png'

# ══════════════════════════════════════════════════════════════
# STEP 1 — Update card back with crisp new QR
# ══════════════════════════════════════════════════════════════
# Restore clean card back (without old QR) from previous version
import subprocess
result = subprocess.run(
    ['git', 'show', 'ab7b675:output/vandan_riddhi_card_back_with_qr.png'],
    capture_output=True
)
if result.returncode == 0 and len(result.stdout) > 10000:
    with open('output/_card_back_base.png', 'wb') as f:
        f.write(result.stdout)
    card = Image.open('output/_card_back_base.png').convert('RGBA')
    print(f'Loaded base card: {card.size}')
else:
    card = Image.open(CARD_BACK_SRC).convert('RGBA')
    print(f'Using current card: {card.size}')

cw, ch = card.size

# Load & binarize new QR
qr = Image.open(NEW_QR).convert('L')
qr_arr = np.array(qr)
qr_arr = (qr_arr > 128).astype(np.uint8) * 255
qr_bw  = Image.fromarray(qr_arr, 'L').convert('RGBA')

# Target QR size (56% of card width for good scan-ability)
target_w = int(cw * 0.56)
qr_resized = qr_bw.resize((target_w, target_w), Image.LANCZOS)

# White mat behind QR
mat_pad = 14
mat = Image.new('RGBA', (target_w + mat_pad*2, target_w + mat_pad*2), (255,255,255,255))

# Centred, 33% from top
px = (cw - mat.width) // 2
py = int(ch * 0.33)
card.paste(mat, (px - mat_pad, py - mat_pad), mat)
card.paste(qr_resized, (px, py), qr_resized)

# Gold border
draw = ImageDraw.Draw(card)
for t in range(3):
    draw.rectangle([px-mat_pad-t, py-mat_pad-t, px+target_w+mat_pad+t, py+target_w+mat_pad+t],
                   outline=(212,175,55,220), width=1)

card.save(CARD_BACK_OUT, format='PNG', optimize=True)
print(f'Updated card back -> {CARD_BACK_OUT}')
# Clean up tmp
if os.path.exists('output/_card_back_base.png'):
    os.remove('output/_card_back_base.png')

# ══════════════════════════════════════════════════════════════
# STEP 2 — Render backdrop + plaque previews
# ══════════════════════════════════════════════════════════════
backdrop  = Image.open('output/textures/card_stage_backdrop.jpg')
plaque    = Image.open('output/textures/stage_gold_plaque.png')
couple_cut= Image.open('output/textures/foreground_cutout_ar.png')

# Composite a quick 2D preview: couple cutout on top of backdrop
prev_w, prev_h = backdrop.size
prev = backdrop.convert('RGBA')

# Resize couple to fit ~65% of backdrop height, bottom-aligned
couple_h = int(prev_h * 0.68)
couple_w  = int(couple_cut.width * couple_h / couple_cut.height)
couple_rs  = couple_cut.resize((couple_w, couple_h), Image.LANCZOS)
cx = (prev_w - couple_w) // 2
cy = prev_h - couple_h - int(prev_h * 0.04)
prev.paste(couple_rs, (cx, cy), couple_rs)

# Paste plaque at bottom
plq_w = int(prev_w * 0.72)
plq_h = int(plaque.height * plq_w / plaque.width)
plq_rs = plaque.resize((plq_w, plq_h), Image.LANCZOS)
px2 = (prev_w - plq_w) // 2
py2 = prev_h - plq_h - 5
prev.paste(plq_rs, (px2, py2), plq_rs)

preview_path = 'output/vandan_riddhi_stage_preview_2d.jpg'
prev.convert('RGB').save(preview_path, 'JPEG', quality=92)
print(f'2D preview saved -> {preview_path}')

# ══════════════════════════════════════════════════════════════
# STEP 3 — Copy all final deliverables to Desktop folder
# ══════════════════════════════════════════════════════════════
deliverables = {
    # Card prints (for printer)
    '01_PRINT_Card_Front.jpg':  'output/card_front.jpg',
    '02_PRINT_Card_Back_QR.png': CARD_BACK_OUT,
    # 2D preview composite
    '03_PREVIEW_Stage_2D.jpg':  preview_path,
    '04_PREVIEW_Stage_Render.jpg': 'output/stage_particles_preview.jpg',
    # Backdrop & plaque textures
    '05_Backdrop_Frosted_Glass.jpg': 'output/textures/card_stage_backdrop.jpg',
    '06_Gold_Plaque_Vandan_Riddhi.png': 'output/textures/stage_gold_plaque.png',
    # Couple cutout
    '07_Couple_Cutout_PNG.png': 'output/textures/foreground_cutout_ar.png',
    # Original photo
    '08_Original_Photo_JAI3712.jpg': 'output/JAI_3712.jpg',
    # Mask
    '09_Segmentation_Preview.jpg': 'output/segmentation_preview.jpg',
}

copied = []
for dest_name, src_path in deliverables.items():
    if os.path.exists(src_path):
        dest = os.path.join(OUT_FOLDER, dest_name)
        shutil.copy2(src_path, dest)
        size_kb = os.path.getsize(dest) // 1024
        copied.append(f'  ✓ {dest_name} ({size_kb} KB)')
        print(f'Copied: {src_path} -> {dest_name}')
    else:
        print(f'MISSING: {src_path}')

print(f'\n=== Done! {len(copied)} files saved to Desktop folder ===')
print(f'Folder: {OUT_FOLDER}')
for c in copied:
    print(c)
