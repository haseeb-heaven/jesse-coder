from PIL import Image, ImageDraw, ImageFont

# CLI Interface Screenshot — terminal-style
W, H = 1280, 850
img = Image.new('RGB', (W, H), (10, 14, 18))  # dark terminal

d = ImageDraw.Draw(img)

# Terminal window frame (rounded corner effect via border)
d.rectangle([20, 20, W-20, H-20], outline=(60, 80, 120), width=2)
d.rounded_rectangle([20, 20, W-20, H-20], radius=8, outline=(40, 60, 100), width=3)

# Title bar
d.rectangle([20, 20, W-20, 70], fill=(18, 22, 30))
d.text((30, 30), "JesseCoder CLI — Autonomous Command Line Engineering Assistant", fill=(230, 230, 240), font=ImageFont.load_default())
d.text((30, 50), "Terminal • Python 3.12 • Safe Execution Sandbox • Streaming: ON", fill=(160, 160, 180), font=ImageFont.load_default())

# Prompt line
d.text((30, 100), "user@macbook jesse-coder % python3 interfaces/cli/main.py --prompt \"Write a Python script to compute Fibonacci\" --exec", fill=(220, 220, 220), font=ImageFont.load_default())

# Simulated streaming response (light blue text)
lines = [
    "▶ Generating code via Jesse API (jesse-prod)...",
    "▶ Extracted Python code block detected.",
    "▶ Executing in isolated subprocess (timeout 20.0s)...",
    "▶ Execution completed — exit code 0 (0ms).",
    "",
    "def fibonacci(n):",
    "    if n <= 1: return n",
    "    return fibonacci(n-1) + fibonacci(n-2)",
    "",
    "if __name__ == '__main__':",
    "    print(fibonacci(10))  # → 55",
    "",
    "Output: 55",
    "Status: PASS ✓",
]
y = 130
for line in lines:
    if line.startswith("▶") or line.startswith("Status:") or line.startswith("Output:"):
        color = (0, 220, 240)  # cyan
    elif line.startswith("def ") or line.startswith("    "):
        color = (220, 210, 180)  # light beige for code
    elif line.startswith("▶"):
        color = (200, 240, 255)
    else:
        color = (200, 210, 230)
    d.text((30, y), line, fill=color, font=ImageFont.load_default())
    y += 22

# Command input box at bottom
d.rectangle([20, H-100, W-20, H-20], fill=(18, 22, 30), outline=(60, 80, 120))
d.text((30, H-85), "(ctrl+r) Focus Prompt  (ctrl+e) Run Code  (ctrl+q) Quit  /clear  /exec  /model jesse-prod", fill=(160, 160, 180), font=ImageFont.load_default())

# Bottom status bar
d.rectangle([20, H-30, W-20, H-20], fill=(14, 18, 26))
d.text((30, H-25), "CLI v2.4 • Auto-Run: OFF • Model: jesse-prod • Temperature: 0.2", fill=(140, 150, 160), font=ImageFont.load_default())

img.save('/Users/haseeb-mir/Documents/Code/Python/jesse-coder/docs/images/cli_interface.png')
print("Created cli_interface.png")

# ──────────────────────────────────────────────────────────────────────
# TUI Interface Screenshot — dual-pane Textual royal-blue theme
# ──────────────────────────────────────────────────────────────────────
W, H = 1280, 850
img = Image.new('RGB', (W, H), (0, 0, 0))  # pure black for TUI
d = ImageDraw.Draw(img)

# Fonts
try:
    font_header = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    font_body = ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", 14)
    font_bold = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
except:
    font_header = ImageFont.load_default()
    font_title = ImageFont.load_default()
    font_body = ImageFont.load_default()
    font_bold = ImageFont.load_default()

# Header bar
HEIGHT = 60
d.rectangle([0, 0, W, HEIGHT], fill=(17, 24, 39))  # gray-900
d.text((20, 10), "JesseCoder · Autonomous Engineering Assistant", fill=(248, 250, 252), font=font_header)
d.text((20, 35), "Code Generation · Execution Engine", fill=(141, 162, 192), font=font_title)

# Top status bar
SBAR_Y = HEIGHT + 1
d.rectangle([0, SBAR_Y, W, SBAR_Y+24], fill=(17, 24, 39))
d.text((10, SBAR_Y+5), "● ONLINE: jesse-prod", fill=(140, 220, 255), font=font_body)
d.text((180, SBAR_Y+5), "Model: jesse-prod", fill=(160, 160, 180), font=font_body)
d.text((340, SBAR_Y+5), "Lang: python", fill=(160, 160, 180), font=font_body)
d.text((470, SBAR_Y+5), "Auto-Run: ON", fill=(160, 160, 180), font=font_body)
d.text((590, SBAR_Y+5), "Raw API ▶", fill=(100, 100, 120), font=font_body)
d.text((680, SBAR_Y+5), "Ctrl+E: Run Code | Ctrl+Q: Quit", fill=(100, 100, 120), font=font_body)

# Main body area
MBODY_Y = SBAR_Y + 25
DCK_BOT = 120  # bottom dock height
MAIN_H = H - MBODY_Y - DCK_BOT

