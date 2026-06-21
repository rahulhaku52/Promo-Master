import os
import io
import asyncio
import requests
import random
import tempfile
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from moviepy.editor import (
    ImageClip, AudioFileClip,
    CompositeVideoClip
)
import moviepy.audio.fx.all as afx

# ==========================================
# 1. CONFIGURATION
# ==========================================
PAGE_ID          = os.environ.get('FACEBOOK_PAGE_ID')
ACCESS_TOKEN     = os.environ.get('FACEBOOK_ACCESS_TOKEN')
PIXABAY_API_KEY  = os.environ.get('PIXABAY_API_KEY')
PEXELS_API_KEY   = os.environ.get('PEXELS_API_KEY')
UNSPLASH_API_KEY = os.environ.get('UNSPLASH_API_KEY')

LOGO_PATH = "logo.png"

# Duration
MIN_DURATION    = 20
MAX_DURATION    = 45
TARGET_DURATION = 30

# Bengali Font
BENGALI_FONT_BOLD = "/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf"
BENGALI_FONT_REG  = "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf"

# edge-tts voices (Bengali + Hindi + English)
EDGE_VOICES = [
    "bn-BD-NabanitaNeural",   # Bengali Female
    "bn-BD-PradeepNeural",    # Bengali Male
    "bn-IN-TanishaaNeural",   # Bengali India Female
    "hi-IN-SwaraNeural",      # Hindi Female
    "hi-IN-MadhurNeural",     # Hindi Male
    "en-US-JennyNeural",      # English Fallback
]

# ==========================================
# 2. CONTENT — ALL ENGLISH ✅
# ==========================================

# English Hooks
HOOKS = [
    "🔥 Stop! This tip will change everything!",
    "💡 Watch closely — this is gold!",
    "🚀 Want to learn pro tips? Stay tuned!",
    "📌 Did you know this secret?",
    "⚡ Learn this in 30 seconds!",
    "🎯 Don't miss out on this!",
    "🔑 This one tip can save hours!",
    "💥 Game changer alert!"
]

# English Facts
FACTS_EN = [
    "Website load time over 3 seconds loses 50% of visitors",
    "Mobile-friendly websites rank higher on Google Search",
    "React JS is the most demanded skill in 2026",
    "You can build a web app in 10 minutes with Python",
    "Modern apps are incomplete without API integration",
    "Flutter lets you build Android & iOS apps together",
    "SEO without content is like a car without fuel",
    "Good UI design improves user experience by 10x",
    "Node.js makes real-time apps easy to build",
    "TypeScript reduces bugs in large projects significantly"
]

# English Tips
TIPS_EN = [
    "Use CSS Grid for layouts — easy & fast",
    "Use async/await in JavaScript — escape callback hell",
    "Use Git for version control — never lose your code",
    "Learn VS Code shortcuts — work 3x faster",
    "Deploy projects with Docker — reliable & simple",
    "TypeScript is a must for large-scale projects",
    "Practice coding at least 1 hour every day",
    "Master Stack Overflow & GitHub for better solutions"
]

# English Reviews
REVIEWS_EN = [
    "My website was built in just 2 days! Amazing work!",
    "The app is super fast and user-friendly — client loved it!",
    "The design was exactly like my dream — perfect delivery!",
    "Professional work, on-time delivery — 100% satisfied!",
    "Low cost, best quality — I will hire again!"
]

# English Image Texts (short, punchy)
IMAGE_TEXTS = [
    "Web Development Tips",
    "Coding Hacks That Work",
    "App Development Secrets",
    "Tech Tips for 2025",
    "Programming Tricks",
    "Build Something Amazing",
    "Level Up Your Skills",
    "Code Smarter Not Harder",
    "Full Stack Developer Tips",
    "React JS Pro Tips"
]

# English Voice Scripts (longer for audio duration)
VOICE_SCRIPTS_EN = [
    "Did you know? Website load time over 3 seconds loses half of your visitors. Optimize your site today for better results.",
    "React JS is the most demanded skill in 2026. Start learning today and boost your career to the next level.",
    "Mobile friendly websites rank higher on Google. Make sure your website looks great on all devices.",
    "Python is so powerful that you can build a web app in just 10 minutes. Start your coding journey now.",
    "Good UI design improves user experience by ten times. Invest in design and watch your business grow.",
    "Git version control saves your code from disasters. Learn Git today and never lose your work again.",
    "Flutter lets you build Android and iOS apps with one codebase. Save time and money with cross platform development.",
    "SEO is the backbone of digital marketing. Without SEO your website is invisible to the world.",
    "Node JS makes building real time applications super easy. Learn it and build the next big app.",
    "TypeScript reduces bugs in large projects. Switch from JavaScript to TypeScript for cleaner code."
]

