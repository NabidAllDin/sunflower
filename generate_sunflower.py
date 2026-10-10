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

usage_count = {lang: 0 for lang in languages}

# ── 1. ACCURATE CHARACTER & TEXT SIZE FOR PERFECT SPACING ──
def get_char_width(ch, font_size):
    cp = ord(ch)
    # CJK (Chinese, Japanese Kanji, Korean Hangul, Katakana, Hiragana)
    if (0x4E00 <= cp <= 0x9FFF or 
        0x3040 <= cp <= 0x30FF or 
        0xAC00 <= cp <= 0xD7AF or
        0xFF00 <= cp <= 0xFFEF):
        return font_size * 1.15
    # Indic (Bengali, Hindi Devanagari) & Thai
    if (0x0980 <= cp <= 0x09FF or 0x0900 <= cp <= 0x097F or 0x0E00 <= cp <= 0x0E7F):
        return font_size * 0.90
    # Arabic, Hebrew, Greek, Cyrillic
    if (0x0600 <= cp <= 0x06FF or 0x0590 <= cp <= 0x05FF or 
        0x0370 <= cp <= 0x03FF or 0x0400 <= cp <= 0x04FF):
        return font_size * 0.75
    # Wide Latin
    if ch in "WMmw":
        return font_size * 0.88
    # Narrow Latin & punctuation
    if ch in "ijlIt f'":
        return font_size * 0.38
    if ch == ' ':
        return font_size * 0.35
    # Standard Latin (bold)
    return font_size * 0.65

def get_text_size(text, font_size):
    w = sum(get_char_width(c, font_size) for c in text)
    h = font_size * 1.25  # realistic line height with breathing room
    return w, h

placed_boxes = []

# ── 2. ZERO OVERLAP SPACING GUARANTEE ──
# Guaranteed minimum spacing between any two words so every word is 100% readable
PADDING_X = 4.5  # 4.5px guaranteed horizontal gap
PADDING_Y = 3.5  # 3.5px guaranteed vertical gap

def check_overlap(x, y, w, h):
    for (bx, by, bw, bh) in placed_boxes:
        if abs(x - bx) < (w + bw) / 2.0 + PADDING_X and abs(y - by) < (h + bh) / 2.0 + PADDING_Y:
            return True
    return False

# ── 3. SUNFLOWER GEOMETRY ──
CENTER_RADIUS = 180
PETAL_LENGTH = 145
NUM_PETALS = 18

def is_inside_flower(x, y):
    r = math.sqrt(x * x + y * y)
    if r < 44:  # Clean dead zone for "مومو"
        return False
    theta = math.atan2(y, x)
    angle_slice = 2 * math.pi / NUM_PETALS
    theta_offset = (theta + angle_slice / 2) % (2 * math.pi)
    theta_mod = (theta_offset % angle_slice) / angle_slice
    petal_curve = math.sin(theta_mod * math.pi) ** 0.85
    r_petal = CENTER_RADIUS + PETAL_LENGTH * petal_curve
    return r < r_petal

def is_inside_plant(x, y):
    # Stem: 60px wide (-30 to 30) from flower base down to 840
    if -30 <= x <= 30 and 150 <= y <= 840:
        return True
    # Upper right leaf: broad sunflower leaf
    if 260 <= y <= 470:
        prog = (y - 260) / 210
        lx = 180 * (math.sin(prog * math.pi) ** 0.85)
        if 0 <= x <= 30 + lx:
            return True
    # Lower left leaf: broad sunflower leaf
    if 480 <= y <= 690:
        prog = (y - 480) / 210
        lx = 180 * (math.sin(prog * math.pi) ** 0.85)
        if -30 - lx <= x <= 0:
            return True
    return False

def can_place_flower_word(x, y, w, h):
    if not is_inside_flower(x, y):
        return False
    for dx in [-w * 0.45, w * 0.45]:
        for dy in [-h * 0.45, h * 0.45]:
            if not is_inside_flower(x + dx, y + dy):
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

# ── 4. CANDIDATE SAMPLING ──
points_flower = []

