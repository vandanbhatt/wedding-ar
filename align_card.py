import cv2
import numpy as np

# Load card_front and original image
card = cv2.imread("card_front.jpg")
orig = cv2.imread("JAI_3712.jpg")

ch, cw = card.shape[:2]
oh, ow = orig.shape[:2]

# Crop the arched window region from card
arch_crop = card[200:764, 121:604]
cv2.imwrite("output/arch_crop.jpg", arch_crop)

# Let's detect SIFT / ORB features between orig and arch_crop to find exact homography / affine transform
sift = cv2.SIFT_create()
kp1, des1 = sift.detectAndCompute(orig, None)
kp2, des2 = sift.detectAndCompute(arch_crop, None)

bf = cv2.BFMatcher()
matches = bf.knnMatch(des1, des2, k=2)

good = []
for m, n in matches:
    if m.distance < 0.75 * n.distance:
        good.append(m)

print(f"Good SIFT feature matches: {len(good)}")

src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

# Estimate affine transform (scale, rotation, translation)
M, inliers = cv2.estimateAffinePartial2D(src_pts, dst_pts)
print("Affine Matrix:\n", M)

# Scale
scale = np.sqrt(M[0, 0]**2 + M[0, 1]**2)
angle = np.arctan2(M[0, 1], M[0, 0]) * 180 / np.pi
tx, ty = M[0, 2], M[1, 2]

print(f"Scale from orig to arch: {scale:.6f}")
print(f"Rotation angle: {angle:.2f} deg")
print(f"Translation in arch crop: tx={tx:.2f}, ty={ty:.2f}")

# Full card coordinates:
# Arch crop top-left is (121, 200)
card_tx = tx + 121
card_ty = ty + 200
print(f"Translation in card_front: tx={card_tx:.2f}, ty={card_ty:.2f}")

# Width and height of the original image scaled to card dimensions:
scaled_w = ow * scale
scaled_h = oh * scale
print(f"Scaled image dimensions on card: {scaled_w:.2f} x {scaled_h:.2f} px")
print(f"Image left: {card_tx:.2f}, right: {card_tx + scaled_w:.2f} (card width: {cw})")
print(f"Image top: {card_ty:.2f}, bottom: {card_ty + scaled_h:.2f} (card height: {ch})")
