import math
import random
import os

languages = [
    "I love you", "Te amo", "Je t'aime", "Ich liebe dich", "Ti amo", "Eu te amo", 
    "Ik hou van jou", "Я тебя люблю", "愛してる", "사랑해", "我爱你", "أحبك", 
    "मैं तुमसे प्यार करता हूँ", "আমি তোমাকে ভালোবাসি", "Seni seviyorum", "Σ' αγαπώ", 
    "Kocham cię", "Jag älskar dig", "ฉันรักเธอ", "Anh yêu em", "Aku cinta kamu", 
    "Nakupenda", "Miluji tě", "Jeg elsker dig", "Rakastan sinua", "Szeretlek", 
    "Jeg elsker deg", "Te iubesc", "Milujem ťa", "Mahal kita", "Te dua", "Saya cinta padamu",
    "S'ayapaw", "Obicham te"
]

def get_text_size(text, font_size):
    # approximate width and height
    # Make bounding boxes slightly smaller to allow tight packing
    return len(text) * font_size * 0.40, font_size * 0.8

placed_boxes = []

def check_overlap(x, y, w, h):
    for (bx, by, bw, bh) in placed_boxes:
        if abs(x - bx) < (w + bw) / 2 and abs(y - by) < (h + bh) / 2:
            return True
    return False

CENTER_RADIUS = 190
PETAL_LENGTH = 150
NUM_PETALS = 18

def get_part(x, y):
    r = math.sqrt(x**2 + y**2)
    theta = math.atan2(y, x)
    
    # Dead zone for the central word "Mumu"
    if r < 40:
        return None
        
    # Stem
    if -12 < x < 12 and y >= 0 and y < 800:
        return "stem"
        
    # Leaves (made much larger and distinct)
    if 300 < y < 450:
        leaf_x_max = 160 * math.sin((y - 300) / 150 * math.pi)
        if 12 < x < 12 + leaf_x_max:
            return "leaf"
            
    if 500 < y < 650:
        leaf_x_max = 160 * math.sin((y - 500) / 150 * math.pi)
        if -12 - leaf_x_max < x < -12:
            return "leaf"
            
    # Petals calculation
    angle_slice = 2 * math.pi / NUM_PETALS
    theta_mod = (theta % angle_slice) / angle_slice
    
    # Use 0.5 power to make petals fat and wide at the base, leaving tight V-shaped gaps
    petal_shape = math.sin(theta_mod * math.pi) ** 0.5
    r_petal = CENTER_RADIUS + PETAL_LENGTH * petal_shape
    
    if r < CENTER_RADIUS:
        return "center"
    elif r < r_petal:
        return "petal"
        
    return None

def is_fully_inside(x, y, w, h, expected_part):
    # Check if the 4 corners of the word are inside the same part
    for dx in [-w/2.0, w/2.0]:
        for dy in [-h/2.0, h/2.0]:
            if get_part(x + dx, y + dy) != expected_part:
                return False
    return True

c = 3.0 # Very dense packing
points = []
for n in range(1, 40000):
    r = c * math.sqrt(n)
    theta = n * 137.508 * math.pi / 180
    
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    
    # Also add some random points for the stem/leaves to ensure they are filled
    # since Fermat spiral is circular
    
points_to_check = []
# Add spiral points
for n in range(1, 50000):
    r = c * math.sqrt(n)
    theta = n * 137.508 * math.pi / 180
    points_to_check.append((r * math.cos(theta), r * math.sin(theta)))

# Add completely random points to find small gaps and petal tips
for _ in range(30000):
    r = random.uniform(CENTER_RADIUS, CENTER_RADIUS + PETAL_LENGTH)
    theta = random.uniform(0, 2 * math.pi)
    points_to_check.append((r * math.cos(theta), r * math.sin(theta)))

# Add linear points for stem and leaves
for _ in range(20000):
    points_to_check.append((random.uniform(-160, 160), random.uniform(150, 850)))

html_parts = []
delay = 0.0

# Sort points by radius so it blooms from center outwards
points_to_check.sort(key=lambda p: math.sqrt(p[0]**2 + p[1]**2))

for x, y in points_to_check:
    part_type = get_part(x, y)
    if not part_type:
        continue
        
    word = random.choice(languages)
    
    if part_type == "center":
        font_size = random.randint(7, 10) # Very small for dense seeds
    elif part_type == "petal":
        font_size = random.randint(10, 15)
    else:
        font_size = random.randint(11, 16)
        
    w, h = get_text_size(word, font_size)
    
    if is_fully_inside(x, y, w, h, part_type) and not check_overlap(x, y, w, h):
        placed_boxes.append((x, y, w, h))
        
        if part_type == "center":
            # Dark colors for the center
            r_dist = math.sqrt(x**2 + y**2)
            if r_dist < CENTER_RADIUS * 0.6:
                color = random.choice(["#0a0500", "#1a0b00", "#241000", "#000000"])
            else:
                color = random.choice(["#3E2723", "#4E342E", "#2D1A11", "#1a0b00"])
        elif part_type == "petal":
            # Bright yellow/gold for petals
            color = random.choice(["#FFD700", "#FFC107", "#FFCA28", "#FFB300", "#FFA000", "#FFE082"])
        else: # stem or leaf
            color = random.choice(["#2E7D32", "#388E3C", "#43A047", "#1B5E20"])
            
        left = 500 + x
        top = 350 + y
        html_parts.append(f'<div class="word" style="left:{left:.1f}px; top:{top:.1f}px; color:{color}; font-size:{font_size}px; animation-delay:{delay:.2f}s;">{word}</div>')
        delay += 0.02 # Faster animation since there are more words

# Add Mumu in Arabic in the center
html_parts.append(f'<div class="word" style="left:500px; top:350px; color:#FFD700; font-size:65px; font-weight:bold; animation-delay:0s; text-shadow: 0px 0px 20px rgba(255, 215, 0, 0.5);">مومو</div>')

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sunflower of Love</title>
<style>
  body {{
    background-color: #050505;
    margin: 0;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    color: white;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }}
  .container {{
    position: relative;
    width: 1000px;
    height: 1200px;
    transform: scale(0.65);
  }}
  .word {{
    position: absolute;
    white-space: nowrap;
    opacity: 0;
    font-weight: bold;
    animation: fadeIn 1s forwards;
    transform: translate(-50%, -50%);
    text-shadow: 0 0 5px rgba(0,0,0,0.8);
  }}
  @keyframes fadeIn {{
    0% {{ opacity: 0; transform: translate(-50%, -50%) scale(0.5); }}
    100% {{ opacity: 1; transform: translate(-50%, -50%) scale(1); }}
  }}
</style>
</head>
<body>
<div class="container">
{"".join(html_parts)}
</div>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"Generated index.html with {len(html_parts)} words!")
