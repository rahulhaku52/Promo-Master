import os
import io
import requests
import random
import tempfile
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from gtts import gTTS
from moviepy.editor import (
    ImageClip, AudioFileClip, VideoFileClip,
    CompositeVideoClip, TextClip, concatenate_videoclips
)

# ==========================================
# ১. কনফিগারেশন (API Keys)
# ==========================================
PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID')
ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN')
PIXABAY_API_KEY = os.environ.get('PIXABAY_API_KEY')        # PRIMARY ✅
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')          # BACKUP 1 ✅
UNSPLASH_API_KEY = os.environ.get('UNSPLASH_API_KEY')      # BACKUP 2 ✅

# ==========================================
# ২. ভ্যারিয়েবল লাইব্রেরি
# ==========================================

TITLE_TEMPLATES = [
    "আপনি কি জানেন? {fact}",
    "{tip} — মাত্র ৩০ সেকেন্ডে শিখুন",
    "ক্লায়েন্ট বললো: {review}",
    "🚀 {fact} — এখনই শুরু করুন",
    "💡 {tip} — প্রো টিপস",
    "📱 {fact} — শর্টস ভার্সন"
]

FACTS = [
    "ওয়েবসাইটের লোড টাইম ৩ সেকেন্ডের বেশি হলে ৫০% ভিজিটর চলে যায়",
    "মোবাইল ফ্রেন্ডলি ওয়েবসাইট Google-এ বেশি র‍্যাঙ্ক পায়",
    "React JS ২০২৬-এ সবচেয়ে ডিমান্ডেড স্কিল",
    "Python দিয়ে ১০ মিনিটেই ওয়েব অ্যাপ বানানো যায়",
    "API ইন্টিগ্রেশন ছাড়া আধুনিক অ্যাপ অসম্পূর্ণ",
    "Flutter দিয়ে Android ও iOS দুটো অ্যাপ একসাথে বানানো যায়",
    "SEO ছাড়া ওয়েবসাইট থাকা মানে অন্ধকারে থাকা"
]

TIPS = [
    "CSS গ্রিড দিয়ে লেআউট ডিজাইন করুন",
    "JavaScript-এ async/await ব্যবহার করুন",
    "Git দিয়ে কোড ভার্সন কন্ট্রোল করুন",
    "VS Code-এ শর্টকাট শিখুন",
    "Docker দিয়ে প্রজেক্ট ডেপ্লয় করুন সহজে",
    "TypeScript শিখলে বড় প্রজেক্টে সুবিধা পাবেন"
]

REVIEWS = [
    "আমার ওয়েবসাইট ২ দিনে তৈরি করে দিয়েছে!",
    "অ্যাপটা ফাস্ট আর ইউজার ফ্রেন্ডলি",
    "ডিজাইনটা ছিল আমার স্বপ্নের মতো",
    "প্রফেশনাল কাজ, সময়মতো ডেলিভারি!",
    "দামে কম, মানে সেরা — সত্যিই অসাধারণ!"
]

DESC_TEMPLATES = [
    "💻 {title}\n\n{body}\n\n📩 যোগাযোগ: t.me/hacker_52\n🔗 আরও টিপসের জন্য ফলো করুন!",
    "🔥 {title}\n\n{body}\n\n📱 আমাদের সাথে থাকুন: t.me/hacker_52",
    "✨ {title}\n\n{body}\n\n🤝 স্মার্ট ওয়েব সলিউশনের জন্য @hacker_52",
    "⚡ {title}\n\n{body}\n\n💡 আপনার প্রজেক্টের কথা বলুন: t.me/hacker_52",
    "🎯 {title}\n\n{body}\n\n📌 শেয়ার করুন আর লাইক দিন!"
]

FIXED_HASHTAGS = [
    "#webdevelopment", "#appdevelopment", "#shorts",
    "#codingtips", "#programming", "#tech"
]

TRENDING_TAGS = [
    "#webdesign", "#developer", "#coder", "#frontend",
    "#backend", "#fullstack", "#reactjs", "#python",
    "#javascript", "#nodejs", "#flutter", "#android",
    "#ios", "#uiux", "#startup", "#entrepreneur",
    "#digitalmarketing", "#seo", "#wordpress", "#laravel"
]

LANGUAGES = ['bn', 'en', 'hi']

TEXT_POSITIONS = [
    ('center', 'bottom'),
    ('center', 'top'),
    ('left', 'bottom'),
    ('right', 'bottom'),
    ('center', 'center')
]

PIXABAY_THEMES = [
    "technology", "coding", "computer", "web design",
    "programming", "laptop", "digital", "startup",
    "developer", "software", "internet", "network"
]

UNSPLASH_THEMES = [
    "technology", "coding", "developer", "web design",
    "laptop", "programming", "startup", "digital"
]

