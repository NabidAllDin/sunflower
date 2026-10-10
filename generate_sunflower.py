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

short_languages = [
    "Te amo", "Ti amo", "Je t'aime", "Eu te amo", "Te dua", "사랑해", 
    "我爱你", "أحبك", "愛してる", "I love you", "Te iubesc", "Kocham cię", 
    "Miluji tě", "Szeretlek", "Σ' αγαπώ"
]

usage_count = {lang: 0 for lang in languages}

def get_char_width(ch, font_size):
    cp = ord(ch)
    if (0x4E00 <= cp <= 0x9FFF or 
        0x3040 <= cp <= 0x30FF or 
        0xAC00 <= cp <= 0xD7AF or
        0xFF00 <= cp <= 0xFFEF):
        return font_size * 1.10
    if (0x0980 <= cp <= 0x09FF or 0x0900 <= cp <= 0x097F or 0x0E00 <= cp <= 0x0E7F):
        return font_size * 0.85
    if (0x0600 <= cp <= 0x06FF or 0x0590 <= cp <= 0x05FF or 
        0x0370 <= cp <= 0x03FF or 0x0400 <= cp <= 0x04FF):
        return font_size * 0.70
    if ch in "WMmw":
        return font_size * 0.82
    if ch in "ijlIt f'":
        return font_size * 0.35
    if ch == ' ':
        return font_size * 0.30
    return font_size * 0.60

def get_text_size(text, font_size):
    w = sum(get_char_width(c, font_size) for c in text)
    h = font_size * 1.20
    return w, h

placed_boxes = []
PADDING_X = 3.5  # Zero overlap guaranteed
PADDING_Y = 2.5

def check_overlap(x, y, w, h):
    for (bx, by, bw, bh) in placed_boxes:
        if abs(x - bx) < (w + bw) / 2.0 + PADDING_X and abs(y - by) < (h + bh) / 2.0 + PADDING_Y:
            return True
    return False

# ── Sunflower Shape Geometry ──
# Center seed disk: solid circle of radius 175
CENTER_RADIUS = 175
# Petals: radiate outward by 130px (total radius 305px)
PETAL_LENGTH = 130
NUM_PETALS = 22  # 22 petals give dense, overlapping, crown-like flower head

def get_petal_max_r(theta):
    angle_slice = 2 * math.pi / NUM_PETALS
    theta_mod = (theta % angle_slice) / angle_slice
    # Petals are rounded with distinct points at tips
    petal_curve = math.sin(theta_mod * math.pi) ** 0.85
    return CENTER_RADIUS + PETAL_LENGTH * petal_curve

def is_inside_flower(x, y):
    r = math.sqrt(x * x + y * y)
    if r < 40:  # Dead zone for "مومو"
        return False
    theta = math.atan2(y, x)
    return r < get_petal_max_r(theta)

def is_inside_plant(x, y):
    # Main stem: straight down from flower base
    if -26 <= x <= 26 and 150 <= y <= 840:
        return True
    # Upper right broad sunflower leaf
    if 260 <= y <= 470:
        prog = (y - 260) / 210
        lx = 185 * (math.sin(prog * math.pi) ** 0.85)
        if 0 <= x <= 26 + lx:
            return True
    # Lower left broad sunflower leaf
    if 480 <= y <= 690:
        prog = (y - 480) / 210
        lx = 185 * (math.sin(prog * math.pi) ** 0.85)
        if -26 - lx <= x <= 0:
            return True
    return False

def can_place_flower_word(x, y, w, h):
    # Word center must be inside
    if not is_inside_flower(x, y):
        return False
    # Check bounding box points with slight margin for organic text contour
    test_pts = [
        (x - w * 0.45, y), (x + w * 0.45, y),
        (x, y - h * 0.45), (x, y + h * 0.45),
        (x - w * 0.40, y - h * 0.40), (x + w * 0.40, y - h * 0.40),
        (x - w * 0.40, y + h * 0.40), (x + w * 0.40, y + h * 0.40)
    ]
    for px, py in test_pts:
        if not is_inside_flower(px, py):
            return False
    return True

def can_place_plant_word(x, y, w, h):
    if not is_inside_plant(x, y):
        return False
    for dx in [-w * 0.45, w * 0.45]:
        for dy in [-h * 0.45, h * 0.45]:
            if not is_inside_plant(x + dx, y + dy):
                return False
    return True

def pick_balanced_word(candidate_pool):
    return sorted(candidate_pool, key=lambda w: (usage_count[w], random.random()))

# ── Sample Points ──
points_flower = []

# 1. Fermat spiral across center and petals
c = 2.1
for n in range(1, 45000):
    r = c * math.sqrt(n)
    if r > CENTER_RADIUS + PETAL_LENGTH + 5:
        break
    theta = n * 137.508 * math.pi / 180
    points_flower.append((r * math.cos(theta), r * math.sin(theta)))

