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

# Track language usage count to guarantee variety
usage_count = {lang: 0 for lang in languages}

def get_char_width(ch, font_size):
    cp = ord(ch)
    # CJK Unified, Hiragana, Katakana, Hangul (Korean)
    if (0x4E00 <= cp <= 0x9FFF or 
        0x3040 <= cp <= 0x30FF or 
        0xAC00 <= cp <= 0xD7AF or
        0xFF00 <= cp <= 0xFFEF):
        return font_size * 1.10
    # Bengali, Devanagari, Thai
    if (0x0980 <= cp <= 0x09FF or 0x0900 <= cp <= 0x097F or 0x0E00 <= cp <= 0x0E7F):
        return font_size * 0.85
    # Arabic, Hebrew, Greek, Cyrillic
    if (0x0600 <= cp <= 0x06FF or 0x0590 <= cp <= 0x05FF or 
        0x0370 <= cp <= 0x03FF or 0x0400 <= cp <= 0x04FF):
        return font_size * 0.70
    # Wide latin
    if ch in "WMmw":
        return font_size * 0.82
    # Narrow latin
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
PADDING_X = 3.5  # Clean gap horizontally
PADDING_Y = 2.5  # Clean gap vertically

def check_overlap(x, y, w, h):
    for (bx, by, bw, bh) in placed_boxes:
        if abs(x - bx) < (w + bw) / 2.0 + PADDING_X and abs(y - by) < (h + bh) / 2.0 + PADDING_Y:
            return True
    return False

# ── Sunflower Shape Geometry (The exact beloved shape) ──
CENTER_RADIUS = 190
PETAL_LENGTH = 155
NUM_PETALS = 18

def is_inside_flower(x, y):
    r = math.sqrt(x * x + y * y)
    if r < 40:  # Dead zone for "مومو"
        return False
    theta = math.atan2(y, x)
    angle_slice = 2 * math.pi / NUM_PETALS
    theta_mod = (theta % angle_slice) / angle_slice
    petal_shape = math.sin(theta_mod * math.pi) ** 0.5
    r_petal = CENTER_RADIUS + PETAL_LENGTH * petal_shape
    return r < r_petal

def is_inside_plant(x, y):
    # Stem: 64px wide (-32 to 32)
    if -32 <= x <= 32 and 150 <= y <= 850:
        return True
    # Upper right leaf: full and graceful
    if 270 <= y <= 470:
        leaf_progress = (y - 270) / 200
        leaf_x_max = 180 * (math.sin(leaf_progress * math.pi) ** 0.8)
        if 0 <= x <= 32 + leaf_x_max:
            return True
    # Lower left leaf: full and graceful
    if 490 <= y <= 690:
        leaf_progress = (y - 490) / 200
        leaf_x_max = 180 * (math.sin(leaf_progress * math.pi) ** 0.8)
        if -32 - leaf_x_max <= x <= 0:
            return True
    return False

def can_place_flower_word(x, y, w, h):
    for dx in [-w/2.0, w/2.0]:
        for dy in [-h/2.0, h/2.0]:
            if not is_inside_flower(x + dx, y + dy):
                return False
    return is_inside_flower(x, y)

def can_place_plant_word(x, y, w, h):
    for dx in [-w/2.0, w/2.0]:
        for dy in [-h/2.0, h/2.0]:
            if not is_inside_plant(x + dx, y + dy):
                return False
    return is_inside_plant(x, y)

# ── Generate candidate sample points ──
points_flower = []

# Fermat spiral for natural blooming
c = 2.3
for n in range(1, 42000):
    r = c * math.sqrt(n)
    if r > CENTER_RADIUS + PETAL_LENGTH + 5:
        break
    theta = n * 137.508 * math.pi / 180
    points_flower.append((r * math.cos(theta), r * math.sin(theta)))

# Targeted petal spines for all 18 petals
for p_idx in range(NUM_PETALS):
    base_angle = p_idx * 2 * math.pi / NUM_PETALS + (math.pi / NUM_PETALS)
    for r_step in range(int(CENTER_RADIUS * 0.75), int(CENTER_RADIUS + PETAL_LENGTH), 7):
        for ang_offset in [-0.09, -0.05, 0.0, 0.05, 0.09]:
            ang = base_angle + ang_offset
            points_flower.append((r_step * math.cos(ang), r_step * math.sin(ang)))

# Random jitter across flower
for _ in range(50000):
    r = random.uniform(35, CENTER_RADIUS + PETAL_LENGTH)
    theta = random.uniform(0, 2 * math.pi)
    points_flower.append((r * math.cos(theta), r * math.sin(theta)))

points_flower.sort(key=lambda p: math.sqrt(p[0]**2 + p[1]**2))

# Dense grid & jitter for plant
points_plant = []
for y_val in range(150, 855, 5):
    for x_val in range(-220, 220, 5):
        if is_inside_plant(x_val, y_val):
            points_plant.append((x_val + random.uniform(-2, 2), y_val + random.uniform(-2, 2)))

for _ in range(40000):
    x_val = random.uniform(-220, 220)
    y_val = random.uniform(150, 855)
    if is_inside_plant(x_val, y_val):
        points_plant.append((x_val, y_val))

points_plant.sort(key=lambda p: p[1])

html_parts = []
delay = 0.0

def pick_balanced_word(candidate_pool):
    # Sort candidates by least used to ensure rich language diversity
    sorted_candidates = sorted(candidate_pool, key=lambda w: (usage_count[w], random.random()))
    return sorted_candidates

# ── 1. Place Flower Words ──
for x, y in points_flower:
    r = math.sqrt(x * x + y * y)
    is_center = (r < CENTER_RADIUS)
    
    candidate_list = pick_balanced_word(languages)
    
    # Try top least-used candidates
    for word in candidate_list[:8]:
        font_size = random.randint(10, 13) if is_center else random.randint(12, 16)
        w, h = get_text_size(word, font_size)
        
        if can_place_flower_word(x, y, w, h) and not check_overlap(x, y, w, h):
            placed_boxes.append((x, y, w, h))
            usage_count[word] += 1
            
            if is_center:
                # Warm, readable amber / copper / bronze tones
                if r < CENTER_RADIUS * 0.55:
                    color = random.choice(["#8B4513", "#A0522D", "#964B00", "#7A3803", "#6E3502"])
                else:
                    color = random.choice(["#CD853F", "#D2691E", "#B8860B", "#CC7722", "#E08934"])
            else:
                # Brilliant, glowing sunflower yellow/gold tones
                color = random.choice(["#FFD700", "#FFC700", "#FFB700", "#FFA500", "#FFD020", "#FFE066"])
                
            left = 500 + x
            top = 350 + y
            html_parts.append(
                f'<div class="word" style="left:{left:.1f}px; top:{top:.1f}px; color:{color}; '
                f'font-size:{font_size}px; animation-delay:{delay:.2f}s;">{word}</div>'
            )
            delay += 0.012
            break

# ── 2. Place Plant (Stem & Leaves) Words ──
for x, y in points_plant:
    candidate_list = pick_balanced_word(languages)
    
    for word in candidate_list[:8]:
        font_size = random.randint(11, 14) if abs(x) < 32 else random.randint(11, 15)
        w, h = get_text_size(word, font_size)
        
        if can_place_plant_word(x, y, w, h) and not check_overlap(x, y, w, h):
            placed_boxes.append((x, y, w, h))
            usage_count[word] += 1
            
            # Rich, lush green tones
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