# ==========================================
# ৩. COLOR THEMES (Professional Gradients)
# ==========================================
COLOR_THEMES = [
    {
        "name": "Deep Ocean",
        "color1": (5, 10, 48),
        "color2": (0, 80, 180),
        "accent": (0, 200, 255),
        "text": (255, 255, 255),
        "highlight": (0, 230, 255)
    },
    {
        "name": "Sunset Fire",
        "color1": (40, 5, 5),
        "color2": (180, 60, 0),
        "accent": (255, 150, 0),
        "text": (255, 255, 255),
        "highlight": (255, 200, 50)
    },
    {
        "name": "Purple Galaxy",
        "color1": (15, 5, 40),
        "color2": (80, 0, 150),
        "accent": (180, 0, 255),
        "text": (255, 255, 255),
        "highlight": (220, 150, 255)
    },
    {
        "name": "Forest Dark",
        "color1": (5, 25, 15),
        "color2": (0, 80, 50),
        "accent": (0, 200, 100),
        "text": (255, 255, 255),
        "highlight": (100, 255, 180)
    },
    {
        "name": "Steel Blue",
        "color1": (10, 20, 35),
        "color2": (30, 60, 120),
        "accent": (80, 160, 255),
        "text": (255, 255, 255),
        "highlight": (150, 220, 255)
    },
    {
        "name": "Neon Dark",
        "color1": (5, 5, 5),
        "color2": (20, 20, 40),
        "accent": (255, 0, 150),
        "text": (255, 255, 255),
        "highlight": (0, 255, 200)
    }
]

# ==========================================
# ৪. ট্রেন্ডিং হ্যাশট্যাগ (Pixabay থেকে PRIMARY)
# ==========================================
def fetch_trending_tags():
    """Pixabay → Pexels → Fallback ক্রমে ট্রেন্ডিং ট্যাগ আনে"""
    
    # PRIMARY: Pixabay
    if PIXABAY_API_KEY:
        try:
            query = random.choice(PIXABAY_THEMES)
            url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&per_page=5&category=technology"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                hits = data.get('hits', [])
                tags = []
                for hit in hits[:3]:
                    raw_tags = hit.get('tags', '').split(',')
                    for tag in raw_tags[:1]:
                        clean = tag.strip().replace(' ', '')
                        if clean and len(clean) > 2:
                            tags.append(f"#{clean}")
                if tags:
                    print("✅ Tags from Pixabay")
                    return tags[:2]
        except Exception as e:
            print(f"⚠️ Pixabay tags error: {e}")
    
    # BACKUP: Pexels
    if PEXELS_API_KEY:
        try:
            url = "https://api.pexels.com/v1/popular?per_page=5"
            headers = {"Authorization": PEXELS_API_KEY}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                tags = []
                for photo in data.get('photos', [])[:2]:
                    alt = photo.get('alt', '').replace(' ', '')
                    if alt:
                        tags.append(f"#{alt[:15]}")
                if tags:
                    print("✅ Tags from Pexels")
                    return tags
        except Exception as e:
            print(f"⚠️ Pexels tags error: {e}")
    
    # FALLBACK
    print("✅ Tags from local pool")
    return random.sample(TRENDING_TAGS, 2)

# ==========================================
# ৫. FONT HELPER (সুন্দর ফন্ট লোড করে)
# ==========================================
def load_fonts():
    """সিস্টেম থেকে সেরা ফন্ট খোঁজে"""
    font_paths = {
        'bold': [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        ],
        'regular': [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        ],
        'italic': [
            "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-BI.ttf",
        ]
    }
    
    loaded = {}
    for style, paths in font_paths.items():
        for path in paths:
            if os.path.exists(path):
                loaded[style] = path
                break
        if style not in loaded:
            loaded[style] = None  # ডিফল্ট
    
    return loaded

