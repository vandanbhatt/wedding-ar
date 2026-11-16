import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def render_high_visibility_back():
    print("Rendering card back with MyWebAR QR and rivawedding.online...")
    
    # 1. Load cleaned background
    card = Image.open('output/cleaned_card_back.jpg').convert('RGB')
    cw, ch = card.size # 726 x 1024
    draw = ImageDraw.Draw(card)
    
    # 2. Typography fonts
    font_cinzel_path = 'output/Cinzel.ttf'
    try:
        font_top_l1 = ImageFont.truetype(font_cinzel_path, 25)
        font_top_l2 = ImageFont.truetype(font_cinzel_path, 32)
        font_web = ImageFont.truetype(font_cinzel_path, 21)
    except:
        font_top_l1 = ImageFont.truetype('georgiab.ttf', 24)
        font_top_l2 = ImageFont.truetype('georgiab.ttf', 30)
        font_web = ImageFont.truetype('georgiab.ttf', 20)
        
    font_bot_l1 = ImageFont.truetype('georgiaz.ttf', 25)
    font_bot_l2 = ImageFont.truetype('georgiaz.ttf', 22)
    
    text_color = (88, 62, 32)      # Deep royal bronze-gold #583E20
    shadow_color = (215, 190, 150) # Subtle champagne glow #D7BE96
    
    def draw_centered_text(y, text, font, tracking=2):
        spaced_text = " ".join(list(text)) if tracking > 0 else text
        bbox = draw.textbbox((0, 0), spaced_text, font=font)
        tw = bbox[2] - bbox[0]
        tx = (cw - tw) // 2
        draw.text((tx + 1, y + 1), spaced_text, font=font, fill=shadow_color)
        draw.text((tx, y), spaced_text, font=font, fill=text_color)
        return y + (bbox[3] - bbox[1])
    
    # 3. Top Text (Above QR Code)
    draw_centered_text(288, "SCAN FOR OUR", font_top_l1, tracking=2)
    draw_centered_text(326, "AR EXPERIENCE", font_top_l2, tracking=2)
    
    # 4. Insert Exact MyWebAR QR Code in White Box
    qr_img = Image.open('C:/Users/vanda/.gemini/antigravity/brain/3133c024-35e5-486e-ba77-581008b91f2d/.user_uploaded/media_1794870023697_b0324c51.png').convert('RGB')
    box_x, box_y, box_w, box_h = 227, 378, 272, 267
    target_qr_size = min(box_w, box_h) - 16 # ~251px
    qr_resized = qr_img.resize((target_qr_size, target_qr_size), Image.Resampling.LANCZOS)
    
    paste_x = box_x + (box_w - target_qr_size) // 2
    paste_y = box_y + (box_h - target_qr_size) // 2
    card.paste(qr_resized, (paste_x, paste_y))
    
    # 5. Bottom Instructions (Below Phone Icon)
    def draw_centered_bottom(y, text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        tx = (cw - tw) // 2
        draw.text((tx + 1, y + 1), text, font=font, fill=shadow_color)
        draw.text((tx, y), text, font=font, fill=text_color)
        return y + (bbox[3] - bbox[1])
        
    draw_centered_bottom(718, "Tap your phone here", font_bot_l1)
    draw_centered_bottom(750, "for the AR experience", font_bot_l2)
    
    # 6. Wedding Website URL (Prominently displayed)
    div_y = 794
    div_w = 120
    draw.line(((cw - div_w)//2, div_y, (cw + div_w)//2, div_y), fill=(185, 150, 100), width=1)
    
    draw_centered_text(808, "rivawedding.online", font_web, tracking=1)
    
    # 7. Save final production file
    out_path = 'output/vandan_riddhi_card_back_with_qr.png'
    card.save(out_path, format='PNG', quality=100)
    preview_path = 'output/card_back_high_visibility_preview.jpg'
    card.save(preview_path, format='JPEG', quality=95)
    print(f"Card back with website saved to {out_path} and {preview_path}!")

if __name__ == '__main__':
    render_high_visibility_back()
