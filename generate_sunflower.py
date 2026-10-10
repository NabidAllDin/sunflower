import math
import random

languages = [
    "I love you", "Te amo", "Je t'aime", "Ich liebe dich", "Ti amo", "Eu te amo",
    "Ik hou van jou", "Я люблю тебя", "愛してる", "사랑해", "我爱你",
    "Seni seviyorum", "Σ'αγαπώ", "Kocham cię", "Jag älskar dig",
    "Anh yêu em", "Aku cinta kamu", "Nakupenda", "Miluji tě",
    "Rakastan sinua", "Szeretlek", "Te iubesc", "Mahal kita", "Te dua",
    "Obicham te", "Milujem ťa", "S'ayapaw", "Hou van jou"
]

# ─── shape ───────────────────────────────────────────────────────────────────
CENTER_RADIUS  = 205   # big dark disc — like image 2
PETAL_LENGTH   = 125   # short petals ringing the disc
NUM_PETALS     = 18    # how many petals
PETAL_EXP      = 0.42  # low value = fat petals, nearly touching at edges

STEM_HALF  = 14        # half-width of stem
STEM_Y0    = 225       # stem starts here (y)
STEM_Y1    = 860       # stem ends here
LEAF_W     = 170       # max leaf half-width

def get_part(x, y):
    r     = math.sqrt(x * x + y * y)
    theta = math.atan2(y, x)

    # hollow centre for مومو
    if r < 46:
        return None

    # stem (narrow vertical bar)
    if -STEM_HALF < x < STEM_HALF and STEM_Y0 < y < STEM_Y1:
        return "stem"

    # right leaf (upper)
    if 310 < y < 480:
        lx = LEAF_W * math.sin((y - 310) / 170 * math.pi)
        if STEM_HALF < x < STEM_HALF + lx:
            return "leaf"

    # left leaf (lower)
    if 530 < y < 700:
        lx = LEAF_W * math.sin((y - 530) / 170 * math.pi)
        if -STEM_HALF - lx < x < -STEM_HALF:
            return "leaf"

    # petal shape via polar formula
    a_slice    = 2 * math.pi / NUM_PETALS
    theta_mod  = (theta % a_slice) / a_slice
    petal_frac = math.sin(theta_mod * math.pi) ** PETAL_EXP
    r_petal    = CENTER_RADIUS + PETAL_LENGTH * petal_frac

    if r < CENTER_RADIUS:
        return "center"
    if r < r_petal:
        return "petal"
    return None

# ─── accurate per-character width ────────────────────────────────────────────
def char_w(ch, fs):
    cp = ord(ch)
    if 0x4E00 <= cp <= 0x9FFF: return fs * 1.0   # CJK unified
    if 0xAC00 <= cp <= 0xD7A3: return fs * 1.0   # Korean hangul
    if 0x3040 <= cp <= 0x30FF: return fs * 1.0   # Hiragana / Katakana
    if 0x0600 <= cp <= 0x06FF: return fs * 0.62  # Arabic
    if 0x0400 <= cp <= 0x04FF: return fs * 0.60  # Cyrillic
    if 0x0370 <= cp <= 0x03FF: return fs * 0.60  # Greek
    return fs * 0.56                              # Latin

def word_w(word, fs):
    return sum(char_w(c, fs) for c in word)

# ─── span scanner ─────────────────────────────────────────────────────────────
def x_spans(yi, parts, lo, hi):
    spans, active, sx = [], False, 0
    for xi in range(lo, hi):
        hit = get_part(xi, yi) in parts
        if hit and not active:  sx = xi;  active = True
        elif not hit and active: spans.append((sx, xi - 1)); active = False
    if active: spans.append((sx, hi))
    return spans

# ─── place words ─────────────────────────────────────────────────────────────
html_parts = []
delay      = 0.0
WORD_GAP   = 10   # minimum gap in px between words