VOICE_SCRIPTS_BN = [
    "জানেন কি? ওয়েবসাইটের লোড টাইম ৩ সেকেন্ডের বেশি হলে ৫০% ভিজিটর চলে যায়। আজই আপনার সাইট অপ্টিমাইজ করুন।",
    "React JS ২০২৬ সালে সবচেয়ে বেশি চাহিদার স্কিল। আজই শেখা শুরু করুন এবং আপনার ক্যারিয়ার এগিয়ে নিন।",
    "মোবাইল ফ্রেন্ডলি ওয়েবসাইট গুগলে বেশি র‍্যাঙ্ক পায়। আপনার ওয়েবসাইট সব ডিভাইসে সুন্দর দেখাচ্ছে তো?",
    "Python দিয়ে মাত্র ১০ মিনিটে ওয়েব অ্যাপ বানানো যায়। আজই কোডিং শুরু করুন।",
    "ভালো UI ডিজাইন ব্যবহারকারীর অভিজ্ঞতা ১০ গুণ বাড়িয়ে দেয়। ডিজাইনে বিনিয়োগ করুন।",
    "Git দিয়ে কোড ভার্সন কন্ট্রোল করুন। আপনার কোড কখনো হারাবে না।",
    "Flutter দিয়ে Android ও iOS দুটো অ্যাপ একসাথে বানানো যায়। সময় ও অর্থ দুটোই বাঁচান।",
    "SEO ছাড়া ওয়েবসাইট থাকা মানে অন্ধকারে থাকা। আজই SEO শুরু করুন।"
]

VOICE_SCRIPTS_HI = [
    "क्या आप जानते हैं? वेबसाइट की लोडिंग 3 सेकंड से ज्यादा होने पर 50% विजिटर चले जाते हैं। आज ही ऑप्टिमाइज़ करें।",
    "React JS 2026 में सबसे ज्यादा डिमांडेड स्किल है। आज से ही सीखना शुरू करें और अपना करियर बनाएं।",
    "Mobile friendly website Google पर ज्यादा rank पाती है। अपनी website को mobile friendly बनाएं।",
    "Python से सिर्फ 10 मिनट में web app बना सकते हैं। आज से ही coding शुरू करें।",
    "अच्छा UI design user experience 10 गुना बेहतर बनाता है। Design में invest करें।"
]

# Hashtags
FIXED_HASHTAGS = [
    "#webdevelopment", "#appdevelopment", "#shorts",
    "#codingtips", "#programming", "#tech"
]

TRENDING_TAGS = [
    "#webdesign", "#developer", "#coder", "#frontend",
    "#backend", "#fullstack", "#reactjs", "#python",
    "#javascript", "#nodejs", "#flutter", "#android",
    "#ios", "#uiux", "#startup", "#digitalmarketing",
    "#seo", "#wordpress", "#laravel", "#entrepreneur"
]

PIXABAY_THEMES = [
    "technology", "coding", "computer",
    "programming", "laptop", "digital",
    "startup", "software", "internet"
]

# ==========================================
# 3. COLOR THEMES
# ==========================================
COLOR_THEMES = [
    {
        "name": "Deep Ocean",
        "color1": (5, 10, 48),
        "color2": (0, 80, 180),
        "accent": (0, 200, 255),
        "highlight": (0, 230, 255)
    },
    {
        "name": "Sunset Fire",
        "color1": (40, 5, 5),
        "color2": (180, 60, 0),
        "accent": (255, 150, 0),
        "highlight": (255, 200, 50)
    },
    {
        "name": "Purple Galaxy",
        "color1": (15, 5, 40),
        "color2": (80, 0, 150),
        "accent": (180, 0, 255),
        "highlight": (220, 150, 255)
    },
    {
        "name": "Forest Dark",
        "color1": (5, 25, 15),
        "color2": (0, 80, 50),
        "accent": (0, 200, 100),
        "highlight": (100, 255, 180)
    },
    {
        "name": "Steel Blue",
        "color1": (10, 20, 35),
        "color2": (30, 60, 120),
        "accent": (80, 160, 255),
        "highlight": (150, 220, 255)
    },
    {
        "name": "Neon Dark",
        "color1": (5, 5, 5),
        "color2": (20, 20, 40),
        "accent": (255, 0, 150),
        "highlight": (0, 255, 200)
    }
]

