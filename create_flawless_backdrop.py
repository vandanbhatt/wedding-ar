import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_flawless_backdrop():
    print("Creating flawless card backdrop with 100% pure garden (NO human pixels)...")
    
    # 1. Load card
    card = Image.open('card_front.jpg').convert('RGB')
    cw, ch = card.size # 726 x 1024
    
    # 2. Load photo and sample from Y: 50..1200 (PURE garden trees, above heads)
    photo = Image.open('JAI_3712.JPG')
    # Bounding box of pure trees: X: 800..2800, Y: 100..1200
    pure_garden = photo.crop((800, 100, 2800, 1200)).resize((483, 574), Image.Resampling.LANCZOS)
    pure_garden = pure_garden.filter(ImageFilter.GaussianBlur(2))
    
    # 3. Create exact arch mask
    arch_w, arch_h = 483, 574
    arch_mask = Image.new('L', (arch_w, arch_h), 0)
    adraw = ImageDraw.Draw(arch_mask)
    # Curved arch top
    adraw.pieslice((0, 0, arch_w, arch_w), 180, 360, fill=255)
    # Rectangular arch bottom
    adraw.rectangle((0, arch_w // 2, arch_w, arch_h), fill=255)
    arch_mask = arch_mask.filter(ImageFilter.GaussianBlur(2))
    
    # Paste pure garden into card
    card_clean = card.copy()
    card_clean.paste(pure_garden, (121, 190), arch_mask)
    
    # 4. Add prominent "29 . 12 . 2027" wedding date at the top below "SAVE THE DATE"
    draw = ImageDraw.Draw(card_clean)
    font_date = None
    for f in ["georgiaz.ttf", "timesbi.ttf", "georgia.ttf", "times.ttf", "arial.ttf"]:
        try:
            font_date = ImageFont.truetype(f, 28)
            break
        except:
            continue
    if font_date is None:
        font_date = ImageFont.load_default()
        
    date_str = "29 . 12 . 2027"
    bbox = draw.textbbox((0, 0), date_str, font=font_date)
    tw = bbox[2] - bbox[0]
    tx = (cw - tw) // 2
    ty = 168
    
    # Shadow + Gold/Bronze fill
    draw.text((tx + 1, ty + 1), date_str, font=font_date, fill=(180, 150, 110))
    draw.text((tx, ty), date_str, font=font_date, fill=(125, 95, 58))
    
    out_path = 'output/textures/card_stage_backdrop.jpg'
    card_clean.save(out_path, format='JPEG', quality=95)
    print(f"Flawless card backdrop saved to {out_path}!")

def create_flawless_grass_texture():
    print("Creating flawless 100% green grass texture...")
    size = 1024
    
    # Sample grass exclusively from bottom lawn (X: 2500..3600, Y: 2600..3800)
    photo = Image.open('JAI_3712.JPG')
    grass_crop = photo.crop((2500, 2600, 3600, 3800)).resize((size, size), Image.Resampling.LANCZOS)
    
    # Ensure rich, pure lawn green tone
    g_np = np.array(grass_crop).astype(float)
    g_np[:, :, 1] = np.clip(g_np[:, :, 1] * 1.10, 0, 255) # boost green
    g_np[:, :, 0] = np.clip(g_np[:, :, 0] * 0.90, 0, 255) # reduce red
    g_np[:, :, 2] = np.clip(g_np[:, :, 2] * 0.90, 0, 255) # reduce blue
    
    grass_img = Image.fromarray(g_np.astype(np.uint8)).convert('RGBA')
    
    # Circular mask with smooth edge
    mask = Image.new('L', (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    margin = 25
    mdraw.ellipse((margin, margin, size - margin, size - margin), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(8))
    
    # Subtle vignette
    vignette = Image.new('L', (size, size), 255)
    vdraw = ImageDraw.Draw(vignette)
    for r in range(0, size // 2, 6):
        alpha = int(255 * (1.0 - (r / (size / 2)) ** 2 * 0.25))
        vdraw.ellipse((size//2 - r, size//2 - r, size//2 + r, size//2 + r), fill=alpha)
    vignette = vignette.filter(ImageFilter.GaussianBlur(16))
    
    vig_np = np.array(vignette).astype(float) / 255.0
    grass_shaded = (np.array(grass_img)[:,:,:3].astype(float) * vig_np[:, :, None]).clip(0, 255).astype(np.uint8)
    final_grass = Image.fromarray(grass_shaded).convert('RGBA')
    
    # Scatter delicate rose petals
    np.random.seed(777)
    for _ in range(45):
        angle = np.random.uniform(0, 2 * np.pi)
        dist = np.random.uniform(size * 0.20, size * 0.44)
        px = int(size / 2 + np.cos(angle) * dist)
        py = int(size / 2 + np.sin(angle) * dist * 0.72)
        
        prx = np.random.randint(9, 18)
        pry = np.random.randint(6, 11)
        rot = np.random.uniform(0, 180)
        
        p_img = Image.new('RGBA', (prx * 4, pry * 4), (0, 0, 0, 0))
        pdraw = ImageDraw.Draw(p_img)
        pdraw.ellipse((prx, pry, prx * 3, pry * 3), fill=(240, 160, 165, 240))
        p_img = p_img.rotate(rot, resample=Image.Resampling.BICUBIC)
        final_grass.paste(p_img, (px - prx * 2, py - pry * 2), p_img)
        
    # Ambient contact shadow
    shadow_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)
    cx, cy = size // 2, size // 2 + 20
    sdraw.ellipse((cx - 280, cy - 65, cx + 280, cy + 65), fill=(10, 16, 8, 170))
    sdraw.ellipse((cx - 220, cy - 45, cx + 220, cy + 45), fill=(5, 10, 4, 210))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(16))
    
    final_grass = Image.alpha_composite(final_grass, shadow_layer)
    final_grass.putalpha(mask)
    
    out_grass = 'output/textures/ground_pure_grass.png'
    final_grass.save(out_grass, format='PNG')
    print(f"Flawless grass texture saved to {out_grass}!")

if __name__ == '__main__':
    create_flawless_backdrop()
    create_flawless_grass_texture()
