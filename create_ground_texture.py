import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def create_ground_texture():
    size = 1024
    # Base grass
    grass = Image.open('output/textures/grass_tile.jpg').resize((size, size), Image.Resampling.LANCZOS)
    
    # Create circular / oval alpha mask
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    margin = 40
    draw.ellipse((margin, margin, size - margin, size - margin), fill=255)
    
    # Soften outer edge
    mask = mask.filter(ImageFilter.GaussianBlur(12))
    
    # Vignette overlay for depth
    vignette = Image.new('L', (size, size), 255)
    vdraw = ImageDraw.Draw(vignette)
    for r in range(0, size // 2, 8):
        alpha = int(255 * (1.0 - (r / (size / 2)) ** 2 * 0.35))
        vdraw.ellipse((size//2 - r, size//2 - r, size//2 + r, size//2 + r), fill=alpha)
    vignette = vignette.filter(ImageFilter.GaussianBlur(16))
    
    # Blend vignette onto grass
    grass_np = np.array(grass).astype(float)
    vig_np = np.array(vignette).astype(float) / 255.0
    grass_shaded = (grass_np * vig_np[:, :, None]).clip(0, 255).astype(np.uint8)
    ground_rgba = Image.fromarray(grass_shaded).convert('RGBA')
    
    # Add romantic scattered rose petals (blush pink and coral gold)
    petal_draw = ImageDraw.Draw(ground_rgba)
    np.random.seed(42)
    # Scatter ~35 petals around the edges and near front
    for _ in range(35):
        angle = np.random.uniform(0, 2 * np.pi)
        dist = np.random.uniform(size * 0.25, size * 0.44)
        px = int(size / 2 + np.cos(angle) * dist)
        py = int(size / 2 + np.sin(angle) * dist * 0.8)  # slight oval perspective
        
        prx = np.random.randint(8, 18)
        pry = np.random.randint(5, 12)
        rot = np.random.uniform(0, 180)
        
        # Color: blush pink #E8A598 with variations
        r_c = np.random.randint(220, 245)
        g_c = np.random.randint(150, 175)
        b_c = np.random.randint(150, 170)
        alpha_c = np.random.randint(210, 255)
        
        petal_img = Image.new('RGBA', (prx * 4, pry * 4), (0, 0, 0, 0))
        p_draw = ImageDraw.Draw(petal_img)
        p_draw.ellipse((prx, pry, prx * 3, pry * 3), fill=(r_c, g_c, b_c, alpha_c))
        petal_img = petal_img.rotate(rot, resample=Image.Resampling.BICUBIC)
        ground_rgba.paste(petal_img, (px - prx * 2, py - pry * 2), petal_img)

    # Ambient Contact Shadow in center where couple stands
    shadow_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_layer)
    # Contact shadow oval
    cx, cy = size // 2, size // 2 + 30
    sw, sh = 260, 70
    s_draw.ellipse((cx - sw, cy - sh, cx + sw, cy + sh), fill=(10, 15, 8, 180))
    # Core contact shadow
    s_draw.ellipse((cx - sw + 40, cy - sh + 15, cx + sw - 40, cy + sh - 15), fill=(5, 8, 5, 230))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(18))
    
    # Composite shadow onto ground
    final_ground = Image.alpha_composite(ground_rgba, shadow_layer)
    
    # Apply outer circular mask
    final_ground.putalpha(mask)
    
    out_path = 'output/textures/ground_lawn.png'
    final_ground.save(out_path)
    print(f'Ground lawn texture created: {out_path}')

if __name__ == '__main__':
    create_ground_texture()