# ==========================================
# 4. FONT LOADER
# ==========================================
def load_fonts():
    bold_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
        BENGALI_FONT_BOLD,
    ]
    reg_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        BENGALI_FONT_REG,
    ]
    bold = next((p for p in bold_paths if os.path.exists(p)), None)
    reg  = next((p for p in reg_paths  if os.path.exists(p)), None)
    print(f"✅ Bold font: {os.path.basename(bold) if bold else 'default'}")
    print(f"✅ Reg font:  {os.path.basename(reg)  if reg  else 'default'}")
    return {'bold': bold, 'regular': reg or bold}


# ==========================================
# 5. PIL TEXT OVERLAY (English — No Font Issue)
# ==========================================
def create_text_overlay(text, img_width=1200, accent_color=(0, 200, 255)):
    """
    PIL দিয়ে English subtitle image তৈরি।
    MoviePy TextClip এর বদলে ImageClip হিসেবে ব্যবহার।
    """
    font_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    font_path = next((p for p in font_paths if os.path.exists(p)), None)

    try:
        font       = ImageFont.truetype(font_path, 38) if font_path else ImageFont.load_default()
        font_small = ImageFont.truetype(font_path, 24) if font_path else ImageFont.load_default()
    except Exception:
        font = font_small = ImageFont.load_default()

    # Word wrap
    words, lines, current = text.split(), [], ""
    for word in words:
        test = f"{current} {word}".strip()
        if len(test) * 23 <= img_width - 80:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    lines = lines[:3]

    line_h = 55
    pad    = 18
    box_h  = len(lines) * line_h + pad * 2 + 42

    overlay = Image.new('RGBA', (img_width, box_h), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)

    # Background gradient
    for y in range(box_h):
        alpha = int(160 + 60 * (y / box_h))
        draw.line([(0, y), (img_width, y)], fill=(0, 0, 0, alpha))

    # Top accent line
    draw.rectangle([(0, 0), (img_width, 4)], fill=(*accent_color, 230))

    # Text
    y_pos = pad
    for i, line in enumerate(lines):
        draw.text((52, y_pos + 2), line, font=font, fill=(0, 0, 0, 210))
        color = (*accent_color, 255) if i == 0 else (255, 255, 255, 255)
        draw.text((50, y_pos), line, font=font, fill=color)
        y_pos += line_h

    # Contact bar
    contact = "📧 rahulhaku52@gmail.com  |  📱 t.me/hacker_52"
    draw.rectangle([(0, box_h - 38), (img_width, box_h)], fill=(0, 0, 0, 230))
    draw.text((50, box_h - 30), contact, font=font_small, fill=(200, 200, 200, 255))

    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    overlay.save(tmp.name)
    print(f"✅ Text overlay created")
    return tmp.name


# ==========================================
# 6. VOICE GENERATOR (Bengali/Hindi/English)
# ==========================================
async def _edge_generate(text, voice, path):
    await edge_tts.Communicate(text, voice).save(path)


def generate_voice(text):
    """
    ✅ Voice language rotation:
    Bengali → Hindi → English
    """
    tmp = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)

    # Extended text for longer audio
    extended = (
        f"{text}. "
        f"Follow us for daily tech tips. "
        f"Contact: rahulhaku52 at gmail dot com "
        f"or Telegram t dot me slash hacker underscore 52."
    )

    for voice in EDGE_VOICES:
        try:
            asyncio.run(_edge_generate(extended, voice, tmp.name))
            if os.path.exists(tmp.name) and os.path.getsize(tmp.name) > 1000:
                print(f"✅ Voice: {voice}")
                return tmp.name, voice
        except Exception as e:
            print(f"⚠️ edge-tts {voice}: {e}")

    # Fallback gTTS
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(tmp.name)
        print("✅ Voice: gTTS (en) fallback")
        return tmp.name, 'en-gTTS'
    except Exception as e:
        print(f"❌ All voice failed: {e}")

    return tmp.name, 'none'


def pick_voice_text():
    """
    Random rotation: Bengali → Hindi → English voice scripts
    """
    choice = random.choices(
        ['bn', 'hi', 'en'],
        weights=[40, 30, 30]
    )[0]

    if choice == 'bn':
        return random.choice(VOICE_SCRIPTS_BN), 'bn'
    elif choice == 'hi':
        return random.choice(VOICE_SCRIPTS_HI), 'hi'
    else:
        return random.choice(VOICE_SCRIPTS_EN), 'en'


