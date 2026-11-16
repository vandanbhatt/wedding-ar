# Vandan & Riddhi – 3D Wedding WebAR Asset & Physical Card Pipeline

A luxury 2.5D holographic 3D augmented reality wedding model and physical card production pipeline engineered for **Vandan & Riddhi's Wedding Save-the-Date Card**.

When guests tap their phone on the physical NFC PVC card or scan the QR code on the back, and point their camera at the front of the card, **Vandan and Riddhi pop out in full three-dimensional depth** directly from the printed floral arch!

---

## 💎 Identity & Photographic Fidelity Guarantee

- **Zero Face Modification:** Both Vandan and Riddhi's original faces, facial expressions, smiles, skin tones, hair details, and traditional jewelry have been preserved bit-for-bit with 100% photographic pixel fidelity.
- **No AI Facial Replacement:** Absolutely no synthetic redraws, AI faces, or beauty filters were applied.
- **Alpha-Only Background Separation:** Neural human segmentation was used strictly to generate an ultra-clean alpha matte without modifying any RGB color pixels.

---

## 📦 Package Contents & File Structure

```text
output/
├── vandan_riddhi_card_3D_AR.glb       # Card-Matched WebAR Model (aligns with Canva card arch, 596 KB)
├── vandan_riddhi_card_3D_AR.blend     # Blender scene for the card-matched model
├── vandan_riddhi_card_back_with_qr.png# High-res printable back of card with QR code inserted
├── vandan_riddhi_card_render_3d_angle.png # 3D perspective render of the card pop-out
│
├── vandan_riddhi_3D_AR.glb            # Deluxe Garden Photo 3D Model with gold frame & backing (8.2 MB)
├── vandan_riddhi_3D_AR.blend          # Blender scene for deluxe garden photo model
├── vandan_riddhi_render_front.png     # Front-facing studio camera render preview
├── vandan_riddhi_render_3d_angle.png  # 3D perspective angle render preview
│
├── vandan_riddhi_cutout.png           # Master couple cutout (3712 x 5568 RGBA PNG, 25.5 MB)
├── mask_preview.png                   # High-contrast alpha mask preview (3712 x 5568 Grayscale)
├── segmentation_preview.jpg           # 3-Panel QA preview (Original | Alpha Matte | Composite)
├── JAI_3712.jpg                       # Original master photograph
├── index.html                         # Interactive 3D Web viewer with live model toggle
├── generate_3d_ar_model.py            # Master script for photo model
└── README.md                          # Complete production & deployment guide
```

---

## 🎯 The Two 3D AR Models Explained

| Model File | Size | Aspect Ratio | Best Used For |
| :--- | :--- | :--- | :--- |
| **`vandan_riddhi_card_3D_AR.glb`** *(Recommended)* | **596 KB** | Standard Card (1 : 1.41) | **Scanning the physical printed Save-the-Date card.** Calibrated with SIFT computer vision to pop out precisely over the printed Canva floral arch. Ultralight for lightning-fast mobile loading. |
| **`vandan_riddhi_3D_AR.glb`** | **8.20 MB** | Photographic (2 : 3) | **Standalone WebAR & 3D website showcase.** Features the lush original green garden photograph on a textured plane with champagne gold beveled borders, soft ambient contact shadows, and luxury backing. |

---

## 🚀 End-to-End Production Guide (4 Steps)

### Step 1: Canva Layout & Physical Card Dimensions
- **Standard Credit Card / PVC Size:** $85.6\text{ mm} \times 53.98\text{ mm}$ ($3.375\text{ in} \times 2.125\text{ in}$), ratio $\approx 0.709$ ($1 : 1.41$).
- **Front Artwork:** Use your front card design with the floral arch.
- **Back Artwork:** Use `output/vandan_riddhi_card_back_with_qr.png`. The high-resolution QR code has already been centered inside the white box below *"SCAN FOR OUR AR EXPERIENCE"* and above *"Tap your phone here for the AR experience"*.

### Step 2: Assets & 3D Pop-Up Mapping
- We generated the master cutout `output/vandan_riddhi_cutout.png` (3712 × 5568) with 100% original RGB pixels intact.
- In `vandan_riddhi_card_3D_AR.glb`, the couple is positioned exactly over the arch coordinates with $+2.8\text{ cm}$ Z-depth pop-out and ambient drop shadow.

### Step 3: WebAR Platform Setup (MyWebAR, Zapworks, MindAR, or 8th Wall)
1. **Target Image:** Upload your front card image (`card_front.jpg`) as the AR tracking marker / image target.
2. **Overlay Model:** Upload `output/vandan_riddhi_card_3D_AR.glb`.
3. **Alignment:** Set position to `(0, 0, 0)`. The card backing matches the paper surface, while Vandan & Riddhi pop out forward in 3D.
4. **Publish:** Publish your project on the WebAR platform to get a live URL (e.g., `https://mywebar.com/p/vandan-riddhi`).
   *(Note: You can update the QR code anytime if your production domain changes.)*

### Step 4: NFC Encoding & Card Printing
1. **Get Cards:** Purchase blank, printable **NTAG215 PVC cards** (CR80 standard credit card size, 30 mil thickness).
2. **Encode the URL:**
   - Download the free **NFC Tools** app (available on iOS and Android).
   - In NFC Tools, tap **Write** $\rightarrow$ **Add a record** $\rightarrow$ **URL / URI**.
   - Paste your WebAR URL.
   - Tap **Write / Tap to Write**, and hold the blank PVC card against the top of your phone until it chirps "Write complete".
3. **Print Cards:**
   - Print directly onto the PVC cards using a dedicated dye-sublimation PVC card printer (e.g. Evolis Primacy, Zebra ZC300, Fargo DTC1250e), or order custom printed NTAG215 cards from card manufacturers like SmartCardAmerica or GotPrint by sending them the front artwork and `output/vandan_riddhi_card_back_with_qr.png`.

---

## 💻 Local 3D Model Inspection

A local Web server is serving `output/`:
- Open your browser to: **`http://localhost:8080/index.html`**
- Use the toggle buttons at the top to switch between the **Save the Date Card 3D Pop-Out** and the **Garden Photo 2.5D Frame**.
- On Android / iOS, open `http://<your-computer-ip>:8080/index.html` on your mobile phone connected to the same Wi-Fi network to test direct WebAR in your living room!
