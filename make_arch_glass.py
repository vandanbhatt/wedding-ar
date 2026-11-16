"""
Clean solid frosted-glass arch — no vignette, no bleed, correct arch shape.
Also fix bottom date text 29.12.2027 → 29.1.2027 on the card.
"""
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import subprocess, os

OUT = 'output/textures/card_stage_backdrop.jpg'
TMP = 'output/textures/card_stage_backdrop_orig.jpg'

# Restore from git commit BEFORE any glass (the clean date-corrected version)
result = subprocess.run(
    ['git', 'show', '423e12d:output/textures/card_stage_backdrop.jpg'],
    capture_output=True
)
if result.returncode == 0 and result.stdout:
    with open(TMP, 'wb') as f:
        f.write(result.stdout)
    src_path = TMP
else:
    src_path = OUT

img  = Image.open(src_path).convert('RGBA')
w, h = img.size   # 726 x 1024

# ── Arch geometry (matches the Canva card arch precisely) ─────────────────────
# Arch inner window: left 15% → right 85%, top 23% → bottom 77%
ax0 = int(w * 0.155)
ax1 = int(w * 0.845)
ay0 = int(h * 0.225)   # just below the gold ornament
ay1 = int(h * 0.775)
aw  = ax1 - ax0
# Arch top semicircle centre-y = ay0 + aw/2
semi_top = ay0
semi_bot = ay0 + aw

# ── Create arch mask ──────────────────────────────────────────────────────────
mask = Image.new('L', (w, h), 0)
md = ImageDraw.Draw(mask)
md.ellipse([ax0, semi_top, ax1, semi_bot], fill=255)        # top dome
md.rectangle([ax0, semi_top + aw//2, ax1, ay1], fill=255)  # rectangular body below dome

# Smooth just the outer edge slightly
mask = mask.filter(ImageFilter.GaussianBlur(radius=1))

# ── Blush-cream glass colour (exact card background colour) ───────────────────
# Sampled from card bg: (249, 237, 232)
GLASS = (249, 237, 232, 255)
glass_layer = Image.new('RGBA', (w, h), GLASS)

# Apply glass inside arch
out_img = Image.composite(glass_layer, img, mask)

# ── Fix bottom date: inpaint "29.12.2027" → "29.1.2027" ──────────────────────
# The old date text sits around y: 88%–91%, centred at x: 36%
# Cover with card BG colour, then write new date
draw = ImageDraw.Draw(out_img)
# Cover old date area
old_x0 = int(w * 0.20)
old_x1 = int(w * 0.80)
old_y0 = int(h * 0.875)
old_y1 = int(h * 0.908)
draw.rectangle([old_x0, old_y0, old_x1, old_y1], fill=(249, 237, 232, 255))

# Write new date
new_date = "29 . 1 . 2027"
font = None
for fn in ['output/Cinzel.ttf','georgiaz.ttf','timesbi.ttf','georgia.ttf','times.ttf']:
    try:
        font = ImageFont.truetype(fn, 32)
        break
    except: pass
if font is None:
    font = ImageFont.load_default()

bb = draw.textbbox((0,0), new_date, font=font)
tw = bb[2]-bb[0]
tx = (w - tw)//2
ty = old_y0 + 4
draw.text((tx+1, ty+1), new_date, font=font, fill=(255,245,230,255))  # highlight
draw.text((tx, ty),   new_date, font=font, fill=(139,105,55,255))     # gold text

# ── Save ───────────────────────────────────────────────────────────────────────
out_rgb = Image.new('RGB', (w, h), (255, 255, 255))
out_rgb.paste(out_img, mask=out_img.split()[3])
out_rgb.save(OUT, format='JPEG', quality=94)
print(f'Clean frosted glass arch saved -> {OUT}')

if os.path.exists(TMP):
    os.remove(TMP)
