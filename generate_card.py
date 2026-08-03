"""
generate_card.py
Generates system-infocard-combined.gif by:
  - Left panel: frames from system-infocard.gif
  - Right panel: drawn frame-by-frame with scan reveal animation
  - Title bar: drawn on top of both panels
"""

from PIL import Image, ImageDraw, ImageFont
import os, sys

# ── CONFIG ──────────────────────────────────────────────
REPO   = os.path.dirname(os.path.abspath(__file__))
GIF_IN = os.path.join(REPO, "system-infocard.gif")
OUT    = os.path.join(REPO, "system-infocard-combined.gif")

# Canvas
TOTAL_W  = 900
TOTAL_H  = 500
TITLEBAR = 38
LEFT_W   = 350
RIGHT_X  = LEFT_W
RIGHT_W  = TOTAL_W - LEFT_W
CONTENT_H = TOTAL_H - TITLEBAR   # 462

# Colors
C_BG        = (13,  27,  42)
C_BG2       = (10,  22,  40)
C_TITLEBAR  = (11,  24,  38)
C_BORDER    = (0,   70,  90)
C_CYAN      = (34,  211, 238)
C_PURPLE    = (91,  45,  142)
C_WHITE     = (226, 232, 240)
C_DIM       = (74,  127, 165)
C_DOTS      = (30,  58,  82)
C_RED       = (255, 59,  59)
C_GREEN     = (40,  200, 64)
C_YELLOW    = (254, 188, 46)
C_LIVE      = (255, 59,  59)

