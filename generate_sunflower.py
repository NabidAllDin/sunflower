import math
import random

languages = [
    "I love you", "Te amo", "Je t'aime", "Ich liebe dich", "Ti amo", "Eu te amo",
    "Ik hou van jou", "Я люблю тебя", "愛してる", "사랑해", "我爱你",
    "Seni seviyorum", "Σ'αγαπώ", "Kocham cię", "Jag älskar dig",
    "Anh yêu em", "Aku cinta kamu", "Nakupenda", "Miluji tě",
    "Rakastan sinua", "Szeretlek", "Te iubesc", "Mahal kita", "Te dua",
    "Obicham te", "Milujem ťa", "Hou van jou", "S'ayapaw"
]

# ─── shape parameters ─────────────────────────────────────────────────────────
NUM_PETALS    = 16
CENTER_RADIUS = 155   # radius of the dark seed disc
PETAL_LENGTH  = 200   # tip-to-centre-edge length of each petal
PETAL_WIDTH   = 78    # widest point of each petal
PETAL_OVERLAP = 25    # how much petal root dips into the center disc

STEM_X_HALF   = 14    # half-width of stem
STEM_Y_START  = CENTER_RADIUS + 10
STEM_Y_END    = 840
LEAF_W        = 170   # max leaf width

# ─── shape classifier ─────────────────────────────────────────────────────────
def is_in_petal(x, y):
    """True if (x,y) falls inside any of the NUM_PETALS ellipses."""
    for i in range(NUM_PETALS):
        angle = i * 2 * math.pi / NUM_PETALS
        # ellipse centre in world space
        ec_r = CENTER_RADIUS + PETAL_LENGTH / 2 - PETAL_OVERLAP
        ec_x = ec_r * math.cos(angle)
        ec_y = ec_r * math.sin(angle)

        dx = x - ec_x
        dy = y - ec_y

        # rotate into petal-local axes
        local_rad  =  dx * math.cos(angle) + dy * math.sin(angle)
        local_tang = -dx * math.sin(angle) + dy * math.cos(angle)

        a = PETAL_LENGTH / 2 + PETAL_OVERLAP   # semi-major
        b = PETAL_WIDTH  / 2                   # semi-minor

        if (local_rad / a) ** 2 + (local_tang / b) ** 2 <= 1.0:
            return True
    return False

def get_part(x, y):
    r = math.sqrt(x * x + y * y)

    # Mumu dead zone
    if r < 42:
        return None

    # stem
    if -STEM_X_HALF < x < STEM_X_HALF and STEM_Y_START < y < STEM_Y_END:
        return "stem"

    # right leaf (upper)
    if 290 < y < 460:
        lx = LEAF_W * math.sin((y - 290) / 170 * math.pi)
        if STEM_X_HALF < x < STEM_X_HALF + lx:
            return "leaf"

    # left leaf (lower)
    if 510 < y < 680:
        lx = LEAF_W * math.sin((y - 510) / 170 * math.pi)
        if -STEM_X_HALF - lx < x < -STEM_X_HALF:
            return "leaf"

    # center disc
    if r < CENTER_RADIUS:
        return "center"

    # petal ellipses
    if is_in_petal(x, y):
        return "petal"

    return None

# ─── row scanner ─────────────────────────────────────────────────────────────
def x_spans(y_val, parts_wanted, x_lo, x_hi, step=1):
    """Returns list of (x_start, x_end) spans where get_part == parts_wanted."""
    spans, in_span, sx = [], False, None
    for xi in range(x_lo, x_hi, step):
        hit = get_part(xi, y_val) in parts_wanted
        if hit and not in_span:
            sx = xi;  in_span = True
        elif not hit and in_span:
            spans.append((sx, xi - step));  in_span = False
    if in_span:
        spans.append((sx, x_hi))
    return spans

# ─── place words ─────────────────────────────────────────────────────────────
html_parts = []
delay      = 0.0
WORD_GAP   = 5   # px gap between words in a row

YELLOW_PALETTE = ["#FFD700","#FFC107","#FFCA28","#FFB300","#FFE082","#FFD54F"]
GREEN_PALETTE  = ["#2E7D32","#388E3C","#43A047","#1B5E20","#33691E"]
CENTER_DARK    = ["#1a0b00","#2a1300","#3E2723","#4E342E","#5D4037"]
CENTER_MID     = ["#4E342E","#5D4037","#6D4C41","#795548"]