# Vertical divider
DIV_X = W // 2 + 50
d.rectangle([DIV_X, MBODY_Y, DIV_X, MBODY_Y+MAIN_H], fill=(40, 40, 40))

# CHAT PANE (left)
d.rounded_rectangle([10, MBODY_Y, DIV_X-15, MBODY_Y+MAIN_H], radius=4, outline=(40, 52, 77), width=2)
d.text((20, MBODY_Y+8), "Chat", fill=(113, 215, 255), font=font_bold)

# Chat messages
chat_y = MBODY_Y + 40
chat_lines = [
    ("JesseCoder Bot", (160, 240, 255), "I'll write a Fibonacci function for you."),
    ("You", (220, 220, 220), "Compute fib(10)"),
    ("JesseCoder Bot", (160, 240, 255), "```python\ndef fib(n):\n    return n if n<=1 else fib(n-1)+fib(n-2)\n```"),
    ("JesseCoder Bot", (160, 240, 255), "▶ Executing in sandbox... exit 0 · 0ms"),
    ("JesseCoder Bot", (113, 215, 255), "Output: 55")
]
for sender, color, msg in chat_lines:
    d.text((20, chat_y), f"[{sender}] ", fill=color, font=font_body)
    d.text((20+60, chat_y), msg, fill=(200, 210, 230), font=font_body)
    chat_y += 28

# Input dock at bottom of chat pane
DOCK_Y = MBODY_Y + MAIN_H - 50
d.rectangle([15, DOCK_Y, DIV_X-20, MBODY_Y+MAIN_H], fill=(13, 19, 32), outline=(40, 52, 77))
d.text((25, DOCK_Y+20), "Ask a coding question, paste code to review... ➜", fill=(80, 90, 110), font=font_body)
d.rectangle([20, DOCK_Y+38, 200, MBODY_Y+MAIN_H-5], fill=(200, 200, 220), outline=(200, 200, 220))
d.text((40, DOCK_Y+40), "Send", fill=(0, 0, 0), font=font_body)

# WORKBENCH PANE (right)
d.rounded_rectangle([DIV_X+15, MBODY_Y, W-10, MBODY_Y+MAIN_H], radius=4, outline=(40, 52, 77), width=2)
d.text((DIV_X+30, MBODY_Y+8), "Code Workbench", fill=(113, 215, 255), font=font_bold)
d.text((DIV_X+30, MBODY_Y+28), "Auto-detect  ·  none · 0 lines", fill=(100, 110, 130), font=font_body)

# Code area
CODE_Y = MBODY_Y + 55
d.rectangle([DIV_X+20, CODE_Y, W-20, DOCK_Y-10], fill=(13, 19, 32), outline=(40, 52, 77))
code_lines = [
    ("", (120, 130, 140)),
    ("# No code extracted yet.", (120, 130, 140)),
    ("# Send a coding prompt to generate code here.", (120, 130, 140)),
    ("", (120, 130, 140)),
    ("def fibonacci(n):", (220, 210, 180)),
    ("    if n <= 1: return n", (220, 210, 180)),
    ("    return fibonacci(n-1) + fibonacci(n-2)", (220, 210, 180)),
    ("", (120, 130, 140)),
    ("# Result: 55", (0, 220, 240)),
]
for i, (text, color) in enumerate(code_lines):
    d.text((DIV_X+30, CODE_Y+i*20), text, fill=color, font=font_body)

# Buttons row
BTN_Y = DOCK_Y - 30
d.rounded_rectangle([DIV_X+20, BTN_Y, DIV_X+130, BTN_Y+30], radius=4, fill=(22, 33, 51), outline=(113, 215, 255))
d.text((DIV_X+35, BTN_Y+8), "▶ Run Code", fill=(113, 215, 255), font=font_body)
d.rounded_rectangle([DIV_X+140, BTN_Y, DIV_X+250, BTN_Y+30], radius=4, fill=(22, 33, 51), outline=(113, 215, 255))
d.text((DIV_X+155, BTN_Y+8), "📋 Copy", fill=(113, 215, 255), font=font_body)
d.rounded_rectangle([DIV_X+260, BTN_Y, DIV_X+340, BTN_Y+30], radius=4, fill=(22, 33, 51), outline=(113, 215, 255))
d.text((DIV_X+275, BTN_Y+8), "⟳ Reset", fill=(113, 215, 255), font=font_body)

# Bottom dock (console output)
d.rectangle([0, H-DCK_BOT, W, H], fill=(13, 19, 32), outline=(40, 52, 77))
d.text((10, H-DCK_BOT+8), "Console [IDLE]", fill=(113, 215, 255), font=font_body)
d.text([W-80, H-DCK_BOT+8], "Clear", fill=(120, 130, 140), font=font_body)
d.text((20, H-DCK_BOT+35), "Console ready. Click [Run] or enable Auto-Run.", fill=(80, 90, 110), font=font_body)

img.save('/Users/haseeb-mir/Documents/Code/Python/jesse-coder/docs/images/tui_interface.png')
print("Created tui_interface.png")