# Font — try Fira Code / Consolas / fallback
def load_font(size):
    candidates = [
        "FiraCode-Regular.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "C:/Windows/Fonts/lucon.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try: return ImageFont.truetype(path, size)
            except: pass
    return ImageFont.load_default()

F11  = load_font(13)
F12  = load_font(14)
F10  = load_font(12)

# ── DATA ROWS ────────────────────────────────────────────
ROWS = [
    # (label, value, value_color)
    ("Subject",          "Frank Emmanuel Wuaten",                          C_WHITE),
    ("Role",             "Web. Developer & Creative UI Designer",          C_WHITE),
    ("Origin",           "Batam, Indonesia",                               C_WHITE),
    ("Education",        "Computer Science, Sam Ratulangi University",     C_WHITE),
    ("Status",           "Building & Learning",                            C_WHITE),
    ("Toolchain",        "VSCode, Git, Figma, AI IDE (Antigravity & Kiro)",C_WHITE),
    None,  # divider
    ("Core. Lang",       "JavaScript, HTML, CSS",                          C_WHITE),
    ("Core. Frontend",   "React, Vite, Tailwind CSS",                      C_WHITE),
    ("Core. Backend",    "Node.js",                                        C_WHITE),
    ("Core Database",    "Supabase",                                       C_WHITE),
    ("Core. Infra",      "Vercel & Git",                                   C_WHITE),
    None,  # divider
    ("- Contact",        None,                                             C_DIM),
    ("Grid. Mail",       "frankwuaten2572@gmail.com",                      C_WHITE),
    ("Grid. Portofolio", "https://portofolio-project-indol.vercel.app/",  C_WHITE),
    ("Grid Linkedin",    "Coming Soon",                                    C_DIM),
    ("Grid. Github",     "Frankwtn",                                       C_WHITE),
    ("Grid. Facebook",   "Coming soon",                                    C_DIM),
]

# ── HELPERS ──────────────────────────────────────────────
def text_w(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font)
    return bb[2] - bb[0]

def draw_titlebar(draw):
    draw.rectangle([0, 0, TOTAL_W, TITLEBAR], fill=C_TITLEBAR)
    # Traffic lights
    draw.ellipse([20,12,36,28], fill=(255,95,87))
    draw.ellipse([44,12,60,28], fill=(254,188,46))
    draw.ellipse([68,12,84,28], fill=(40,200,64))
    # Title text
    title = "frankwuaten2572@gmail.com  \u2014  % ./profile.sh --live"
    tw = text_w(draw, title, F12)
    draw.text(((TOTAL_W-tw)//2, 13), title, font=F12, fill=C_DIM)
    # Bottom border
    draw.line([0, TITLEBAR-1, TOTAL_W, TITLEBAR-1], fill=C_BORDER, width=1)

def draw_right_panel(draw, reveal_y, live_on, cursor_on):
    """Draw right info panel. reveal_y = how far down content is revealed (px from top of content area)."""
    rx = RIGHT_X
    ry = TITLEBAR  # top of content
    rw = RIGHT_W

    # Background
    draw.rectangle([rx, ry, TOTAL_W, TOTAL_H], fill=C_BG2)
    # Left border line
    draw.line([rx, ry, rx, TOTAL_H], fill=C_BORDER, width=1)

    # SYSTEM.INFO
    draw.text((rx+14, ry+12), "SYSTEM.INFO", font=F11, fill=C_DIM)

    # LIVE indicator
    if live_on:
        draw.ellipse([TOTAL_W-62, ry+12, TOTAL_W-52, ry+22], fill=C_RED)
    draw.text((TOTAL_W-48, ry+10), "LIVE", font=F11, fill=C_RED)

    # Email badge
    badge_text = "frankwuaten2572@gmail.com"
    bw = text_w(draw, badge_text, F10) + 16
    draw.rounded_rectangle([rx+14, ry+30, rx+14+bw, ry+50], radius=4, fill=C_PURPLE)
    draw.text((rx+22, ry+33), badge_text, font=F10, fill=C_WHITE)

    # Top divider
    draw.line([rx+14, ry+58, TOTAL_W-14, ry+58], fill=C_BORDER, width=1)

    # ── ROWS ──
    row_y = ry + 74
    row_h = 22

    for row in ROWS:
        content_top = row_y - ry  # relative to content area top

        if content_top > reveal_y:
            row_y += row_h
            continue

        if row is None:
            # Divider
            draw.line([rx+14, row_y-4, TOTAL_W-14, row_y-4], fill=C_BORDER, width=1)
            row_y += 6
            continue

        label, value, vcol = row

        # Label
        label_color = C_DIM if label.startswith("-") else C_CYAN
        draw.text((rx+14, row_y), label, font=F11, fill=label_color)
        lw = text_w(draw, label, F11)

        if value:
            # Value (right-aligned)
            vw = text_w(draw, value, F11)
            vx = TOTAL_W - 14 - vw
            draw.text((vx, row_y), value, font=F11, fill=vcol)

            # Dots between label end and value start
            dot_x1 = rx + 14 + lw + 6
            dot_x2 = vx - 6
            if dot_x2 > dot_x1 + 10:
                # Draw dashed line
                x = dot_x1
                dot_y = row_y + 8
                while x < dot_x2:
                    draw.line([x, dot_y, min(x+2, dot_x2), dot_y], fill=C_DOTS, width=1)
                    x += 5

        row_y += row_h

    # ── BOTTOM BAR ──
    bar_y = TOTAL_H - 40
    draw.line([rx, bar_y, TOTAL_W, bar_y], fill=C_BORDER, width=1)
    bottom_text = "\u2022 More about me & projects below in README"
    btw = text_w(draw, bottom_text, F10)
    bx = rx + (rw - btw) // 2
    draw.text((bx, bar_y+8), bottom_text, font=F10, fill=C_DIM)
    # Cursor block
    if cursor_on:
        cx = bx + btw + 4
        draw.rectangle([cx, bar_y+8, cx+8, bar_y+22], fill=C_CYAN)

def draw_scan_line(draw, scan_y):
    """Draw glowing horizontal scan line at scan_y (absolute)."""
    if scan_y < TITLEBAR or scan_y > TOTAL_H - 40:
        return
    for i, alpha in [(3,20),(2,40),(1,70),(0,120)]:
        y = scan_y - i
        if y >= TITLEBAR:
            r,g,b = C_CYAN
            a = alpha
            # Pillow RGBA blend manually
            draw.line([RIGHT_X, y, TOTAL_W, y],
                fill=(r, g, b, a if a < 255 else 255), width=1)
    draw.line([RIGHT_X, scan_y, TOTAL_W, scan_y], fill=(*C_CYAN, 180), width=2)

def draw_left_panel_bg(img):
    """Draw dark background for left panel (GIF will be pasted over)."""
    d = ImageDraw.Draw(img)
    d.rectangle([0, TITLEBAR, LEFT_W, TOTAL_H], fill=C_BG)

# ── LOAD SOURCE GIF ──────────────────────────────────────
print("Loading source GIF...")
try:
    src_gif = Image.open(GIF_IN)
except FileNotFoundError:
    print(f"ERROR: {GIF_IN} not found. Place system-infocard.gif in repo root.")
    sys.exit(1)

# Extract all frames
src_frames = []
src_durations = []
try:
    while True:
        frame = src_gif.copy().convert("RGBA")
        src_frames.append(frame)
        src_durations.append(src_gif.info.get("duration", 80))
        src_gif.seek(src_gif.tell() + 1)
except EOFError:
    pass

print(f"  {len(src_frames)} frames loaded from source GIF")

# ── ANIMATION PLAN ───────────────────────────────────────
# Total animation: scan reveal over ~120 frames (~4s at 33ms)
# Then hold with blinking cursor/live for ~60 frames
# Then loop

REVEAL_FRAMES = 60    # frames to complete scan reveal
HOLD_FRAMES   = 40    # frames to hold after reveal
BLINK_PERIOD  = 20    # frames per blink cycle

content_height = TOTAL_H - TITLEBAR - 40   # scannable area

frames_out = []
durations_out = []

total_frames = REVEAL_FRAMES + HOLD_FRAMES

for f in range(total_frames):
    # Create canvas
    img = Image.new("RGBA", (TOTAL_W, TOTAL_H), C_BG)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Left panel: paste source GIF frame ──
    gif_idx = f % len(src_frames)
    left_frame = src_frames[gif_idx].copy()
    # Resize to fit left panel
    lf_resized = left_frame.resize((LEFT_W, CONTENT_H), Image.LANCZOS)
    img.paste(lf_resized, (0, TITLEBAR), lf_resized)

    # ── Right panel ──
    if f < REVEAL_FRAMES:
        progress = f / REVEAL_FRAMES  # 0.0 → 1.0
        reveal_y = int(progress * content_height)
        scan_y = TITLEBAR + reveal_y
        live_on = (f % BLINK_PERIOD) < (BLINK_PERIOD // 2)
        cursor_on = False
    else:
        reveal_y = content_height  # fully revealed
        scan_y = -1  # no scan line
        live_on = (f % BLINK_PERIOD) < (BLINK_PERIOD // 2)
        cursor_on = (f % BLINK_PERIOD) < (BLINK_PERIOD // 2)

    draw_right_panel(draw, reveal_y, live_on, cursor_on)

    if f < REVEAL_FRAMES and scan_y >= TITLEBAR:
        draw_scan_line(draw, scan_y)

    # ── Title bar (on top of everything) ──
    draw_titlebar(draw)

    # Outer border glow
    draw.rectangle([0, 0, TOTAL_W-1, TOTAL_H-1], outline=(*C_BORDER, 180), width=2)

    # Convert to RGB palette for GIF
    img_rgb = img.convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT)

    frames_out.append(img_rgb)
    # 60ms per frame for smooth enough animation, saves file size
    durations_out.append(60)

    if f % 20 == 0:
        print(f"  Frame {f+1}/{total_frames}...")

# ── SAVE ─────────────────────────────────────────────────
print(f"Saving {OUT}...")
frames_out[0].save(
    OUT,
    save_all=True,
    append_images=frames_out[1:],
    loop=0,
    duration=durations_out,
    optimize=False,
)
print(f"Done! Saved to {OUT}")
print(f"File size: {os.path.getsize(OUT) / 1024:.1f} KB")
