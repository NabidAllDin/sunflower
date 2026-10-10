import math
import random

languages = [
    "I love you", "Te amo", "Je t'aime", "Ich liebe dich", "Ti amo", "Eu te amo",
    "Ik hou van jou", "Я тебя люблю", "愛してる", "사랑해", "我爱你",
    "Seni seviyorum", "Σ' αγαπώ", "Kocham cię", "Jag älskar dig",
    "Anh yêu em", "Aku cinta kamu", "Nakupenda", "Miluji tě",
    "Rakastan sinua", "Szeretlek", "Te iubesc", "Mahal kita", "Te dua",
    "Obicham te", "Milujem ťa", "Hou van jou", "S'ayapaw"
]

CENTER_RADIUS = 190
PETAL_LENGTH  = 155
NUM_PETALS    = 18

def get_part(x, y):
    r     = math.sqrt(x * x + y * y)
    theta = math.atan2(y, x)

    # dead-zone for "مومو"
    if r < 42:
        return None

    # stem
    if -13 < x < 13 and 220 < y < 820:
        return "stem"

    # right leaf
    if 300 < y < 460:
        lx = 165 * math.sin((y - 300) / 160 * math.pi)
        if 13 < x < 13 + lx:
            return "leaf"

    # left leaf
    if 510 < y < 670:
        lx = 165 * math.sin((y - 510) / 160 * math.pi)
        if -13 - lx < x < -13:
            return "leaf"

    # petals
    angle_slice = 2 * math.pi / NUM_PETALS
    theta_mod   = (theta % angle_slice) / angle_slice
    petal_shape = math.sin(theta_mod * math.pi) ** 0.5
    r_petal     = CENTER_RADIUS + PETAL_LENGTH * petal_shape

    if r < CENTER_RADIUS:
        return "center"
    elif r < r_petal:
        return "petal"

    return None

# ── row-scan helpers ──────────────────────────────────────────────────────────
def x_spans(y_val, parts_wanted, x_lo=-500, x_hi=500, step=1):
    """Return list of (x_start, x_end) continuous spans inside parts_wanted."""
    spans = []
    in_span = False
    sx = None
    for xi in range(x_lo, x_hi, step):
        hit = get_part(xi, y_val) in parts_wanted
        if hit and not in_span:
            sx = xi
            in_span = True
        elif not hit and in_span:
            spans.append((sx, xi - step))
            in_span = False
    if in_span:
        spans.append((sx, x_hi))
    return spans

# ── placement ─────────────────────────────────────────────────────────────────
html_parts = []
delay      = 0.0
WORD_GAP   = 7   # px gap between words

# ── Flower head (center + petals) ────────────────────────────────────────────
Y_STEP_CENTER = 16   # line height for center
Y_STEP_PETAL  = 19   # line height for petals
FS_CENTER     = 12
FS_PETAL      = 15
# avg char width ≈ font_size * 0.55
CW_CENTER = FS_CENTER * 0.55
CW_PETAL  = FS_PETAL  * 0.55

Y_MIN = -(CENTER_RADIUS + PETAL_LENGTH + 5)
Y_MAX =  (CENTER_RADIUS + PETAL_LENGTH + 5)

y = Y_MIN
while y <= Y_MAX:
    # pick font / step by region
    in_center_band = abs(y) < CENTER_RADIUS
    fs   = FS_CENTER if in_center_band else FS_PETAL
    cw   = CW_CENTER if in_center_band else CW_PETAL
    step = Y_STEP_CENTER if in_center_band else Y_STEP_PETAL

    for (sx, ex) in x_spans(y, {"center", "petal"}):
        x = sx
        while True:
            word   = random.choice(languages)
            word_w = int(len(word) * cw)
            if x + word_w > ex:
                break
            # check mid-point still in shape
            mid_x = x + word_w // 2
            pt    = get_part(mid_x, y)
            if pt not in ("center", "petal"):
                x += 4
                continue

            if pt == "center":
                rd = math.sqrt(mid_x * mid_x + y * y)
                color = random.choice(["#1a0b00","#2a1300","#3E2723","#4E342E"]) \
                        if rd < CENTER_RADIUS * 0.6 else \
                        random.choice(["#4E342E","#5D4037","#6D4C41"])
            else:
                color = random.choice(["#FFD700","#FFC107","#FFCA28","#FFB300","#FFE082"])

            left   = 500 + x
            top_px = 350 + int(y) - fs // 2
            html_parts.append(
                f'<div class="word" style="left:{left}px;top:{top_px}px;'
                f'color:{color};font-size:{fs}px;'
                f'animation-delay:{delay:.2f}s;">{word}</div>'
            )
            delay += 0.025
            x     += word_w + WORD_GAP

    y += step

# ── Stem + leaves ────────────────────────────────────────────────────────────
Y_STEP_STEM = 19
FS_STEM     = 14
CW_STEM     = FS_STEM * 0.55

y = CENTER_RADIUS + 15.0
while y <= 820:
    for (sx, ex) in x_spans(int(y), {"stem", "leaf"}, x_lo=-200, x_hi=200):
        x = sx
        while True:
            word   = random.choice(languages)
            word_w = int(len(word) * CW_STEM)
            if x + word_w > ex:
                break
            mid_x = x + word_w // 2
            pt    = get_part(mid_x, int(y))
            if pt not in ("stem", "leaf"):
                x += 4
                continue

            color = random.choice(["#2E7D32","#388E3C","#43A047","#1B5E20"])
            left   = 500 + x
            top_px = 350 + int(y) - FS_STEM // 2
            html_parts.append(
                f'<div class="word" style="left:{left}px;top:{top_px}px;'
                f'color:{color};font-size:{FS_STEM}px;'
                f'animation-delay:{delay:.2f}s;">{word}</div>'
            )
            delay += 0.025
            x     += word_w + WORD_GAP

    y += Y_STEP_STEM

# ── "مومو" in the very centre ─────────────────────────────────────────────────
html_parts.append(
    '<div class="word" style="left:500px;top:350px;color:#FFD700;'
    'font-size:44px;font-weight:bold;animation-delay:0s;'
    'text-shadow:0 0 20px rgba(255,215,0,0.6);">مومو</div>'
)

# ── HTML output ───────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mumu's Sunflower</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #050505;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    overflow: hidden;
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
    font-weight: 600;
    line-height: 1;
    animation: fadeIn 0.8s forwards;
    transform: translate(-50%, -50%);
  }}
  @keyframes fadeIn {{
    from {{ opacity: 0; transform: translate(-50%,-50%) scale(0.6); }}
    to   {{ opacity: 1; transform: translate(-50%,-50%) scale(1); }}
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
