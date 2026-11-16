"""
Replace the arch window area on the card backdrop with a frosted-glass effect.
The arch is roughly centred horizontally, starts ~25% from top, ends ~75% from top.
Frosted glass = heavy gaussian blur of original content + white semi-opaque veil.
"""
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

BACKDROP = 'output/textures/card_stage_backdrop.jpg'
OUT      = 'output/textures/card_stage_backdrop.jpg'

img  = Image.open(BACKDROP).convert('RGBA')
w, h = img.size   # 726 x 1024

# ── Define the arch shape ────────────────────────────────────────────────────
# Arch = rounded-top rectangle
# Approximate bounds based on the Canva card design:
arch_x0 = int(w * 0.14)   # left edge of arch
arch_x1 = int(w * 0.86)   # right edge
arch_y0  = int(h * 0.26)  # top of arch (where the round starts)
arch_y1  = int(h * 0.76)  # bottom of arch
arch_cx  = (arch_x0 + arch_x1) // 2
arch_w   = arch_x1 - arch_x0
arch_r   = arch_w // 2    # radius of the top semicircle

# ── Create arch mask ─────────────────────────────────────────────────────────
mask = Image.new('L', (w, h), 0)
md = ImageDraw.Draw(mask)
# Rectangular body (below the semicircle centre)
rect_y0 = arch_y0 + arch_r
md.rectangle([arch_x0, rect_y0, arch_x1, arch_y1], fill=255)
# Semicircle top
md.ellipse([arch_x0, arch_y0, arch_x1, arch_y0 + arch_w], fill=255)

# Feather mask edges for smooth blend
mask = mask.filter(ImageFilter.GaussianBlur(radius=6))

# ── Frosted glass layer ───────────────────────────────────────────────────────
# Step 1: heavily blur the original image content inside arch
blurred = img.filter(ImageFilter.GaussianBlur(radius=22))

# Step 2: create a soft white frosted glass layer
glass = Image.new('RGBA', (w, h), (245, 238, 232, 230))  # warm white, more opaque = milky glass

# Step 3: Composite: original + blur + glass veil
# Within arch area: use blurred original, then overlay glass
frosted = Image.composite(blurred, img, mask)
frosted = Image.composite(glass, frosted, mask)

# Step 4: Slight tint — add a very subtle blush-pink warmth to match card palette
tint = Image.new('RGBA', (w, h), (255, 230, 220, 30))
frosted = Image.alpha_composite(frosted, tint)

# Convert back to RGB for JPEG
out_rgb = Image.new('RGB', (w, h), (255, 255, 255))
out_rgb.paste(frosted, mask=frosted.split()[3])
out_rgb.save(OUT, format='JPEG', quality=92)
print(f'Frosted glass arch saved -> {OUT}')
print(f'Arch bounds: x={arch_x0}..{arch_x1}, y={arch_y0}..{arch_y1}')