def add_word(x, y, word, color, fs, delay_v):
    left   = 500 + x
    top_px = 350 + y
    html_parts.append(
        f'<div class="word" style="left:{left}px;top:{top_px}px;'
        f'color:{color};font-size:{fs}px;'
        f'animation-delay:{delay_v:.2f}s;">{word}</div>'
    )

# ── flower head ───────────────────────────────────────────────────────────────
Y_FLOWER_MIN = -(CENTER_RADIUS + PETAL_LENGTH + 8)
Y_FLOWER_MAX =  (CENTER_RADIUS + PETAL_LENGTH + 8)

FS_CENTER = 13;  LH_CENTER = 17;  CW_CENTER = FS_CENTER * 0.56
FS_PETAL  = 16;  LH_PETAL  = 21;  CW_PETAL  = FS_PETAL  * 0.56

y = float(Y_FLOWER_MIN)
while y <= Y_FLOWER_MAX:
    in_center_band = abs(y) <= CENTER_RADIUS + 4
    fs  = FS_CENTER if in_center_band else FS_PETAL
    cw  = CW_CENTER if in_center_band else CW_PETAL
    lh  = LH_CENTER if in_center_band else LH_PETAL
    parts = {"center", "petal"}
    bounds = int(CENTER_RADIUS + PETAL_LENGTH + 20)

    for (sx, ex) in x_spans(int(y), parts, -bounds, bounds):
        x = float(sx)
        while True:
            word   = random.choice(languages)
            word_w = len(word) * cw
            if x + word_w > ex:
                break
            mid_x = x + word_w / 2
            pt    = get_part(int(mid_x), int(y))
            if pt not in parts:
                x += 3; continue

            if pt == "center":
                rd    = math.sqrt(mid_x**2 + y**2)
                color = random.choice(CENTER_DARK if rd < CENTER_RADIUS * 0.65 else CENTER_MID)
            else:
                color = random.choice(YELLOW_PALETTE)

            add_word(int(x + word_w/2), int(y) - fs//2, word, color, fs, delay)
            delay += 0.025
            x     += word_w + WORD_GAP

    y += lh

# ── stem + leaves ─────────────────────────────────────────────────────────────
FS_STEM = 14;  LH_STEM = 19;  CW_STEM = FS_STEM * 0.56

y = float(STEM_Y_START)
while y <= STEM_Y_END:
    for (sx, ex) in x_spans(int(y), {"stem","leaf"}, -220, 220):
        x = float(sx)
        while True:
            word   = random.choice(languages)
            word_w = len(word) * CW_STEM
            if x + word_w > ex:
                break
            mid_x = x + word_w / 2
            pt    = get_part(int(mid_x), int(y))
            if pt not in {"stem","leaf"}:
                x += 3; continue

            color = random.choice(GREEN_PALETTE)
            add_word(int(x + word_w/2), int(y) - FS_STEM//2, word, color, FS_STEM, delay)
            delay += 0.025
            x     += word_w + WORD_GAP

    y += LH_STEM

# ── مومو in the centre ─────────────────────────────────────────────────────────
html_parts.append(
    '<div class="word" style="left:500px;top:343px;color:#FFD700;'
    'font-size:42px;font-weight:bold;animation-delay:0s;'
    'text-shadow:0 0 18px rgba(255,215,0,0.7);">مومو</div>'
)

# ─── HTML ─────────────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Mumu's Sunflower</title>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{
  background:#050505;
  min-height:100vh;
  display:flex;
  justify-content:center;
  align-items:center;
  font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;
  overflow:hidden;
}}
.container {{
  position:relative;
  width:1000px;
  height:1250px;
  transform:scale(0.68);
  transform-origin:center center;
}}
.word {{
  position:absolute;
  white-space:nowrap;
  opacity:0;
  font-weight:600;
  line-height:1;
  animation:fadeIn 0.7s forwards;
  transform:translate(-50%,-50%);
}}
@keyframes fadeIn {{
  from {{ opacity:0; transform:translate(-50%,-50%) scale(0.5); }}
  to   {{ opacity:1; transform:translate(-50%,-50%) scale(1); }}
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