# ==========================================
# ৬. PROFESSIONAL IMAGE GENERATOR
# ==========================================
def draw_rounded_rectangle(draw, xy, radius, fill, outline=None, outline_width=2):
    """Rounded Rectangle আঁকে (সুন্দর কার্ড স্টাইল)"""
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
    draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
    draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
    draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)
    if outline:
        draw.arc([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=outline, width=outline_width)
        draw.arc([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=outline, width=outline_width)
        draw.arc([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=outline, width=outline_width)
        draw.arc([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=outline, width=outline_width)

def generate_image_from_pixabay(text, theme):
    """PRIMARY: Pixabay থেকে ইমেজ আনে"""
    if not PIXABAY_API_KEY:
        return None
    try:
        url = (
            f"https://pixabay.com/api/?key={PIXABAY_API_KEY}"
            f"&q={theme}&image_type=photo&category=technology"
            f"&orientation=horizontal&per_page=10&safesearch=true"
            f"&min_width=1200&min_height=628"
        )
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            hits = resp.json().get('hits', [])
            if hits:
                chosen = random.choice(hits[:5])
                img_url = chosen.get('webformatURL') or chosen.get('largeImageURL')
                img_resp = requests.get(img_url, timeout=20)
                if img_resp.status_code == 200:
                    img = Image.open(io.BytesIO(img_resp.content)).convert('RGB')
                    img = img.resize((1200, 628), Image.LANCZOS)
                    print(f"✅ Pixabay image: {chosen.get('tags', '')[:30]}")
                    return img
    except Exception as e:
        print(f"⚠️ Pixabay image error: {e}")
    return None

def generate_image_from_pexels(text, theme):
    """BACKUP 1: Pexels থেকে ইমেজ আনে"""
    if not PEXELS_API_KEY:
        return None
    try:
        url = f"https://api.pexels.com/v1/search?query={theme}&per_page=10&orientation=landscape"
        headers = {"Authorization": PEXELS_API_KEY}
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            photos = resp.json().get('photos', [])
            if photos:
                chosen = random.choice(photos[:5])
                img_url = chosen['src']['large']
                img_resp = requests.get(img_url, timeout=20)
                if img_resp.status_code == 200:
                    img = Image.open(io.BytesIO(img_resp.content)).convert('RGB')
                    img = img.resize((1200, 628), Image.LANCZOS)
                    print("✅ Pexels image fetched")
                    return img
    except Exception as e:
        print(f"⚠️ Pexels image error: {e}")
    return None

def generate_image_from_unsplash(text, theme):
    """BACKUP 2: Unsplash থেকে ইমেজ আনে"""
    if not UNSPLASH_API_KEY:
        return None
    try:
        url = f"https://api.unsplash.com/photos/random?query={theme}&orientation=landscape&count=1"
        headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data:
                img_url = data[0]['urls']['regular']
                img_resp = requests.get(img_url, timeout=20)
                if img_resp.status_code == 200:
                    img = Image.open(io.BytesIO(img_resp.content)).convert('RGB')
                    img = img.resize((1200, 628), Image.LANCZOS)
                    print("✅ Unsplash image fetched")
                    return img
    except Exception as e:
        print(f"⚠️ Unsplash image error: {e}")
    return None

def create_gradient_background(theme_colors, width=1200, height=628):
    """FALLBACK: প্রফেশনাল গ্রেডিয়েন্ট ব্যাকগ্রাউন্ড"""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    c1 = theme_colors['color1']
    c2 = theme_colors['color2']
    accent = theme_colors['accent']
    
    # মেইন গ্রেডিয়েন্ট (টপ টু বটম)
    for y in range(height):
        t = y / height
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # ডায়াগোনাল অ্যাকসেন্ট (রাইট সাইড গ্লো)
    for x in range(width // 2, width):
        t = (x - width // 2) / (width // 2)
        alpha = int(30 * t)
        r = min(255, c2[0] + int((accent[0] - c2[0]) * t))
        g = min(255, c2[1] + int((accent[1] - c2[1]) * t))
        b = min(255, c2[2] + int((accent[2] - c2[2]) * t))
        for y in range(height):
            dy = abs(y - height // 2) / (height // 2)
            fade = max(0, int(alpha * (1 - dy)))
            if fade > 5:
                cur_color = img.getpixel((x, y))
                blended = (
                    min(255, cur_color[0] + fade),
                    min(255, cur_color[1] + fade // 3),
                    min(255, cur_color[2] + fade // 2)
                )
                img.putpixel((x, y), blended)
    
    # সার্কেল ডেকোরেশন (ব্যাকগ্রাউন্ড বুকে)
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    
    # বড় সার্কেল (রাইট টপ)
    ov_draw.ellipse(
        [width - 350, -150, width + 100, 350],
        fill=(*accent, 25)
    )
    # ছোট সার্কেল (লেফট বটম)
    ov_draw.ellipse(
        [-100, height - 300, 250, height + 50],
        fill=(*accent, 20)
    )
    # মিডিয়াম সার্কেল (সেন্টার)
    ov_draw.ellipse(
        [width // 2 - 200, height // 2 - 200, width // 2 + 200, height // 2 + 200],
        fill=(*accent, 10)
    )
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    # গ্রিড লাইন (সাটল)
    draw = ImageDraw.Draw(img)
    for x in range(0, width, 80):
        draw.line([(x, 0), (x, height)], fill=(*accent, 8), width=1)
    for y in range(0, height, 80):
        draw.line([(0, y), (width, y)], fill=(*accent, 8), width=1)
    
    print("✅ Gradient background created")
    return img

def add_professional_overlay(img, theme_colors):
    """ইমেজে প্রফেশনাল ডার্ক ওভারলে + ডেকোরেশন যোগ"""
    width, height = img.size
    
    # ডার্ক গ্রেডিয়েন্ট ওভারলে (নিচের দিকে বেশি)
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    
    for y in range(height):
        t = y / height
        alpha = int(80 + 100 * t)  # নিচে বেশি অন্ধকার
        ov_draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
    
    # লেফট সাইড গ্রেডিয়েন্ট (টেক্সট রিডেবিলিটির জন্য)
    for x in range(width // 2):
        t = 1 - (x / (width // 2))
        alpha = int(60 * t)
        for y in range(height):
            ov_draw.point((x, y), fill=(0, 0, 0, alpha))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    # অ্যাকসেন্ট লাইন (টপ ও বটম)
    draw = ImageDraw.Draw(img)
    accent = theme_colors['accent']
    draw.rectangle([(0, 0), (width, 5)], fill=accent)
    draw.rectangle([(0, height - 5), (width, height)], fill=accent)
    
    return img

def add_stylish_text(img, text, theme_colors, font_paths, layout='card'):
    """সুন্দর ফন্ট ও লেআউট দিয়ে টেক্সট যোগ"""
    draw = ImageDraw.Draw(img)
    width, height = img.size
    accent = theme_colors['accent']
    highlight = theme_colors['highlight']
    
    # ফন্ট লোড
    try:
        if font_paths.get('bold'):
            font_huge = ImageFont.truetype(font_paths['bold'], 62)
            font_large = ImageFont.truetype(font_paths['bold'], 46)
            font_medium = ImageFont.truetype(font_paths['bold'], 34)
            font_small = ImageFont.truetype(font_paths.get('regular', font_paths['bold']), 26)
            font_tiny = ImageFont.truetype(font_paths.get('regular', font_paths['bold']), 22)
        else:
            font_huge = font_large = font_medium = font_small = font_tiny = ImageFont.load_default()
    except:
        font_huge = font_large = font_medium = font_small = font_tiny = ImageFont.load_default()
    
    # লেআউট সিলেক্ট
    if layout == 'card':
        _draw_card_layout(draw, img, text, theme_colors, 
                         font_huge, font_large, font_medium, font_small, font_tiny,
                         width, height, accent, highlight)
    elif layout == 'split':
        _draw_split_layout(draw, img, text, theme_colors,
                          font_huge, font_large, font_medium, font_small, font_tiny,
                          width, height, accent, highlight)
    elif layout == 'minimal':
        _draw_minimal_layout(draw, img, text, theme_colors,
                            font_huge, font_large, font_medium, font_small, font_tiny,
                            width, height, accent, highlight)
    elif layout == 'bold_center':
        _draw_bold_center_layout(draw, img, text, theme_colors,
                                font_huge, font_large, font_medium, font_small, font_tiny,
                                width, height, accent, highlight)
    
    return img

def _wrap_text(text, font, max_width, draw):
    """টেক্সট র‍্যাপ করে (লম্বা টেক্সটকে মাল্টি-লাইনে)"""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        try:
            w = draw.textlength(test, font=font)
        except:
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

def _draw_card_layout(draw, img, text, theme_colors, 
                      font_huge, font_large, font_medium, font_small, font_tiny,
                      width, height, accent, highlight):
    """কার্ড স্টাইল লেআউট — সবচেয়ে প্রফেশনাল"""
    
    # সেমি-ট্রান্সপারেন্ট কার্ড (বাম দিকে)
    card_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_overlay)
    
    card_x1, card_y1 = 50, 80
    card_x2, card_y2 = 780, height - 80
    card_draw.rectangle([card_x1, card_y1, card_x2, card_y2], fill=(0, 0, 0, 140))
    
    # কার্ড বর্ডার (অ্যাকসেন্ট)
    card_draw.rectangle([card_x1, card_y1, card_x2, card_y1 + 4], fill=(*accent, 230))
    card_draw.rectangle([card_x1, card_y1, card_x1 + 4, card_y2], fill=(*accent, 180))
    
    img_with_card = Image.alpha_composite(img.convert('RGBA'), card_overlay).convert('RGB')
    img.paste(img_with_card)
    draw = ImageDraw.Draw(img)
    
    # ট্যাগ (WEB DEV / TECH)
    tag_text = "⚡ TECH TIPS"
    tag_x, tag_y = 80, 110
    try:
        tag_w = draw.textlength(tag_text, font=font_tiny)
    except:
        tag_w = 120
    draw.rectangle([tag_x - 10, tag_y - 5, tag_x + tag_w + 10, tag_y + 30], fill=accent)
    draw.text((tag_x, tag_y), tag_text, fill=(0, 0, 0), font=font_tiny)
    
    # শ্যাডো + মেইন টেক্সট
    lines = _wrap_text(text, font_large, 680, draw)
    y_pos = 165
    for i, line in enumerate(lines[:4]):
        # শ্যাডো
        draw.text((82, y_pos + 2), line, fill=(0, 0, 0, 150), font=font_large)
        # হাইলাইট (প্রথম লাইন)
        color = highlight if i == 0 else (255, 255, 255)
        draw.text((80, y_pos), line, fill=color, font=font_large)
        y_pos += 58
    
    # ডিভাইডার লাইন
    div_y = y_pos + 15
    draw.rectangle([(80, div_y), (80 + 200, div_y + 3)], fill=accent)
    draw.rectangle([(80 + 210, div_y + 1), (80 + 400, div_y + 2)], fill=(*accent, 100))
    
    # সাবটাইটেল
    sub_text = "🔗 t.me/hacker_52 | ফলো করুন"
    draw.text((80, div_y + 20), sub_text, fill=(*accent[:3],), font=font_small)
    
    # ব্র্যান্ড লোগো (বটম রাইট কার্ড)
    brand = "@hacker_52"
    try:
        brand_w = draw.textlength(brand, font=font_medium)
    except:
        brand_w = 180
    bx = card_x2 - brand_w - 20
    by = card_y2 - 55
    draw.rectangle([bx - 12, by - 8, card_x2 - 10, by + 42], fill=accent)
    draw.text((bx, by), brand, fill=(0, 0, 0), font=font_medium)
    
    # নম্বর/তারিখ (কর্নার)
    date_str = datetime.now().strftime("%d %b %Y")
    draw.text((card_x1 + 10, card_y2 - 35), date_str, fill=(*accent[:3], 150), font=font_tiny)

def _draw_split_layout(draw, img, text, theme_colors,
                       font_huge, font_large, font_medium, font_small, font_tiny,
                       width, height, accent, highlight):
    """স্প্লিট লেআউট — বাম-ডান বিভাজন"""
    
    # বাম সাইড ডার্ক
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rectangle([0, 0, width // 2 - 20, height], fill=(0, 0, 0, 170))
    img_new = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    img.paste(img_new)
    draw = ImageDraw.Draw(img)
    
    # ভার্টিকাল ডিভাইডার
    draw.rectangle([(width // 2 - 8, 0), (width // 2 - 4, height)], fill=accent)
    draw.rectangle([(width // 2 - 22, 0), (width // 2 - 20, height)], fill=(*accent[:3], 80))
    
    # লেফট: TITLE + TEXT
    title_lines = _wrap_text(text, font_large, width // 2 - 80, draw)
    y_pos = 120
    
    # বড় নম্বর (ব্যাকগ্রাউন্ড)
    draw.text((30, 60), "01", fill=(*accent[:3], 25), font=font_huge)
    
    for i, line in enumerate(title_lines[:3]):
        color = highlight if i == 0 else (255, 255, 255)
        # শ্যাডো
        draw.text((62, y_pos + 2), line, fill=(0, 0, 0), font=font_large)
        draw.text((60, y_pos), line, fill=color, font=font_large)
        y_pos += 60
    
    # অ্যাকসেন্ট আন্ডারলাইন
    draw.rectangle([(60, y_pos + 10), (60 + 150, y_pos + 14)], fill=accent)
    
    # ব্র্যান্ড
    draw.text((60, height - 100), "💡 @hacker_52", fill=highlight, font=font_medium)
    draw.text((60, height - 65), "t.me/hacker_52", fill=(*accent[:3],), font=font_small)
    
    # রাইট: ডেকোরেশন + ইকন
    cx = width * 3 // 4
    cy = height // 2
    
    # বড় আইকন বক্স
    draw.rectangle(
        [cx - 100, cy - 100, cx + 100, cy + 100],
        outline=(*accent[:3], 80), width=2
    )
    draw.rectangle(
        [cx - 85, cy - 85, cx + 85, cy + 85],
        outline=(*accent[:3], 40), width=1
    )
    
    # ইমোজি/আইকন সেন্টার
    tech_icons = ["⚡", "🚀", "💻", "🔥", "✨", "🎯"]
    icon = random.choice(tech_icons)
    draw.text((cx - 45, cy - 55), icon, fill=(255, 255, 255), font=font_huge)
    
    # ছোট ডট ডেকোরেশন
    for i in range(4):
        for j in range(4):
            dx = cx - 150 + i * 30
            dy = cy + 130 + j * 20
            draw.ellipse([dx, dy, dx + 6, dy + 6], fill=(*accent[:3], 80))

def _draw_minimal_layout(draw, img, text, theme_colors,
                         font_huge, font_large, font_medium, font_small, font_tiny,
                         width, height, accent, highlight):
    """মিনিমাল ক্লিন লেআউট"""
    
    # বটম বড় ডার্ক এরিয়া
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rectangle([0, height // 2, width, height], fill=(0, 0, 0, 200))
    # ফেড ট্রানজিশন
    for y in range(height // 3):
        alpha = int(200 * (y / (height // 3)))
        ov_draw.line([(0, height // 2 - y), (width, height // 2 - y)], fill=(0, 0, 0, alpha))
    
    img_new = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    img.paste(img_new)
    draw = ImageDraw.Draw(img)
    
    # টপ বর্ডার
    draw.rectangle([(0, 0), (width, 6)], fill=accent)
    
    # টপ লেফট ব্র্যান্ড
    draw.text((40, 25), "⚡ hacker_52", fill=(255, 255, 255), font=font_small)
    
    # বটম টেক্সট
    lines = _wrap_text(text, font_large, width - 100, draw)
    total_h = len(lines[:3]) * 60
    y_pos = height - total_h - 100
    
    for i, line in enumerate(lines[:3]):
        color = highlight if i == 0 else (230, 230, 230)
        # শ্যাডো
        draw.text((52, y_pos + 3), line, fill=(0, 0, 0), font=font_large)
        draw.text((50, y_pos), line, fill=color, font=font_large)
        y_pos += 62
    
    # বটম বর্ডার + লিংক
    draw.rectangle([(0, height - 6), (width, height)], fill=accent)
    link_text = "📱 t.me/hacker_52 | #webdev #tech #coding"
    try:
        link_w = draw.textlength(link_text, font=font_tiny)
    except:
        link_w = 400
    draw.text(((width - link_w) // 2, height - 35), link_text, fill=(200, 200, 200), font=font_tiny)

def _draw_bold_center_layout(draw, img, text, theme_colors,
                             font_huge, font_large, font_medium, font_small, font_tiny,
                             width, height, accent, highlight):
    """বোল্ড সেন্টার লেআউট — ইম্প্যাক্টফুল"""
    
    # ফুল ওভারলে
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 160))
    img_new = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    img.paste(img_new)
    draw = ImageDraw.Draw(img)
    
    # কর্নার ডেকোরেশন
    size = 40
    # টপ লেফট
    draw.rectangle([(20, 20), (20 + size, 20 + 5)], fill=accent)
    draw.rectangle([(20, 20), (20 + 5, 20 + size)], fill=accent)
    # টপ রাইট
    draw.rectangle([(width - 20 - size, 20), (width - 20, 20 + 5)], fill=accent)
    draw.rectangle([(width - 25, 20), (width - 20, 20 + size)], fill=accent)
    # বটম লেফট
    draw.rectangle([(20, height - 25), (20 + size, height - 20)], fill=accent)
    draw.rectangle([(20, height - 20 - size), (20 + 5, height - 20)], fill=accent)
    # বটম রাইট
    draw.rectangle([(width - 20 - size, height - 25), (width - 20, height - 20)], fill=accent)
    draw.rectangle([(width - 25, height - 20 - size), (width - 20, height - 20)], fill=accent)
    
    # ইমোজি আইকন (টপ)
    icons = ["🚀", "💡", "⚡", "🎯", "🔥", "✨"]
    icon = random.choice(icons)
    try:
        icon_w = draw.textlength(icon, font=font_huge)
    except:
        icon_w = 60
    draw.text(((width - icon_w) // 2, 60), icon, fill=(255, 255, 255), font=font_huge)
    
    # টপ লাইন
    draw.rectangle([(width // 2 - 100, 140), (width // 2 + 100, 144)], fill=accent)
    
    # সেন্টার মেইন টেক্সট
    lines = _wrap_text(text, font_large, width - 160, draw)
    total_h = len(lines[:4]) * 62
    y_pos = (height - total_h) // 2 - 20
    
    for i, line in enumerate(lines[:4]):
        try:
            line_w = draw.textlength(line, font=font_large)
        except:
            line_w = len(line) * 25
        x_pos = (width - line_w) // 2
        color = highlight if i == 0 else (255, 255, 255)
        # শ্যাডো
        draw.text((x_pos + 3, y_pos + 3), line, fill=(0, 0, 0), font=font_large)
        draw.text((x_pos, y_pos), line, fill=color, font=font_large)
        y_pos += 62
    
    # বটম লাইন + ব্র্যান্ড
    draw.rectangle([(width // 2 - 100, y_pos + 20), (width // 2 + 100, y_pos + 24)], fill=accent)
    
    brand = "@hacker_52 | t.me/hacker_52"
    try:
        brand_w = draw.textlength(brand, font=font_small)
    except:
        brand_w = 300
    draw.text(((width - brand_w) // 2, height - 80), brand, fill=highlight, font=font_small)

def generate_image(text, style='auto'):
    """মেইন ইমেজ জেনারেটর: Pixabay→Pexels→Unsplash→Gradient"""
    
    width, height = 1200, 628
    theme = random.choice(COLOR_THEMES)
    font_paths = load_fonts()
    img_source = None
    
    # থিম কোয়েরি
    query = random.choice(PIXABAY_THEMES)
    
    if style == 'auto':
        # স্বয়ংক্রিয়ভাবে সোর্স সিলেক্ট (Pixabay PRIMARY)
        style_choice = random.choices(
            ['photo', 'photo', 'photo', 'gradient'],
            weights=[50, 30, 20, 20]
        )[0]
    else:
        style_choice = style
    
    # ফটো আনার চেষ্টা
    if style_choice == 'photo' or style_choice == 'pixabay':
        img_source = generate_image_from_pixabay(text, query)
    
    if img_source is None and PEXELS_API_KEY:
        img_source = generate_image_from_pexels(text, query)
    
    if img_source is None and UNSPLASH_API_KEY:
        img_source = generate_image_from_unsplash(text, query)
    
    # সম্পূর্ণ গ্রেডিয়েন্ট ফলব্যাক
    if img_source is None:
        img_source = create_gradient_background(theme, width, height)
    else:
        # ফটোতে প্রফেশনাল ওভারলে যোগ
        img_source = add_professional_overlay(img_source, theme)
    
    # লেআউট সিলেক্ট
    layouts = ['card', 'split', 'minimal', 'bold_center']
    layout = random.choice(layouts)
    print(f"✅ Layout: {layout} | Theme: {theme['name']}")
    
    # টেক্সট যোগ
    final_img = add_stylish_text(img_source, text, theme, font_paths, layout=layout)
    
    # সেভ
    temp_img = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    final_img.save(temp_img.name, quality=95)
    return temp_img.name

# ==========================================
# ৭. ভয়েস জেনারেট (মাল্টি-ল্যাঙ্গুয়েজ)
# ==========================================
def generate_voice(text, lang=None):
    """gTTS দিয়ে ভয়েস বানায়"""
    if lang is None:
        lang = random.choice(LANGUAGES)
    
    temp_audio = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
    
    try:
        tts = gTTS(
            text=text,
            lang=lang,
            slow=random.choice([True, False])
        )
        tts.save(temp_audio.name)
        print(f"✅ Voice generated (lang: {lang})")
    except Exception as e:
        print(f"⚠️ Voice error: {e}")
        # ফলব্যাক: ইংরেজি
        tts = gTTS(text=text[:200], lang='en', slow=False)
        tts.save(temp_audio.name)
    
    return temp_audio.name, lang

# ==========================================
# ৮. ভিডিও তৈরি (প্রফেশনাল)
# ==========================================
def create_video(image_path, voice_path, text, logo_text="⚡ @hacker_52", duration=15):
    """ইমেজ + অডিও → প্রফেশনাল ভিডিও"""
    output_path = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
    
    try:
        # ইমেজ ক্লিপ
        img_clip = ImageClip(image_path, duration=duration)
        
        # ভয়েস
        audio_clip = AudioFileClip(voice_path)
        actual_duration = min(duration, audio_clip.duration + 2)
        img_clip = img_clip.set_duration(actual_duration)
        
        # অডিও সেট
        final_clip = img_clip.set_audio(audio_clip)
        
        # টেক্সট ওভারলে (সাবটাইটেল স্টাইল)
        short_text = text[:80] + "..." if len(text) > 80 else text
        
        # মেইন সাবটাইটেল (শুধু প্রথম ৮ সেকেন্ড)
        subtitle_clip = TextClip(
            short_text,
            fontsize=28,
            color='white',
            stroke_color='black',
            stroke_width=1.5,
            method='caption',
            size=(900, None),
            align='center'
        ).set_position(('center', 'bottom')).set_duration(min(8, actual_duration)).set_opacity(0.9)
        
        # লোগো (শেষ ৩ সেকেন্ড)
        logo_clip = TextClip(
            logo_text,
            fontsize=42,
            color='yellow',
            stroke_color='black',
            stroke_width=2,
            method='label'
        )
        logo_pos = random.choice([
            ('center', 'bottom'),
            ('right', 'bottom'),
        ])
        logo_clip = (logo_clip
                    .set_position(logo_pos)
                    .set_duration(3)
                    .set_start(actual_duration - 3)
                    .set_opacity(0.95))
        
        # কম্পোজিট
        final = CompositeVideoClip([final_clip, subtitle_clip, logo_clip])
        
        # রেন্ডার
        final.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None,
            preset='fast'
        )
        print(f"✅ Video created: {output_path}")
        
    except Exception as e:
        print(f"⚠️ Video error: {e}")
        # সিম্পল ফলব্যাক
        img_clip = ImageClip(image_path, duration=12)
        img_clip.write_videofile(output_path, fps=24, verbose=False, logger=None)
    
    return output_path

# ==========================================
# ৯. ফেসবুক আপলোড
# ==========================================
def upload_to_facebook(video_path, title, description):
    """Facebook Graph API-তে ভিডিও আপলোড"""
    if not PAGE_ID or not ACCESS_TOKEN:
        print("❌ Facebook credentials missing!")
        return {"error": "Missing credentials"}
    
    url = f"https://graph.facebook.com/{PAGE_ID}/videos"
    
    try:
        with open(video_path, 'rb') as video_file:
            files = {'source': video_file}
            data = {
                'access_token': ACCESS_TOKEN,
                'title': title[:100],
                'description': description[:2000],
                'published': True
            }
            resp = requests.post(url, files=files, data=data, timeout=120)
            result = resp.json()
            
            if 'id' in result:
                print(f"✅ Video uploaded! ID: {result['id']}")
            else:
                print(f"⚠️ Upload response: {result}")
            
            return result
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return {"error": str(e)}

# ==========================================
# ১০. স্টাইলিশ ক্যাপশন জেনারেটর
# ==========================================
def stylish_unicode(text):
    """ইউনিকোড স্মল ক্যাপস স্টাইল"""
    caps = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ',
        'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
        'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ',
        'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ',
        'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ',
        'z': 'ᴢ'
    }
    return ''.join(caps.get(c.lower(), c) for c in text)

def bold_unicode(text):
    """বোল্ড ইউনিকোড (Mathematical Bold)"""
    bold = {
        'a': '𝗮', 'b': '𝗯', 'c': '𝗰', 'd': '𝗱', 'e': '𝗲',
        'f': '𝗳', 'g': '𝗴', 'h': '𝗵', 'i': '𝗶', 'j': '𝗷',
        'k': '𝗸', 'l': '𝗹', 'm': '𝗺', 'n': '𝗻', 'o': '𝗼',
        'p': '𝗽', 'q': '𝗾', 'r': '𝗿', 's': '𝘀', 't': '𝘁',
        'u': '𝘂', 'v': '𝘃', 'w': '𝘄', 'x': '𝘅', 'y': '𝘆',
        'z': '𝘇',
        'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘',
        'F': '𝗙', 'G': '𝗚', 'H': '𝗛', 'I': '𝗜', 'J': '𝗝',
        'K': '𝗞', 'L': '𝗟', 'M': '𝗠', 'N': '𝗡', 'O': '𝗢',
        'P': '𝗣', 'Q': '𝗤', 'R': '𝗥', 'S': '𝗦', 'T': '𝗧',
        'U': '𝗨', 'V': '𝗩', 'W': '𝗪', 'X': '𝗫', 'Y': '𝗬',
        'Z': '𝗭'
    }
    return ''.join(bold.get(c, c) for c in text)

def italic_unicode(text):
    """ইটালিক ইউনিকোড"""
    italic = {
        'a': '𝘢', 'b': '𝘣', 'c': '𝘤', 'd': '𝘥', 'e': '𝘦',
        'f': '𝘧', 'g': '𝘨', 'h': '𝘩', 'i': '𝘪', 'j': '𝘫',
        'k': '𝘬', 'l': '𝘭', 'm': '𝘮', 'n': '𝘯', 'o': '𝘰',
        'p': '𝘱', 'q': '𝘲', 'r': '𝘳', 's': '𝘴', 't': '𝘵',
        'u': '𝘶', 'v': '𝘷', 'w': '𝘸', 'x': '𝘹', 'y': '𝘺',
        'z': '𝘻'
    }
    return ''.join(italic.get(c, c) for c in text)

def generate_caption(topic_text):
    """সম্পূর্ণ স্টাইলিশ ক্যাপশন তৈরি"""
    
    # কন্টেন্ট সিলেক্ট
    fact = random.choice(FACTS)
    tip = random.choice(TIPS)
    review = random.choice(REVIEWS)
    
    title_template = random.choice(TITLE_TEMPLATES)
    title_raw = title_template.format(fact=fact, tip=tip, review=review)
    
    # ফন্ট স্টাইল ভ্যারিয়েশন
    style_fn = random.choice([stylish_unicode, bold_unicode, italic_unicode, str])
    
    # কিছু ইংরেজি শব্দে স্টাইল (পুরো বাংলা টেক্সটে না)
    english_words = ["Web Dev", "React JS", "Python", "API", "Tech", "Code"]
    styled_word = style_fn(random.choice(english_words))
    
    # ডেসক্রিপশন
    desc_template = random.choice(DESC_TEMPLATES)
    body = random.choice([fact, tip, review])
    
    # হ্যাশট্যাগ
    fixed = random.sample(FIXED_HASHTAGS, 4)
    trending = fetch_trending_tags()
    extra = random.sample(TRENDING_TAGS, 3)
    all_tags = " ".join(fixed + trending + extra)
    
    # ফাইনাল ক্যাপশন
    divider = "━" * 30
    
    caption = f"""
{divider}
🔥 {title_raw}
{divider}

{body}

━━━━━━━━━━━━━━━━
💼 {bold_unicode('Service')}: {styled_word}
📩 {italic_unicode('Contact')}: t.me/hacker_52
🌐 {stylish_unicode('Follow Us')} for daily tips!
━━━━━━━━━━━━━━━━

{all_tags}
""".strip()
    
    return caption

# ==========================================
# ১১. মেইন ফাংশন
# ==========================================
def main():
    print("=" * 50)
    print(f"🚀 Bot Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Pixabay: {'✅' if PIXABAY_API_KEY else '❌'}")
    print(f"🔑 Pexels:  {'✅' if PEXELS_API_KEY else '❌'}")
    print(f"🔑 Unsplash:{'✅' if UNSPLASH_API_KEY else '❌'}")
    print(f"🔑 Facebook:{'✅' if PAGE_ID and ACCESS_TOKEN else '❌'}")
    print("=" * 50)
    
    try:
        # ১. টেক্সট সিলেক্ট
        content_pool = FACTS + TIPS + REVIEWS
        main_text = random.choice(content_pool)
        print(f"📝 Content: {main_text[:60]}...")
        
        # ২. ইমেজ তৈরি (Pixabay PRIMARY)
        img_path = generate_image(main_text, style='auto')
        print(f"🖼️  Image: {img_path}")
        
        # ৩. ভয়েস তৈরি
        voice_path, lang = generate_voice(main_text)
        print(f"🎙️  Voice: {lang}")
        
        # ৪. ভিডিও তৈরি
        video_path = create_video(img_path, voice_path, main_text)
        print(f"🎬 Video: {video_path}")
        
        # ৫. ক্যাপশন
        caption = generate_caption(main_text)
        print(f"📋 Caption preview:\n{caption[:200]}...")
        
        # ৬. Facebook আপলোড
        print("📤 Uploading to Facebook...")
        result = upload_to_facebook(video_path, main_text[:80], caption)
        print(f"📊 Result: {result}")
        
    except Exception as e:
        print(f"❌ Main error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # ৭. ক্লিনআপ
        for var in ['img_path', 'voice_path', 'video_path']:
            path = locals().get(var)
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                    print(f"🧹 Cleaned: {var}")
                except:
                    pass
    
    print("=" * 50)
    print(f"✅ Done: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

if __name__ == "__main__":
    main()