# ==========================================
# 7. IMAGE SOURCES
# ==========================================
def fetch_pixabay_image(query):
    if not PIXABAY_API_KEY:
        return None
    try:
        url = (
            f"https://pixabay.com/api/?key={PIXABAY_API_KEY}"
            f"&q={query}&image_type=photo&category=technology"
            f"&orientation=horizontal&per_page=10&safesearch=true"
            f"&min_width=1200&min_height=600"
        )
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            hits = r.json().get('hits', [])
            if hits:
                chosen  = random.choice(hits[:5])
                img_url = chosen.get('webformatURL') or chosen.get('largeImageURL')
                ir = requests.get(img_url, timeout=20)
                if ir.status_code == 200:
                    img = Image.open(io.BytesIO(ir.content)).convert('RGB')
                    img = img.resize((1200, 628), Image.LANCZOS)
                    print(f"✅ Pixabay: {chosen.get('tags','')[:30]}")
                    return img
    except Exception as e:
        print(f"⚠️ Pixabay: {e}")
    return None


def fetch_pexels_image(query):
    if not PEXELS_API_KEY:
        return None
    try:
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=10&orientation=landscape"
        r = requests.get(url, headers={"Authorization": PEXELS_API_KEY}, timeout=15)
        if r.status_code == 200:
            photos = r.json().get('photos', [])
            if photos:
                chosen = random.choice(photos[:5])
                ir = requests.get(chosen['src']['large'], timeout=20)
                if ir.status_code == 200:
                    img = Image.open(io.BytesIO(ir.content)).convert('RGB')
                    img = img.resize((1200, 628), Image.LANCZOS)
                    print("✅ Pexels image")
                    return img
    except Exception as e:
        print(f"⚠️ Pexels: {e}")
    return None


def fetch_unsplash_image(query):
    if not UNSPLASH_API_KEY:
        return None
    try:
        url = (
            f"https://api.unsplash.com/photos/random"
            f"?query={query}&orientation=landscape&count=1"
        )
        r = requests.get(
            url,
            headers={"Authorization": f"Client-ID {UNSPLASH_API_KEY}"},
            timeout=15
        )
        if r.status_code == 200:
            data    = r.json()
            img_url = None
            if isinstance(data, list) and data:
                img_url = data[0].get('urls', {}).get('regular')
            elif isinstance(data, dict):
                img_url = data.get('urls', {}).get('regular')
            if img_url:
                ir = requests.get(img_url, timeout=20)
                if ir.status_code == 200:
                    img = Image.open(io.BytesIO(ir.content)).convert('RGB')
                    img = img.resize((1200, 628), Image.LANCZOS)
                    print("✅ Unsplash image")
                    return img
    except Exception as e:
        print(f"⚠️ Unsplash: {e}")
    return None


# ==========================================
# 8. GRADIENT BACKGROUND
# ==========================================
def create_gradient_background(theme, width=1200, height=628):
    img  = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    c1, c2, accent = theme['color1'], theme['color2'], theme['accent']

    for y in range(height):
        t = y / height
        draw.line(
            [(0, y), (width, y)],
            fill=(
                int(c1[0] + (c2[0] - c1[0]) * t),
                int(c1[1] + (c2[1] - c1[1]) * t),
                int(c1[2] + (c2[2] - c1[2]) * t),
            )
        )

    ov = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse([width - 300, -100, width + 50, 300], fill=(*accent, 20))
    od.ellipse([-80, height - 250, 200, height + 30], fill=(*accent, 15))

    img = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
    print("✅ Gradient background")
    return img


# ==========================================
# 9. PROFESSIONAL OVERLAY
# ==========================================
def add_professional_overlay(img, theme):
    width, height = img.size
    ov = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)

    for y in range(height):
        alpha = int(50 + 120 * (y / height))
        od.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))

    # Bottom gradient bar for text readability
    for y in range(height - 220, height):
        t     = (y - (height - 220)) / 220
        alpha = int(200 * t)
        od.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))

    img  = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
    draw = ImageDraw.Draw(img)
    accent = theme['accent']
    draw.rectangle([(0, 0), (width, 5)], fill=accent)
    draw.rectangle([(0, height - 5), (width, height)], fill=accent)
    return img


