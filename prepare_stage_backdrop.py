import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def prepare_backdrop():
    # 1. Load card
    card = Image.open('card_front.jpg').convert('RGB')
    cw, ch = card.size # 726 x 1024
    
    # 2. Load original photo for clean garden foliage
    photo = Image.open('JAI_3712.JPG')
    pw, ph = photo.size
    
    # Crop pure green background from left side of photo (X: 100..1500, Y: 1400..3200)
    garden_bg = photo.crop((100, 1400, 1500, 3200)).resize((483, 574), Image.Resampling.LANCZOS)
    # Apply subtle romantic soft-focus blur to background
    garden_bg = garden_bg.filter(ImageFilter.GaussianBlur(3))
    
    # 3. Create arch mask
    # Arch in card_front: X: 121..604 (w=483), Y: 190..764 (h=574)
    # The arch has a curved semi-circle top and vertical rectangular bottom
    arch_w, arch_h = 483, 574
    arch_mask = Image.new('L', (arch_w, arch_h), 0)
    adraw = ImageDraw.Draw(arch_mask)
    # Semi-circle top: radius = arch_w / 2 = 241.5
    radius = arch_w // 2
    adraw.pieslice((0, 0, arch_w, arch_w), 180, 360, fill=255)
    # Rectangular bottom
    adraw.rectangle((0, radius, arch_w, arch_h), fill=255)
    arch_mask = arch_mask.filter(ImageFilter.GaussianBlur(2))
    
    # 4. Composite clean garden into card arch
    card_composite = card.copy()
    card_composite.paste(garden_bg, (121, 190), arch_mask)
    
    # 5. Make the wedding date prominently visible at the top as well as the bottom!
    # Top has "SAVE THE DATE". Let's add the wedding date "29 . 12 . 2027" cleanly below "SAVE THE DATE"
    # in an elegant gold serif style matching the card typography
    draw = ImageDraw.Draw(card_composite)
    
    # Try loading a serif font, or use default with clean styling
    font_date = None
    for font_name in ["times.ttf", "georgia.ttf", "cinzel.ttf", "arial.ttf"]:
        try:
            font_date = ImageFont.truetype(font_name, 26)
            break
        except:
            continue
    if font_date is None:
        font_date = ImageFont.load_default()
        
    date_text = "29 . 12 . 2027"
    # Measure text
    bbox = draw.textbbox((0, 0), date_text, font=font_date)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # Place right below "SAVE THE DATE" at Y=168 (centered horizontally)
    tx = (cw - tw) // 2
    ty = 168
    
    # Subtle drop shadow for text
    draw.text((tx + 1, ty + 1), date_text, font=font_date, fill=(160, 130, 95))
    # Elegant gold/bronze color matching "SAVE THE DATE" (#8B6D45)
    draw.text((tx, ty), date_text, font=font_date, fill=(138, 105, 68))
    
    out_path = 'output/textures/card_stage_backdrop.jpg'
    card_composite.save(out_path, format='JPEG', quality=95)
    print(f'Clean card backdrop saved to {out_path}!')

def prepare_gold_plaque():
    # Create an ultra-luxurious champagne-gold inscribed plaque for the front of the stage base:
    # "Vandan & Riddhi"
    # "29.12.2027"
    pw, ph = 800, 240
    plaque = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(plaque)
    
    # Metallic gold background rectangle with rounded corners
    margin = 8
    pdraw.rounded_rectangle((margin, margin, pw - margin, ph - margin), radius=28, fill=(232, 205, 145, 250), outline=(255, 235, 185, 255), width=4)
    # Inner border
    pdraw.rounded_rectangle((margin + 8, margin + 8, pw - margin - 8, ph - margin - 8), radius=22, outline=(180, 145, 80, 200), width=2)
    
    font_names = None
    font_date = None
    for font_name in ["georgiaz.ttf", "timesbi.ttf", "georgia.ttf", "times.ttf"]:
        try:
            font_names = ImageFont.truetype(font_name, 52)
            font_date = ImageFont.truetype(font_name, 38)
            break
        except:
            continue
    if font_names is None:
        font_names = ImageFont.load_default()
        font_date = ImageFont.load_default()
        
    names_text = "Vandan & Riddhi"
    date_text = "29 . 12 . 2027"
    
    # Draw Names centered
    nb = pdraw.textbbox((0, 0), names_text, font=font_names)
    nw = nb[2] - nb[0]
    pdraw.text(((pw - nw) // 2 + 1, 48 + 1), names_text, font=font_names, fill=(255, 245, 220))
    pdraw.text(((pw - nw) // 2, 48), names_text, font=font_names, fill=(75, 52, 24))
    
    # Draw Date centered
    db = pdraw.textbbox((0, 0), date_text, font=font_date)
    dw = db[2] - db[0]
    pdraw.text(((pw - dw) // 2 + 1, 130 + 1), date_text, font=font_date, fill=(255, 245, 220))
    pdraw.text(((pw - dw) // 2, 130), date_text, font=font_date, fill=(90, 65, 32))
    
    plaque_path = 'output/textures/stage_gold_plaque.png'
    plaque.save(plaque_path, format='PNG')
    print(f'Gold plaque saved to {plaque_path}!')

if __name__ == '__main__':
    prepare_backdrop()
    prepare_gold_plaque()