YELLOW = ["#FFD700", "#FFC107", "#FFCA28", "#FFB300", "#FFE082", "#FFD54F"]
GREEN  = ["#2E7D32", "#388E3C", "#43A047", "#1B5E20", "#33691E", "#558B2F"]
C_DARK = ["#1a0b00", "#2a1300", "#3E2723", "#4E342E"]
C_MID  = ["#5D4037", "#6D4C41", "#795548", "#4E342E"]

def emit(cx, cy, word, color, fs):
    """cx/cy = centre of the word in flower-space coords"""
    global delay
    left = 500 + cx
    top  = 350 + cy
    html_parts.append(
        f'<div class="word" style="left:{left}px;top:{top}px;'
        f'color:{color};font-size:{fs}px;'
        f'animation-delay:{delay:.2f}s;">{word}</div>'
    )
    delay += 0.022

# ── flower head ───────────────────────────────────────────────────────────────
FS_C  = 14;  LH_C = 18   # font-size & line-height for center zone
FS_P  = 17;  LH_P = 22   # font-size & line-height for petal zone

BOUND = CENTER_RADIUS + PETAL_LENGTH + 12

y = float(-(CENTER_RADIUS + PETAL_LENGTH + 8))
while y <= BOUND:
    in_center = abs(y) <= CENTER_RADIUS + 2
    fs = FS_C if in_center else FS_P
    lh = LH_C if in_center else LH_P

    for sx, ex in x_spans(int(y), {"center", "petal"}, -BOUND, BOUND):
        x = float(sx)
        while True:
            word = random.choice(languages)
            ww   = word_w(word, fs)
            # stop if word won't fit in remaining span
            if x + ww > ex:
                break
            mid = x + ww / 2
            pt  = get_part(int(mid), int(y))
            if pt not in {"center", "petal"}:
                x += 2; continue

            if pt == "center":
                rd    = math.sqrt(mid**2 + y**2)
                color = random.choice(C_DARK if rd < CENTER_RADIUS * 0.65 else C_MID)
            else:
                color = random.choice(YELLOW)

            emit(int(mid), int(y) - fs // 2, word, color, fs)
            x += ww + WORD_GAP

    y += lh

# ── stem + leaves ─────────────────────────────────────────────────────────────
FS_S = 15;  LH_S = 20

y = float(STEM_Y0)
while y <= STEM_Y1:
    for sx, ex in x_spans(int(y), {"stem", "leaf"}, -230, 230):
        x = float(sx)
        while True:
            word = random.choice(languages)
            ww   = word_w(word, FS_S)
            if x + ww > ex:
                break
            mid = x + ww / 2
            pt  = get_part(int(mid), int(y))
            if pt not in {"stem", "leaf"}:
                x += 2; continue

            color = random.choice(GREEN)
            emit(int(mid), int(y) - FS_S // 2, word, color, FS_S)
            x += ww + WORD_GAP

    y += LH_S

# ── مومو centrepiece ──────────────────────────────────────────────────────────
html_parts.append(
    '<div class="word mumu" style="left:500px;top:343px;color:#FFD700;'
    'font-size:42px;font-weight:bold;animation-delay:0s;'
    'text-shadow:0 0 22px rgba(255,215,0,0.8),0 0 6px #000;">مومو</div>'
)

# ─── HTML output ─────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Mumu's Sunflower</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{
  background:#050505;
  min-height:100vh;
  display:flex;
  justify-content:center;
  align-items:center;
  font-family:'Segoe UI',Arial,sans-serif;
  overflow:hidden;
}}
.container{{
  position:relative;
  width:1000px;
  height:1280px;
  transform:scale(0.68);
  transform-origin:center center;
}}
.word{{
  position:absolute;
  white-space:nowrap;
  opacity:0;
  font-weight:700;
  line-height:1;
  animation:pop 0.6s cubic-bezier(.34,1.4,.64,1) forwards;
  transform:translate(-50%,-50%);
}}
.mumu{{z-index:10}}
@keyframes pop{{
  from{{opacity:0;transform:translate(-50%,-50%) scale(0.3)}}
  to  {{opacity:1;transform:translate(-50%,-50%) scale(1)}}
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
print(f"Done — {len(html_parts)} words, no overlaps.")