# ==========================================
# 10. TEXT WRAP
# ==========================================
def wrap_text(text, font, max_width, draw):
    words, lines, current = text.split(), [], ""
    for word in words:
        test = f"{current} {word}".strip()
        try:
            w = draw.textlength(test, font=font)
        except Exception:
            w = len(test) * 20
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ==========================================
# 11. LAYOUTS (English Text — Clean)
# ==========================================
def draw_bottom_card(img, draw, text, hook, theme, fonts, width, height):
    accent, highlight = theme['accent'], theme['highlight']
    f_large  = fonts['large']
    f_small  = fonts['small']
    f_tiny   = fonts['tiny']

    card_y = int(height * 0.46)

    ov = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.rectangle([0, card_y, width, height], fill=(0, 0, 0, 190))
    od.rectangle([0, card_y, width, card_y + 5], fill=(*accent, 230))
    merged = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
    img.paste(merged)
    draw = ImageDraw.Draw(img)

    # Hook
    draw.text((40, card_y + 14), hook, fill=highlight, font=f_small)
    draw.rectangle([(40, card_y + 50), (200, card_y + 53)], fill=accent)

    # Main text
    lines = wrap_text(text, f_large, width - 80, draw)
    y_pos = card_y + 65
    for i, line in enumerate(lines[:3]):
        draw.text((42, y_pos + 2), line, fill=(0, 0, 0), font=f_large)
        draw.text((40, y_pos), line,
                  fill=highlight if i == 0 else (255, 255, 255), font=f_large)
        y_pos += 52

    # Bottom bar
    draw.rectangle([0, height - 44, width, height], fill=(0, 0, 0))
    draw.rectangle([0, height - 44, width, height - 41], fill=accent)
    contact = "📧 rahulhaku52@gmail.com  |  📱 t.me/hacker_52"
    try:
        cw = int(draw.textlength(contact, font=f_tiny))
    except Exception:
        cw = 500
    draw.text(((width - cw) // 2, height - 33),
              contact, fill=(210, 210, 210), font=f_tiny)


def draw_center_bold(img, draw, text, hook, theme, fonts, width, height):
    accent, highlight = theme['accent'], theme['highlight']
    f_large = fonts['large']
    f_small = fonts['small']
    f_tiny  = fonts['tiny']

    ov     = Image.new('RGBA', (width, height), (0, 0, 0, 170))
    merged = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
    img.paste(merged)
    draw = ImageDraw.Draw(img)

    # Top bar
    draw.rectangle([(0, 0), (width, 6)], fill=accent)
    draw.text((40, 16), "⚡ @hacker_52", fill=(255, 255, 255), font=f_small)

    # Hook centered
    try:
        hw = int(draw.textlength(hook, font=f_small))
    except Exception:
        hw = 300
    draw.text(((width - hw) // 2, 75), hook, fill=highlight, font=f_small)
    draw.rectangle([(width // 2 - 80, 115), (width // 2 + 80, 119)], fill=accent)

    # Main text
    lines = wrap_text(text, f_large, width - 120, draw)
    y_pos = 138
    for i, line in enumerate(lines[:3]):
        try:
            lw = int(draw.textlength(line, font=f_large))
        except Exception:
            lw = len(line) * 25
        x = (width - lw) // 2
        draw.text((x + 2, y_pos + 2), line, fill=(0, 0, 0), font=f_large)
        draw.text((x, y_pos), line,
                  fill=highlight if i == 0 else (255, 255, 255), font=f_large)
        y_pos += 56

    # Bottom
    draw.rectangle([(0, height - 6), (width, height)], fill=accent)
    draw.rectangle([(0, height - 44), (width, height - 6)], fill=(0, 0, 0))
    contact = "📧 rahulhaku52@gmail.com  |  📱 t.me/hacker_52"
    try:
        cw = int(draw.textlength(contact, font=f_tiny))
    except Exception:
        cw = 500
    draw.text(((width - cw) // 2, height - 35),
              contact, fill=(210, 210, 210), font=f_tiny)


def draw_top_title(img, draw, text, hook, theme, fonts, width, height):
    accent, highlight = theme['accent'], theme['highlight']
    f_large = fonts['large']
    f_small = fonts['small']
    f_tiny  = fonts['tiny']

    card_h = int(height * 0.44)
    ov = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.rectangle([0, 0, width, card_h], fill=(0, 0, 0, 195))
    od.rectangle([0, card_h - 5, width, card_h], fill=(*accent, 220))
    merged = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
    img.paste(merged)
    draw = ImageDraw.Draw(img)

    # Brand + date
    draw.text((40, 15), "⚡ @hacker_52", fill=accent, font=f_small)
    date_str = datetime.now().strftime("%d %b %Y")
    try:
        dw = int(draw.textlength(date_str, font=f_tiny))
    except Exception:
        dw = 90
    draw.text((width - dw - 30, 20), date_str, fill=(180, 180, 180), font=f_tiny)

    # Hook
    draw.text((40, 58), hook, fill=highlight, font=f_small)

    # Main text
    lines = wrap_text(text, f_large, width - 80, draw)
    y_pos = 100
    for i, line in enumerate(lines[:3]):
        draw.text((42, y_pos + 2), line, fill=(0, 0, 0), font=f_large)
        draw.text((40, y_pos), line,
                  fill=highlight if i == 0 else (255, 255, 255), font=f_large)
        y_pos += 52

    # Bottom bar
    bot_ov = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bot_ov)
    bd.rectangle([0, height - 48, width, height], fill=(0, 0, 0, 210))
    img.paste(Image.alpha_composite(img.convert('RGBA'), bot_ov).convert('RGB'))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, height - 48, width, height - 45], fill=accent)
    contact = "📧 rahulhaku52@gmail.com  |  📱 t.me/hacker_52"
    try:
        cw = int(draw.textlength(contact, font=f_tiny))
    except Exception:
        cw = 500
    draw.text(((width - cw) // 2, height - 38),
              contact, fill=(210, 210, 210), font=f_tiny)


# ==========================================
# 12. ADD TEXT TO IMAGE
# ==========================================
def add_stylish_text(img, text, hook, theme, font_paths, layout):
    draw = ImageDraw.Draw(img)
    width, height = img.size

    try:
        bp = font_paths.get('bold')
        rp = font_paths.get('regular') or bp
        if bp and os.path.exists(bp):
            fonts = {
                'large':  ImageFont.truetype(bp, 46),
                'medium': ImageFont.truetype(bp, 33),
                'small':  ImageFont.truetype(rp, 28),
                'tiny':   ImageFont.truetype(rp, 22),
            }
        else:
            raise OSError
    except Exception:
        d = ImageFont.load_default()
        fonts = {'large': d, 'medium': d, 'small': d, 'tiny': d}
        print("⚠️ Default font")

    args = (img, draw, text, hook, theme, fonts, width, height)
    if layout == 'bottom_card':
        draw_bottom_card(*args)
    elif layout == 'center_bold':
        draw_center_bold(*args)
    elif layout == 'top_title':
        draw_top_title(*args)

    return img


# ==========================================
# 13. LOGO ON IMAGE
# ==========================================
def add_logo_to_image(img):
    if not os.path.exists(LOGO_PATH):
        return img
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        iw, ih = img.size
        lw = iw // 7
        lh = int(logo.size[1] * (lw / logo.size[0]))
        logo = logo.resize((lw, lh), Image.LANCZOS)
        base = img.convert('RGBA')
        base.paste(logo, (iw - lw - 20, ih - lh - 55), logo)
        img = base.convert('RGB')
        print("✅ Logo added")
    except Exception as e:
        print(f"⚠️ Logo: {e}")
    return img


# ==========================================
# 14. MAIN IMAGE GENERATOR
# ==========================================
def generate_image(image_text, hook):
    width, height = 1200, 628
    theme      = random.choice(COLOR_THEMES)
    font_paths = load_fonts()
    query      = random.choice(PIXABAY_THEMES)

    img = fetch_pixabay_image(query)
    if img is None:
        img = fetch_pexels_image(query)
    if img is None:
        img = fetch_unsplash_image(query)
    if img is None:
        img = create_gradient_background(theme, width, height)
    else:
        img = add_professional_overlay(img, theme)

    layout = random.choice(['bottom_card', 'center_bold', 'top_title'])
    print(f"✅ Layout: {layout} | Theme: {theme['name']}")

    img = add_stylish_text(img, image_text, hook, theme, font_paths, layout)
    img = add_logo_to_image(img)

    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(tmp.name, quality=95)
    return tmp.name


# ==========================================
# 15. VIDEO CREATOR
# ==========================================
def create_video(image_path, voice_path, subtitle_text, theme_accent=(0, 200, 255)):
    output_path = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
    overlay_path = None

    try:
        audio_clip = AudioFileClip(voice_path)
        audio_dur  = audio_clip.duration
        print(f"🎙️ Audio: {audio_dur:.1f}s")

        video_dur = max(audio_dur, MIN_DURATION, TARGET_DURATION)
        video_dur = min(video_dur, MAX_DURATION)
        print(f"🎬 Video: {video_dur:.1f}s")

        if audio_dur < video_dur:
            audio_clip = audio_clip.fx(afx.audio_loop, duration=video_dur)
            print(f"🔁 Audio looped to {video_dur:.1f}s")

        img_clip   = ImageClip(image_path, duration=video_dur)
        final_clip = img_clip.set_audio(audio_clip)

        # ✅ PIL subtitle (no TextClip — no font issue)
        overlay_path = create_text_overlay(subtitle_text, 1200, theme_accent)
        text_clip = (
            ImageClip(overlay_path)
            .set_position(('center', 'bottom'))
            .set_duration(min(12, video_dur))
            .set_opacity(0.93)
        )

        # Logo clip
        logo_clip = _get_logo_clip(video_dur)

        clips = [final_clip, text_clip]
        if logo_clip:
            clips.append(logo_clip)

        final = CompositeVideoClip(clips)
        final.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None,
            preset='fast'
        )
        print(f"✅ Video: {output_path}")

    except Exception as e:
        print(f"⚠️ Video error: {e}")
        import traceback
        traceback.print_exc()
        img_clip = ImageClip(image_path, duration=MIN_DURATION)
        img_clip.write_videofile(output_path, fps=24, verbose=False, logger=None)

    finally:
        if overlay_path and os.path.exists(overlay_path):
            try:
                os.unlink(overlay_path)
            except Exception:
                pass

    return output_path


# ==========================================
# 16. LOGO CLIP
# ==========================================
def _get_logo_clip(video_dur):
    start_t = max(0, video_dur - 4)
    if os.path.exists(LOGO_PATH):
        try:
            return (
                ImageClip(LOGO_PATH)
                .resize(height=75)
                .set_position(('right', 'bottom'))
                .set_duration(4)
                .set_start(start_t)
                .set_opacity(0.90)
            )
        except Exception as e:
            print(f"⚠️ Logo clip: {e}")
    return None


# ==========================================
# 17. TRENDING HASHTAGS
# ==========================================
def fetch_trending_tags():
    if PIXABAY_API_KEY:
        try:
            query = random.choice(PIXABAY_THEMES)
            r = requests.get(
                f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&per_page=5&category=technology",
                timeout=10
            )
            if r.status_code == 200:
                tags = []
                for hit in r.json().get('hits', [])[:3]:
                    for tag in hit.get('tags', '').split(',')[:1]:
                        c = tag.strip().replace(' ', '')
                        if c and len(c) > 2:
                            tags.append(f"#{c}")
                if tags:
                    return tags[:2]
        except Exception as e:
            print(f"⚠️ Pixabay tags: {e}")

    if PEXELS_API_KEY:
        try:
            r = requests.get(
                "https://api.pexels.com/v1/popular?per_page=5",
                headers={"Authorization": PEXELS_API_KEY},
                timeout=10
            )
            if r.status_code == 200:
                tags = []
                for p in r.json().get('photos', [])[:2]:
                    alt = p.get('alt', '').replace(' ', '')
                    if alt:
                        tags.append(f"#{alt[:15]}")
                if tags:
                    return tags
        except Exception as e:
            print(f"⚠️ Pexels tags: {e}")

    return random.sample(TRENDING_TAGS, 2)


# ==========================================
# 18. UNICODE STYLES
# ==========================================
def bold_unicode(t):
    m = {
        'a':'𝗮','b':'𝗯','c':'𝗰','d':'𝗱','e':'𝗲','f':'𝗳','g':'𝗴',
        'h':'𝗵','i':'𝗶','j':'𝗷','k':'𝗸','l':'𝗹','m':'𝗺','n':'𝗻',
        'o':'𝗼','p':'𝗽','q':'𝗾','r':'𝗿','s':'𝘀','t':'𝘁','u':'𝘂',
        'v':'𝘃','w':'𝘄','x':'𝘅','y':'𝘆','z':'𝘇',
        'A':'𝗔','B':'𝗕','C':'𝗖','D':'𝗗','E':'𝗘','F':'𝗙','G':'𝗚',
        'H':'𝗛','I':'𝗜','J':'𝗝','K':'𝗞','L':'𝗟','M':'𝗠','N':'𝗡',
        'O':'𝗢','P':'𝗣','Q':'𝗤','R':'𝗥','S':'𝗦','T':'𝗧','U':'𝗨',
        'V':'𝗩','W':'𝗪','X':'𝗫','Y':'𝗬','Z':'𝗭'
    }
    return ''.join(m.get(c, c) for c in t)

def italic_unicode(t):
    m = {
        'a':'𝘢','b':'𝘣','c':'𝘤','d':'𝘥','e':'𝘦','f':'𝘧','g':'𝘨',
        'h':'𝘩','i':'𝘪','j':'𝘫','k':'𝘬','l':'𝘭','m':'𝘮','n':'𝘯',
        'o':'𝘰','p':'𝘱','q':'𝘲','r':'𝘳','s':'𝘴','t':'𝘵','u':'𝘶',
        'v':'𝘷','w':'𝘸','x':'𝘹','y':'𝘺','z':'𝘻'
    }
    return ''.join(m.get(c, c) for c in t)

def smallcaps_unicode(t):
    m = {
        'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ғ','g':'ɢ',
        'h':'ʜ','i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ',
        'o':'ᴏ','p':'ᴘ','q':'ǫ','r':'ʀ','s':'s','t':'ᴛ','u':'ᴜ',
        'v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ'
    }
    return ''.join(m.get(c.lower(), c) for c in t)


# ==========================================
# 19. ENGLISH CAPTION GENERATOR
# ==========================================
def generate_caption(hook, image_text):
    fact   = random.choice(FACTS_EN)
    tip    = random.choice(TIPS_EN)
    review = random.choice(REVIEWS_EN)
    body   = random.choice([fact, tip, review])

    words  = ["Web Dev", "React JS", "Python", "API", "Tech", "Flutter", "Node JS"]
    styled = random.choice([bold_unicode, italic_unicode, smallcaps_unicode])(
        random.choice(words)
    )

    fixed    = random.sample(FIXED_HASHTAGS, 4)
    trending = fetch_trending_tags()
    extra    = random.sample(TRENDING_TAGS, 3)
    tags     = " ".join(fixed + trending + extra)

    d = "━" * 32
    return (
        f"{d}\n"
        f"{hook}\n"
        f"🔥 {image_text}\n"
        f"{d}\n\n"
        f"💡 {body}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💼 {bold_unicode('Service')}: {styled}\n"
        f"📧 {italic_unicode('Email')}: rahulhaku52@gmail.com\n"
        f"📱 {italic_unicode('Telegram')}: t.me/hacker_52\n"
        f"🌐 {smallcaps_unicode('Follow Us')} for daily tips!\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{tags}"
    )


# ==========================================
# 20. FACEBOOK UPLOAD
# ==========================================
def upload_to_facebook(video_path, title, description):
    if not PAGE_ID or not ACCESS_TOKEN:
        print("❌ Facebook credentials missing!")
        return {"error": "Missing credentials"}
    try:
        with open(video_path, 'rb') as vf:
            resp = requests.post(
                f"https://graph.facebook.com/{PAGE_ID}/videos",
                files={'source': vf},
                data={
                    'access_token': ACCESS_TOKEN,
                    'title': title[:100],
                    'description': description[:2000],
                    'published': True
                },
                timeout=180
            )
        result = resp.json()
        if 'id' in result:
            print(f"✅ Uploaded! ID: {result['id']}")
        else:
            print(f"⚠️ Upload: {result}")
        return result
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return {"error": str(e)}


# ==========================================
# 21. MAIN
# ==========================================
def main():
    print("=" * 55)
    print(f"🚀 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Pixabay : {'✅' if PIXABAY_API_KEY  else '❌'}")
    print(f"🔑 Pexels  : {'✅' if PEXELS_API_KEY   else '❌'}")
    print(f"🔑 Unsplash: {'✅' if UNSPLASH_API_KEY  else '❌'}")
    print(f"🔑 Facebook: {'✅' if PAGE_ID and ACCESS_TOKEN else '❌'}")
    print(f"🖼️  Logo    : {'✅' if os.path.exists(LOGO_PATH) else '⚠️'}")
    print(f"⏱️  Duration: {MIN_DURATION}~{MAX_DURATION}s")
    print("=" * 55)

    img_path = voice_path = video_path = None

    try:
        # ✅ 1. English hook + image text
        hook       = random.choice(HOOKS)
        image_text = random.choice(IMAGE_TEXTS)

        # ✅ 2. Voice text (Bengali/Hindi/English rotation)
        voice_text, lang = pick_voice_text()

        print(f"🎣 Hook      : {hook}")
        print(f"🖼️  Image text: {image_text}")
        print(f"🎙️  Voice lang: {lang}")
        print(f"📢 Voice text: {voice_text[:60]}...")

        # 3. Generate image (English text)
        img_path = generate_image(image_text, hook)

        # 4. Generate voice (Bengali/Hindi/English)
        voice_path, voice_id = generate_voice(voice_text)
        print(f"🎙️  Voice ID: {voice_id}")

        # 5. Create video (English subtitle)
        video_path = create_video(img_path, voice_path, image_text)

        # 6. English caption
        caption = generate_caption(hook, image_text)
        print(f"\n📋 Caption:\n{caption[:300]}...\n")

        # 7. Upload
        print("📤 Uploading...")
        result = upload_to_facebook(
            video_path,
            f"{hook} — {image_text}",
            caption
        )
        print(f"📊 Result: {result}")

    except Exception as e:
        print(f"❌ Fatal: {e}")
        import traceback
        traceback.print_exc()

    finally:
        for label, path in [
            ("image", img_path),
            ("voice", voice_path),
            ("video", video_path)
        ]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                    print(f"🧹 {label} cleaned")
                except Exception:
                    pass

    print("=" * 55)
    print(f"✅ Done: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)


if __name__ == "__main__":
    main()
