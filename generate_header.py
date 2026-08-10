"""
generate_header.py
Generates dark.svg and light.svg for GitHub Profile README.
Edit CONFIG below to update content, then run: python generate_header.py
"""

# ── CONFIG ───────────────────────────────────────────────────────────────────
NAME        = "Frank Emmanuel Wuaten"
ROLE        = "Web Developer & Creative UI Designer"
LOCATION    = "Batam, Indonesia"
EMAIL       = "frankwuaten2572@gmail.com"
GITHUB      = "Frankwtn"
PORTFOLIO   = "portofolio-project-indol.vercel.app"

TAGLINES = [
    "Building for the web.",
    "React · Supabase · Tailwind",
    "UI/UX + Code.",
]

# ── THEME DEFINITIONS ────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "bg"          : "#0d1117",
        "bg2"         : "#161b22",
        "border"      : "#21262d",
        "accent"      : "#22d3ee",
        "accent2"     : "#a78bfa",
        "text"        : "#e6edf3",
        "text_dim"    : "#7d8590",
        "text_muted"  : "#484f58",
        "badge_bg"    : "#1f2937",
        "name_color"  : "#ffffff",
    },
    "light": {
        "bg"          : "#ffffff",
        "bg2"         : "#f6f8fa",
        "border"      : "#d0d7de",
        "accent"      : "#0891b2",
        "accent2"     : "#7c3aed",
        "text"        : "#1f2328",
        "text_dim"    : "#57606a",
        "text_muted"  : "#afb8c1",
        "badge_bg"    : "#eaeef2",
        "name_color"  : "#0d1117",
    },
}

W = 860
H = 160

# ── SVG BUILDER ──────────────────────────────────────────────────────────────
def build_svg(theme_name):
    t = THEMES[theme_name]

    # Animated tagline cycling via SMIL
    tagline_anims = []
    n = len(TAGLINES)
    per = 3.0        # seconds per tagline
    total = per * n

    for i, tag in enumerate(TAGLINES):
        t_in   = round(i * per / total, 4)
        t_out  = round(((i + 1) * per - 0.3) / total, 4)
        t_next = round((i + 1) * per / total, 4)
        # opacity keyTimes: 0, fade_in, hold, fade_out, gone, loop
        key_times  = f"0;{t_in};{round(t_in+0.05,4)};{t_out};{round(t_out+0.05,4)};1"
        key_values = f"0;0;1;1;0;0"
        tagline_anims.append(
            f'<text x="{W//2}" y="102" text-anchor="middle" '
            f'font-family="\'Fira Code\',Consolas,monospace" font-size="13" '
            f'fill="{t["accent"]}" opacity="0">'
            f'{tag}'
            f'<animate attributeName="opacity" values="{key_values}" '
            f'keyTimes="{key_times}" dur="{total}s" repeatCount="indefinite"/>'
            f'</text>'
        )

    taglines_svg = "\n  ".join(tagline_anims)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="{t['accent']}"  stop-opacity="0.15"/>
      <stop offset="100%" stop-color="{t['accent2']}" stop-opacity="0.05"/>
    </linearGradient>
    <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="{t['accent']}"  stop-opacity="0.8"/>
      <stop offset="100%" stop-color="{t['accent2']}" stop-opacity="0.8"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="{W}" height="{H}" rx="12" fill="{t['bg']}"/>
  <rect width="{W}" height="{H}" rx="12" fill="url(#grad)"/>

  <!-- Border -->
  <rect width="{W}" height="{H}" rx="12" fill="none"
    stroke="{t['border']}" stroke-width="1"/>

  <!-- Accent top bar -->
  <rect x="32" y="0" width="120" height="3" rx="1.5" fill="url(#line)"/>

  <!-- Avatar placeholder circle -->
  <circle cx="72" cy="80" r="40" fill="{t['bg2']}" stroke="{t['border']}" stroke-width="1.5"/>
  <text x="72" y="86" text-anchor="middle"
    font-family="'Fira Code',Consolas,monospace" font-size="22"
    fill="{t['accent']}">F</text>

  <!-- Name -->
  <text x="132" y="58"
    font-family="'Segoe UI',system-ui,sans-serif" font-size="22" font-weight="700"
    fill="{t['name_color']}">{NAME}</text>

  <!-- Role -->
  <text x="132" y="80"
    font-family="'Fira Code',Consolas,monospace" font-size="13"
    fill="{t['text_dim']}">{ROLE}</text>

  <!-- Animated taglines -->
  {taglines_svg}

  <!-- Divider -->
  <line x1="132" y1="114" x2="{W-32}" y2="114"
    stroke="{t['border']}" stroke-width="1"/>

  <!-- Meta info row -->
  <text x="132" y="134"
    font-family="'Fira Code',Consolas,monospace" font-size="11.5"
    fill="{t['text_muted']}">
    <tspan fill="{t['accent']}">@</tspan>{GITHUB}
    <tspan dx="20" fill="{t['accent']}">&#9993;</tspan>
    <tspan dx="4">{EMAIL}</tspan>
    <tspan dx="20" fill="{t['accent']}">&#127759;</tspan>
    <tspan dx="4">{LOCATION}</tspan>
    <tspan dx="20" fill="{t['accent']}">&#128279;</tspan>
    <tspan dx="4">{PORTFOLIO}</tspan>
  </text>

  <!-- Blinking cursor -->
  <rect x="{W-48}" y="68" width="8" height="14" rx="1" fill="{t['accent']}">
    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
  </rect>

</svg>'''
    return svg


# ── WRITE FILES ───────────────────────────────────────────────────────────────
import os
REPO = os.path.dirname(os.path.abspath(__file__))

for theme_name in ["dark", "light"]:
    out = os.path.join(REPO, f"{theme_name}.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_svg(theme_name))
    print(f"Written: {out}")

print("Done! Commit dark.svg and light.svg to repo.")
