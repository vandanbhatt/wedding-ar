import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def generate_pure_grass():
    size = 1024
    
    # 1. Load photo and sample exclusively from pure green lawn regions
    photo = Image.open('JAI_3712.JPG')
    pw, ph = photo.size
    
    # In JAI_3712.JPG, the right-hand background is lush green lawn and trees:
    # pw = 3712, ph = 5568
    # The lawn to the right of the couple is around X: 2400..3600, Y: 2800..4200
    lawn_crop = photo.crop((2400, 2800, 3600, 4000)).resize((size, size), Image.Resampling.LANCZOS)
    
    # Convert to numpy array to enhance vibrancy & rich emerald/garden green tone
    lawn_np = np.array(lawn_crop).astype(float)
    # Ensure rich lush green balance
    # Boost green channel slightly and balance exposure
    lawn_np[:, :, 1] = np.clip(lawn_np[:, :, 1] * 1.08, 0, 255) # Green
    lawn_np[:, :, 0] = np.clip(lawn_np[:, :, 0] * 0.95, 0, 255) # Red
    lawn_img = Image.fromarray(lawn_np.astype(np.uint8)).convert('RGBA')
    
    # 2. Circular / Oval mask
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    margin = 30
    draw.ellipse((margin, margin, size - margin, size - margin), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(10))
    
    # 3. Soft vignette
    vignette = Image.new('L', (size, size), 255)
    vdraw = ImageDraw.Draw(vignette)
    for r in range(0, size // 2, 6):
        alpha = int(255 * (1.0 - (r / (size / 2)) ** 2 * 0.30))
        vdraw.ellipse((size//2 - r, size//2 - r, size//2 + r, size//2 + r), fill=alpha)
    vignette = vignette.filter(ImageFilter.GaussianBlur(16))
    
    vig_np = np.array(vignette).astype(float) / 255.0
    lawn_shaded = (np.array(lawn_img)[:,:,:3].astype(float) * vig_np[:, :, None]).clip(0, 255).astype(np.uint8)
    ground_rgba = Image.fromarray(lawn_shaded).convert('RGBA')
    
    # 4. Add scattered blush rose petals on the grass
    np.random.seed(101)
    for _ in range(40):
        angle = np.random.uniform(0, 2 * np.pi)
        dist = np.random.uniform(size * 0.22, size * 0.44)
        px = int(size / 2 + np.cos(angle) * dist)
        py = int(size / 2 + np.sin(angle) * dist * 0.75)
        
        prx = np.random.randint(9, 17)
        pry = np.random.randint(6, 11)
        rot = np.random.uniform(0, 180)
        
        # Blush pink and delicate coral petals
        r_c = np.random.randint(225, 248)
        g_c = np.random.randint(145, 170)
        b_c = np.random.randint(150, 168)
        alpha_c = np.random.randint(220, 255)
        
        petal_img = Image.new('RGBA', (prx * 4, pry * 4), (0, 0, 0, 0))
        p_draw = ImageDraw.Draw(petal_img)
        p_draw.ellipse((prx, pry, prx * 3, pry * 3), fill=(r_c, g_c, b_c, alpha_c))
        petal_img = petal_img.rotate(rot, resample=Image.Resampling.BICUBIC)
        ground_rgba.paste(petal_img, (px - prx * 2, py - pry * 2), petal_img)

    # 5. Realistic ambient contact drop shadow where couple stands
    shadow_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_layer)
    cx, cy = size // 2, size // 2 + 20
    sw, sh = 280, 65
    s_draw.ellipse((cx - sw, cy - sh, cx + sw, cy + sh), fill=(8, 14, 6, 175))
    s_draw.ellipse((cx - sw + 50, cy - sh + 15, cx + sw - 50, cy + sh - 15), fill=(4, 8, 3, 220))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(16))
    
    final_ground = Image.alpha_composite(ground_rgba, shadow_layer)
    final_ground.putalpha(mask)
    
    out_path = 'output/textures/ground_pure_grass.png'
    final_ground.save(out_path, format='PNG')
    print(f'Pure grass ground texture saved to {out_path}!')

if __name__ == '__main__':
    generate_pure_grass()