# 2. Targeted Petal Spines for all 22 petals
for p_idx in range(NUM_PETALS):
    base_ang = p_idx * (2 * math.pi / NUM_PETALS) + (math.pi / NUM_PETALS)
    for r_step in range(int(CENTER_RADIUS + PETAL_LENGTH - 8), int(CENTER_RADIUS * 0.8), -6):
        for ang_offset in [-0.06, -0.03, 0.0, 0.03, 0.06]:
            ang = base_ang + ang_offset
            points_flower.append((r_step * math.cos(ang), r_step * math.sin(ang)))

# 3. Dense random jitter across flower
for _ in range(60000):
    r = random.uniform(38, CENTER_RADIUS + PETAL_LENGTH)
    theta = random.uniform(0, 2 * math.pi)
    points_flower.append((r * math.cos(theta), r * math.sin(theta)))

points_flower.sort(key=lambda p: math.sqrt(p[0]**2 + p[1]**2))

# Plant points
points_plant = []
for y_val in range(150, 845, 5):
    for x_val in range(-215, 215, 5):
        if is_inside_plant(x_val, y_val):
            points_plant.append((x_val + random.uniform(-2, 2), y_val + random.uniform(-2, 2)))

for _ in range(40000):
    x_val = random.uniform(-215, 215)
    y_val = random.uniform(150, 845)
    if is_inside_plant(x_val, y_val):
        points_plant.append((x_val, y_val))

points_plant.sort(key=lambda p: p[1])

html_parts = []
delay = 0.0

# ── 1. Place Flower Words ──
for x, y in points_flower:
    r = math.sqrt(x * x + y * y)
    is_center = (r < CENTER_RADIUS)
    
    # Outer petals prioritize shorter words so all 22 petals fill completely
    if r > CENTER_RADIUS + 35:
        candidates = pick_balanced_word(short_languages)
        font_size = random.randint(11, 14)
    elif is_center:
        candidates = pick_balanced_word(languages)
        font_size = random.randint(10, 13)
    else:
        candidates = pick_balanced_word(languages)
        font_size = random.randint(12, 15)
        
    for word in candidates[:6]:
        w, h = get_text_size(word, font_size)
        if can_place_flower_word(x, y, w, h) and not check_overlap(x, y, w, h):
            placed_boxes.append((x, y, w, h))
            usage_count[word] += 1
            
            if is_center:
                # Beautiful, readable amber/copper/bronze tones
                if r < CENTER_RADIUS * 0.55:
                    color = random.choice(["#8B4513", "#A0522D", "#964B00", "#7A3803", "#6E3502"])
                else:
                    color = random.choice(["#CD853F", "#D2691E", "#B8860B", "#CC7722", "#E08934"])
            else:
                # Radiant sunflower yellow/gold tones
                color = random.choice(["#FFD700", "#FFC700", "#FFB700", "#FFA500", "#FFD020", "#FFE066"])
                
            left = 500 + x
            top = 350 + y
            html_parts.append(
                f'<div class="word" style="left:{left:.1f}px; top:{top:.1f}px; color:{color}; '
                f'font-size:{font_size}px; animation-delay:{delay:.2f}s;">{word}</div>'
            )
            delay += 0.012
            break

# ── 2. Place Plant Words ──
for x, y in points_plant:
    if abs(x) < 26:
        candidates = pick_balanced_word(short_languages)
        font_size = random.randint(11, 13)
    else:
        candidates = pick_balanced_word(languages)
        font_size = random.randint(11, 15)
        
    for word in candidates[:6]:
        w, h = get_text_size(word, font_size)
        if can_place_plant_word(x, y, w, h) and not check_overlap(x, y, w, h):
            placed_boxes.append((x, y, w, h))
            usage_count[word] += 1
            
            color = random.choice(["#2E7D32", "#388E3C", "#43A047", "#1B5E20", "#4CAF50", "#558B2F", "#66BB6A"])
            left = 500 + x
            top = 350 + y
            html_parts.append(
                f'<div class="word" style="left:{left:.1f}px; top:{top:.1f}px; color:{color}; '
                f'font-size:{font_size}px; animation-delay:{delay:.2f}s;">{word}</div>'
            )
            delay += 0.012
            break

# ── 3. Add "مومو" in the exact center ──
html_parts.append(
    '<div class="word mumu" style="left:500px; top:350px; color:#FFD700; '
    'font-size:44px; font-weight:bold; animation-delay:0s; '
    'text-shadow: 0 0 16px rgba(255, 215, 0, 0.9), 0 0 6px #000;">مومو</div>'
)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mumu's Sunflower</title>
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    background-color: #050505;
    margin: 0;
    overflow-x: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    color: white;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }}
  .container {{
    position: relative;
    width: 1000px;
    height: 1250px;
    transform: scale(0.68);
    transform-origin: center center;
  }}
  .word {{
    position: absolute;
    white-space: nowrap;
    opacity: 0;
    font-weight: 700;
    line-height: 1;
    animation: fadeIn 0.8s forwards;
    transform: translate(-50%, -50%);
    text-shadow: 0 0 3px rgba(0,0,0,0.9);
  }}
  .mumu {{
    z-index: 99;
  }}
  @keyframes fadeIn {{
    0% {{ opacity: 0; transform: translate(-50%, -50%) scale(0.6); }}
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