# Fermat spiral for natural organic blooming
c = 2.2
for n in range(1, 45000):
    r = c * math.sqrt(n)
    if r > CENTER_RADIUS + PETAL_LENGTH + 5:
        break
    theta = n * 137.508 * math.pi / 180
    points_flower.append((r * math.cos(theta), r * math.sin(theta)))

# Targeted petal spines for all 18 petals
for p_idx in range(NUM_PETALS):
    base_ang = p_idx * (2 * math.pi / NUM_PETALS)
    for r_step in range(int(CENTER_RADIUS + PETAL_LENGTH - 6), int(CENTER_RADIUS * 0.75), -6):
        for ang_offset in [-0.07, -0.035, 0.0, 0.035, 0.07]:
            ang = base_ang + ang_offset
            points_flower.append((r_step * math.cos(ang), r_step * math.sin(ang)))

# Random filling points
for _ in range(60000):
    r = random.uniform(40, CENTER_RADIUS + PETAL_LENGTH)
    theta = random.uniform(0, 2 * math.pi)
    points_flower.append((r * math.cos(theta), r * math.sin(theta)))

# Sort from center outward so flower blooms organically
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

# ── 5. PLACE FLOWER WORDS (READABLE SIZES & HIGH-CONTRAST COLORS) ──
for x, y in points_flower:
    r = math.sqrt(x * x + y * y)
    is_center = (r < CENTER_RADIUS)
    
    # Readability: font size 12-14px for center, 13-16px for petals
    if is_center:
        font_size = random.randint(12, 14)
    else:
        font_size = random.randint(13, 16)
        
    candidates = pick_balanced_word(languages)
    
    for word in candidates[:6]:
        w, h = get_text_size(word, font_size)
        if can_place_flower_word(x, y, w, h) and not check_overlap(x, y, w, h):
            placed_boxes.append((x, y, w, h))
            usage_count[word] += 1
            
            if is_center:
                # Highly readable amber, bronze, copper seed colors
                if r < CENTER_RADIUS * 0.55:
                    color = random.choice(["#E08934", "#D2691E", "#CD853F", "#C68642", "#B8860B"])
                else:
                    color = random.choice(["#E5A04A", "#DE8C38", "#DAA520", "#D2691E", "#CD853F"])
            else:
                # Bright, vivid sunflower gold/yellow
                color = random.choice(["#FFD700", "#FFCC00", "#FFC000", "#FFAA00", "#FFD020", "#FFE066"])
                
            left = 500 + x
            top = 350 + y
            html_parts.append(
                f'<div class="word" style="left:{left:.1f}px; top:{top:.1f}px; color:{color}; '
                f'font-size:{font_size}px; animation-delay:{delay:.2f}s;">{word}</div>'
            )
            delay += 0.015
            break

# ── 6. PLACE PLANT WORDS (READABLE SIZES & CLEAN GREENS) ──
for x, y in points_plant:
    font_size = random.randint(12, 15)
    candidates = pick_balanced_word(languages)
    
    for word in candidates[:6]:
        w, h = get_text_size(word, font_size)
        if can_place_plant_word(x, y, w, h) and not check_overlap(x, y, w, h):
            placed_boxes.append((x, y, w, h))
            usage_count[word] += 1
            
            # Vibrant, readable foliage greens
            color = random.choice(["#4CAF50", "#66BB6A", "#43A047", "#388E3C", "#2E7D32", "#81C784"])
            
            left = 500 + x
            top = 350 + y
            html_parts.append(
                f'<div class="word" style="left:{left:.1f}px; top:{top:.1f}px; color:{color}; '
                f'font-size:{font_size}px; animation-delay:{delay:.2f}s;">{word}</div>'
            )
            delay += 0.015
            break

# ── 7. ADD "مومو" CENTERPIECE ──
html_parts.append(
    '<div class="word mumu" style="left:500px; top:350px; color:#FFD700; '
    'font-size:42px; font-weight:bold; animation-delay:0s; '
    'text-shadow: 0 0 16px rgba(255, 215, 0, 0.9), 0 0 6px #000;">مومو</div>'
)

# ── 8. HTML & CSS OUTPUT ──
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
    line-height: 1.1;
    letter-spacing: 0.4px;
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
print(f"Generated index.html with {len(html_parts)} perfectly spaced, readable words!")
