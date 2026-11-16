import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def prepare_gold_plaque():
    pw, ph = 800, 260
    plaque = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(plaque)
    
    # Metallic gold background rectangle with rounded corners
    margin = 8
    pdraw.rounded_rectangle((margin, margin, pw - margin, ph - margin), radius=28, fill=(232, 205, 145, 250), outline=(255, 235, 185, 255), width=4)
    # Inner border
    pdraw.rounded_rectangle((margin + 8, margin + 8, pw - margin - 8, ph - margin - 8), radius=22, outline=(180, 145, 80, 200), width=2)
    
    font_names = None
    font_date = None
    font_web = None
    for font_name in ["output/Cinzel.ttf", "georgiaz.ttf", "timesbi.ttf", "georgia.ttf", "times.ttf"]:
        try:
            font_names = ImageFont.truetype(font_name, 48)
            font_date = ImageFont.truetype(font_name, 34)
            font_web = ImageFont.truetype(font_name, 28)
            break
        except:
            continue
    if font_names is None:
        font_names = ImageFont.load_default()
        font_date = ImageFont.load_default()
        font_web = ImageFont.load_default()
        
    names_text = "Vandan & Riddhi"
    date_text = "29 . 1 . 2027"
    web_text = "rivawedding.online"
    
    # Draw Names centered
    nb = pdraw.textbbox((0, 0), names_text, font=font_names)
    nw = nb[2] - nb[0]
    pdraw.text(((pw - nw) // 2 + 1, 36 + 1), names_text, font=font_names, fill=(255, 245, 220))
    pdraw.text(((pw - nw) // 2, 36), names_text, font=font_names, fill=(75, 52, 24))
    
    # Draw Date centered
    db = pdraw.textbbox((0, 0), date_text, font=font_date)
    dw = db[2] - db[0]
    pdraw.text(((pw - dw) // 2 + 1, 108 + 1), date_text, font=font_date, fill=(255, 245, 220))
    pdraw.text(((pw - dw) // 2, 108), date_text, font=font_date, fill=(90, 65, 32))

    # Divider line
    div_y = 168
    pdraw.line((240, div_y, pw - 240, div_y), fill=(180, 145, 80), width=1)
    
    # Draw Website centered
    wb = pdraw.textbbox((0, 0), web_text, font=font_web)
    ww = wb[2] - wb[0]
    pdraw.text(((pw - ww) // 2 + 1, 185 + 1), web_text, font=font_web, fill=(255, 245, 220))
    pdraw.text(((pw - ww) // 2, 185), web_text, font=font_web, fill=(105, 75, 38))
    
    plaque_path = 'output/textures/stage_gold_plaque.png'
    plaque.save(plaque_path, format='PNG')
    print(f"Updated gold plaque with rivawedding.online saved to {plaque_path}!")

if __name__ == '__main__':
    prepare_gold_plaque()
