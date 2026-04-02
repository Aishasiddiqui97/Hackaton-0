"""
Create a simple test image for Instagram posting
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create a 1080x1080 image (Instagram square format)
img = Image.new('RGB', (1080, 1080), color='#4158D0')

# Add gradient effect
draw = ImageDraw.Draw(img)
for i in range(1080):
    # Create a gradient from blue to purple
    r = int(65 + (193 - 65) * i / 1080)
    g = int(88 + (94 - 88) * i / 1080)
    b = int(208 + (251 - 208) * i / 1080)
    draw.line([(0, i), (1080, i)], fill=(r, g, b))

# Add text
try:
    # Try to use a nice font
    font = ImageFont.truetype("arial.ttf", 80)
    font_small = ImageFont.truetype("arial.ttf", 40)
except:
    # Fallback to default font
    font = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Add text with shadow effect
text = "Test Post"
subtext = "Automated by AI"

# Shadow
draw.text((542, 492), text, font=font, fill='black')
draw.text((542, 592), subtext, font=font_small, fill='black')

# Main text
draw.text((540, 490), text, font=font, fill='white')
draw.text((540, 590), subtext, font=font_small, fill='white')

# Save the image
output_path = "AI_Employee_Vault/test_image.jpg"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
img.save(output_path, quality=95)

print(f"Test image created: {output_path}")
print(f"Image size: {img.size}")
