import os
import io
import requests
import random
import tempfile
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy.editor import (
    ImageClip, AudioFileClip, VideoFileClip,
    CompositeVideoClip, TextClip
)

# ==========================================
# 1. CONFIGURATION (API Keys)
# ==========================================
PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID')
ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN')
PIXABAY_API_KEY = os.environ.get('PIXABAY_API_KEY')
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')
UNSPLASH_API_KEY = os.environ.get('UNSPLASH_API_KEY')

# ==========================================
# 2. CONTENT LIBRARY
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
# 3. COLOR THEMES
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
# 4. TRENDING HASHTAGS
# ==========================================
def fetch_trending_tags():
    """Pixabay → Pexels → Fallback"""
    if PIXABAY_API_KEY:
        try:
            query = random.choice(PIXABAY_THEMES)
            url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&per_page=5&category=technology"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                hits = resp.json().get('hits', [])
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

    if PEXELS_API_KEY:
        try:
            url = "https://api.pexels.com/v1/popular?per_page=5"
            headers = {"Authorization": PEXELS_API_KEY}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                photos = resp.json().get('photos', [])
                tags = []
                for photo in photos[:2]:
                    alt = photo.get('alt', '').replace(' ', '')
                    if alt:
                        tags.append(f"#{alt[:15]}")
                if tags:
                    print("✅ Tags from Pexels")
                    return tags
        except Exception as e:
            print(f"⚠️ Pexels tags error: {e}")

    print("✅ Tags from local pool")
    return random.sample(TRENDING_TAGS, 2)


# ==========================================
# 5. FONT LOADER
# ==========================================
def load_fonts():
    """Best available system fonts including Bengali"""
    font_paths = {
        'bold': [
            "/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
        ],
        'regular': [
            "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
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
                print(f"✅ Font loaded [{style}]: {os.path.basename(path)}")
                break
        if style not in loaded:
            loaded[style] = None
    return loaded


# ==========================================
# 6. IMAGE SOURCES
# ==========================================
def fetch_pixabay_image(query):
    """PRIMARY: Pixabay"""
    if not PIXABAY_API_KEY:
        return None
    try:
        url = (
            f"https://pixabay.com/api/?key={PIXABAY_API_KEY}"
            f"&q={query}&image_type=photo&category=technology"
            f"&orientation=horizontal&per_page=10&safesearch=true"
            f"&min_width=1200&min_height=600"
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
                    print(f"✅ Pixabay image: {chosen.get('tags','')[:30]}")
                    return img
    except Exception as e:
        print(f"⚠️ Pixabay image error: {e}")
    return None


def fetch_pexels_image(query):
    """BACKUP 1: Pexels"""
    if not PEXELS_API_KEY:
        return None
    try:
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=10&orientation=landscape"
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


def fetch_unsplash_image(query):
    """BACKUP 2: Unsplash (List/Dict উভয় handle করে)"""
    if not UNSPLASH_API_KEY:
        return None
    try:
        url = f"https://api.unsplash.com/photos/random?query={query}&orientation=landscape&count=1"
        headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
        resp = requests.get(url, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            data = resp.json()
            img_url = None
            
            if isinstance(data, list):
                if data and len(data) > 0:
                    img_url = data[0].get('urls', {}).get('regular')
            elif isinstance(data, dict):
                img_url = data.get('urls', {}).get('regular')
            
            if img_url:
                img_resp = requests.get(img_url, timeout=20)
                if img_resp.status_code == 200:
                    img = Image.open(io.BytesIO(img_resp.content)).convert('RGB')
                    img = img.resize((1200, 628), Image.LANCZOS)
                    print("✅ Unsplash image fetched")
                    return img
                    
    except Exception as e:
        print(f"⚠️ Unsplash image error: {e}")
    
    return None


# ==========================================
# 7. GRADIENT BACKGROUND
# ==========================================
def create_gradient_background(theme_colors, width=1200, height=628):
    """Professional gradient with decorations"""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    c1 = theme_colors['color1']
    c2 = theme_colors['color2']
    accent = theme_colors['accent']

    for y in range(height):
        t = y / height
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)

    ov_draw.ellipse([width - 350, -150, width + 100, 350], fill=(*accent, 25))
    ov_draw.ellipse([-100, height - 300, 250, height + 50], fill=(*accent, 20))
    ov_draw.ellipse(
        [width // 2 - 200, height // 2 - 200, width // 2 + 200, height // 2 + 200],
        fill=(*accent, 10)
    )

    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

    draw = ImageDraw.Draw(img)
    for x in range(0, width, 80):
        draw.line([(x, 0), (x, height)], fill=(*accent, 8), width=1)
    for y in range(0, height, 80):
        draw.line([(0, y), (width, y)], fill=(*accent, 8), width=1)

    print("✅ Gradient background created")
    return img


# ==========================================
# 8. PROFESSIONAL OVERLAY
# ==========================================
def add_professional_overlay(img, theme_colors):
    """Dark overlay + accent borders on photo"""
    width, height = img.size
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)

    for y in range(height):
        t = y / height
        alpha = int(80 + 100 * t)
        ov_draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))

    for x in range(width // 2):
        t = 1 - (x / (width // 2))
        alpha = int(60 * t)
        for y in range(height):
            ov_draw.point((x, y), fill=(0, 0, 0, alpha))

    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

    draw = ImageDraw.Draw(img)
    accent = theme_colors['accent']
    draw.rectangle([(0, 0), (width, 5)], fill=accent)
    draw.rectangle([(0, height - 5), (width, height)], fill=accent)

    return img


# ==========================================
# 9. TEXT WRAP HELPER
# ==========================================
def wrap_text(text, font, max_width, draw):
    """Wrap long text into multiple lines"""
    words = text.split()
    lines = []
    current = ""
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
# 10. LAYOUT DRAWERS
# ==========================================
def draw_card_layout(img, draw, text, theme_colors,
                     font_huge, font_large, font_medium,
                     font_small, font_tiny, width, height):
    """Semi-transparent card on left side"""
    accent = theme_colors['accent']
    highlight = theme_colors['highlight']

    card_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_overlay)

    cx1, cy1, cx2, cy2 = 50, 80, 780, height - 80
    card_draw.rectangle([cx1, cy1, cx2, cy2], fill=(0, 0, 0, 140))
    card_draw.rectangle([cx1, cy1, cx2, cy1 + 4], fill=(*accent, 230))
    card_draw.rectangle([cx1, cy1, cx1 + 4, cy2], fill=(*accent, 180))

    merged = Image.alpha_composite(img.convert('RGBA'), card_overlay).convert('RGB')
    img.paste(merged)
    draw = ImageDraw.Draw(img)

    tag_text = "⚡ TECH TIPS"
    tag_x, tag_y = 80, 110
    try:
        tag_w = int(draw.textlength(tag_text, font=font_tiny))
    except Exception:
        tag_w = 120
    draw.rectangle([tag_x - 10, tag_y - 5, tag_x + tag_w + 10, tag_y + 30], fill=accent)
    draw.text((tag_x, tag_y), tag_text, fill=(0, 0, 0), font=font_tiny)

    lines = wrap_text(text, font_large, 680, draw)
    y_pos = 165
    for i, line in enumerate(lines[:4]):
        draw.text((82, y_pos + 2), line, fill=(0, 0, 0), font=font_large)
        color = highlight if i == 0 else (255, 255, 255)
        draw.text((80, y_pos), line, fill=color, font=font_large)
        y_pos += 58

    div_y = y_pos + 15
    draw.rectangle([(80, div_y), (280, div_y + 3)], fill=accent)
    draw.rectangle([(290, div_y + 1), (480, div_y + 2)], fill=(*accent, 100))

    draw.text((80, div_y + 20), "🔗 t.me/hacker_52 | ফলো করুন", fill=accent, font=font_small)

    brand = "@hacker_52"
    try:
        brand_w = int(draw.textlength(brand, font=font_medium))
    except Exception:
        brand_w = 180
    bx = cx2 - brand_w - 20
    by = cy2 - 55
    draw.rectangle([bx - 12, by - 8, cx2 - 10, by + 42], fill=accent)
    draw.text((bx, by), brand, fill=(0, 0, 0), font=font_medium)

    date_str = datetime.now().strftime("%d %b %Y")
    draw.text((cx1 + 10, cy2 - 35), date_str, fill=(*accent, 150), font=font_tiny)


def draw_split_layout(img, draw, text, theme_colors,
                      font_huge, font_large, font_medium,
                      font_small, font_tiny, width, height):
    """Left-right split layout"""
    accent = theme_colors['accent']
    highlight = theme_colors['highlight']

    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rectangle([0, 0, width // 2 - 20, height], fill=(0, 0, 0, 170))
    merged = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    img.paste(merged)
    draw = ImageDraw.Draw(img)

    draw.rectangle([(width // 2 - 8, 0), (width // 2 - 4, height)], fill=accent)
    draw.rectangle([(width // 2 - 22, 0), (width // 2 - 20, height)], fill=(*accent, 80))

    draw.text((30, 60), "01", fill=(*accent, 25), font=font_huge)

    lines = wrap_text(text, font_large, width // 2 - 80, draw)
    y_pos = 120
    for i, line in enumerate(lines[:3]):
        color = highlight if i == 0 else (255, 255, 255)
        draw.text((62, y_pos + 2), line, fill=(0, 0, 0), font=font_large)
        draw.text((60, y_pos), line, fill=color, font=font_large)
        y_pos += 60

    draw.rectangle([(60, y_pos + 10), (210, y_pos + 14)], fill=accent)
    draw.text((60, height - 100), "💡 @hacker_52", fill=highlight, font=font_medium)
    draw.text((60, height - 65), "t.me/hacker_52", fill=accent, font=font_small)

    cx = width * 3 // 4
    cy = height // 2
    draw.rectangle([cx - 100, cy - 100, cx + 100, cy + 100], outline=(*accent, 80), width=2)
    draw.rectangle([cx - 85, cy - 85, cx + 85, cy + 85], outline=(*accent, 40), width=1)

    icons = ["⚡", "🚀", "💻", "🔥", "✨", "🎯"]
    draw.text((cx - 45, cy - 55), random.choice(icons), fill=(255, 255, 255), font=font_huge)

    for i in range(4):
        for j in range(4):
            dx = cx - 150 + i * 30
            dy = cy + 130 + j * 20
            draw.ellipse([dx, dy, dx + 6, dy + 6], fill=(*accent, 80))


def draw_minimal_layout(img, draw, text, theme_colors,
                        font_huge, font_large, font_medium,
                        font_small, font_tiny, width, height):
    """Clean minimal bottom-text layout"""
    accent = theme_colors['accent']
    highlight = theme_colors['highlight']

    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rectangle([0, height // 2, width, height], fill=(0, 0, 0, 200))
    for y in range(height // 3):
        alpha = int(200 * (y / (height // 3)))
        ov_draw.line([(0, height // 2 - y), (width, height // 2 - y)], fill=(0, 0, 0, alpha))
    merged = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    img.paste(merged)
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (width, 6)], fill=accent)
    draw.text((40, 25), "⚡ hacker_52", fill=(255, 255, 255), font=font_small)

    lines = wrap_text(text, font_large, width - 100, draw)
    total_h = len(lines[:3]) * 62
    y_pos = height - total_h - 100

    for i, line in enumerate(lines[:3]):
        color = highlight if i == 0 else (230, 230, 230)
        draw.text((52, y_pos + 3), line, fill=(0, 0, 0), font=font_large)
        draw.text((50, y_pos), line, fill=color, font=font_large)
        y_pos += 62

    draw.rectangle([(0, height - 6), (width, height)], fill=accent)
    link_text = "📱 t.me/hacker_52 | #webdev #tech #coding"
    try:
        link_w = int(draw.textlength(link_text, font=font_tiny))
    except Exception:
        link_w = 400
    draw.text(((width - link_w) // 2, height - 35), link_text, fill=(200, 200, 200), font=font_tiny)


def draw_bold_center_layout(img, draw, text, theme_colors,
                            font_huge, font_large, font_medium,
                            font_small, font_tiny, width, height):
    """Bold centered impactful layout"""
    accent = theme_colors['accent']
    highlight = theme_colors['highlight']

    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 160))
    merged = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    img.paste(merged)
    draw = ImageDraw.Draw(img)

    s = 40
    draw.rectangle([(20, 20), (20 + s, 25)], fill=accent)
    draw.rectangle([(20, 20), (25, 20 + s)], fill=accent)
    draw.rectangle([(width - 20 - s, 20), (width - 20, 25)], fill=accent)
    draw.rectangle([(width - 25, 20), (width - 20, 20 + s)], fill=accent)
    draw.rectangle([(20, height - 25), (20 + s, height - 20)], fill=accent)
    draw.rectangle([(20, height - 20 - s), (25, height - 20)], fill=accent)
    draw.rectangle([(width - 20 - s, height - 25), (width - 20, height - 20)], fill=accent)
    draw.rectangle([(width - 25, height - 20 - s), (width - 20, height - 20)], fill=accent)

    icons = ["🚀", "💡", "⚡", "🎯", "🔥", "✨"]
    icon = random.choice(icons)
    try:
        icon_w = int(draw.textlength(icon, font=font_huge))
    except Exception:
        icon_w = 60
    draw.text(((width - icon_w) // 2, 60), icon, fill=(255, 255, 255), font=font_huge)

    draw.rectangle([(width // 2 - 100, 140), (width // 2 + 100, 144)], fill=accent)

    lines = wrap_text(text, font_large, width - 160, draw)
    total_h = len(lines[:4]) * 62
    y_pos = (height - total_h) // 2 - 20

    for i, line in enumerate(lines[:4]):
        try:
            line_w = int(draw.textlength(line, font=font_large))
        except Exception:
            line_w = len(line) * 25
        x_pos = (width - line_w) // 2
        color = highlight if i == 0 else (255, 255, 255)
        draw.text((x_pos + 3, y_pos + 3), line, fill=(0, 0, 0), font=font_large)
        draw.text((x_pos, y_pos), line, fill=color, font=font_large)
        y_pos += 62

    draw.rectangle([(width // 2 - 100, y_pos + 20), (width // 2 + 100, y_pos + 24)], fill=accent)
    brand = "@hacker_52 | t.me/hacker_52"
    try:
        brand_w = int(draw.textlength(brand, font=font_small))
    except Exception:
        brand_w = 300
    draw.text(((width - brand_w) // 2, height - 80), brand, fill=highlight, font=font_small)


# ==========================================
# 11. ADD TEXT TO IMAGE
# ==========================================
def add_stylish_text(img, text, theme_colors, font_paths, layout='card'):
    """Load fonts and call chosen layout"""
    draw = ImageDraw.Draw(img)
    width, height = img.size

    try:
        bold_path = font_paths.get('bold')
        reg_path = font_paths.get('regular') or bold_path
        if bold_path:
            font_huge   = ImageFont.truetype(bold_path, 62)
            font_large  = ImageFont.truetype(bold_path, 46)
            font_medium = ImageFont.truetype(bold_path, 34)
            font_small  = ImageFont.truetype(reg_path, 26)
            font_tiny   = ImageFont.truetype(reg_path, 22)
        else:
            raise OSError("No font found")
    except Exception:
        default = ImageFont.load_default()
        font_huge = font_large = font_medium = font_small = font_tiny = default

    args = (img, draw, text, theme_colors, font_huge, font_large, font_medium, font_small, font_tiny, width, height)

    if layout == 'card':
        draw_card_layout(*args)
    elif layout == 'split':
        draw_split_layout(*args)
    elif layout == 'minimal':
        draw_minimal_layout(*args)
    elif layout == 'bold_center':
        draw_bold_center_layout(*args)

    return img


# ==========================================
# 12. MAIN IMAGE GENERATOR
# ==========================================
def generate_image(text):
    """Priority: Pixabay → Pexels → Unsplash → Gradient"""
    width, height = 1200, 628
    theme = random.choice(COLOR_THEMES)
    font_paths = load_fonts()
    query = random.choice(PIXABAY_THEMES)

    img_source = fetch_pixabay_image(query)

    if img_source is None:
        img_source = fetch_pexels_image(query)

    if img_source is None:
        img_source = fetch_unsplash_image(query)

    if img_source is None:
        img_source = create_gradient_background(theme, width, height)
    else:
        img_source = add_professional_overlay(img_source, theme)

    layout = random.choice(['card', 'split', 'minimal', 'bold_center'])
    print(f"✅ Layout: {layout} | Theme: {theme['name']}")

    final_img = add_stylish_text(img_source, text, theme, font_paths, layout=layout)

    temp_img = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    final_img.save(temp_img.name, quality=95)
    return temp_img.name


# ==========================================
# 13. VOICE GENERATOR
# ==========================================
def generate_voice(text, lang=None):
    """gTTS multi-language voice"""
    if lang is None:
        lang = random.choice(LANGUAGES)

    temp_audio = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)

    try:
        tts = gTTS(text=text, lang=lang, slow=random.choice([True, False]))
        tts.save(temp_audio.name)
        print(f"✅ Voice generated (lang: {lang})")
    except Exception as e:
        print(f"⚠️ Voice error ({lang}): {e} — retrying English")
        try:
            tts = gTTS(text=text[:200], lang='en', slow=False)
            tts.save(temp_audio.name)
            lang = 'en'
        except Exception as e2:
            print(f"❌ Voice failed: {e2}")

    return temp_audio.name, lang


# ==========================================
# 14. VIDEO CREATOR (FIXED)
# ==========================================
def create_video(image_path, voice_path, text, logo_text="⚡ @hacker_52", duration=15):
    """Image + audio → MP4 with Bengali font support"""
    output_path = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name

    bengali_font = None
    for font_path in [
        "/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]:
        if os.path.exists(font_path):
            bengali_font = font_path
            print(f"✅ Video font: {os.path.basename(font_path)}")
            break

    try:
        img_clip = ImageClip(image_path, duration=duration)
        audio_clip = AudioFileClip(voice_path)
        actual_duration = min(duration, audio_clip.duration + 2)
        img_clip = img_clip.set_duration(actual_duration)
        final_clip = img_clip.set_audio(audio_clip)

                    # ফন্ট পাওয়া গেলে ব্যবহার করব, না হলে font প্যারামিটার বাদ দেব
            if bengali_font:
                short_text = text[:80] + "..." if len(text) > 80 else text
                subtitle = TextClip(
                    short_text,
                    fontsize=28,
                    color='white',
                    stroke_color='black',
                    stroke_width=1.5,
                    method='caption',
                    size=(900, None),
                    align='center',
                    font=bengali_font
                ).set_position(('center', 'bottom')).set_duration(min(8, actual_duration)).set_opacity(0.9)

                logo_pos = random.choice([('center', 'bottom'), ('right', 'bottom')])
                logo = TextClip(
                    logo_text,
                    fontsize=42,
                    color='yellow',
                    stroke_color='black',
                    stroke_width=2,
                    method='label',
                    font=bengali_font
                ).set_position(logo_pos).set_duration(3).set_start(actual_duration - 3).set_opacity(0.95)
            else:
                short_text = text[:80] + "..." if len(text) > 80 else text
                subtitle = TextClip(
                    short_text,
                    fontsize=28,
                    color='white',
                    stroke_color='black',
                    stroke_width=1.5,
                    method='caption',
                    size=(900, None),
                    align='center'
                ).set_position(('center', 'bottom')).set_duration(min(8, actual_duration)).set_opacity(0.9)

                logo_pos = random.choice([('center', 'bottom'), ('right', 'bottom')])
                logo = TextClip(
                    logo_text,
                    fontsize=42,
                    color='yellow',
                    stroke_color='black',
                    stroke_width=2,
                    method='label'
                ).set_position(logo_pos).set_duration(3).set_start(actual_duration - 3).set_opacity(0.95)

        final = CompositeVideoClip([final_clip, subtitle, logo])
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
        print(f"⚠️ Video error: {e} — using simple fallback")
        img_clip = ImageClip(image_path, duration=12)
        img_clip.write_videofile(output_path, fps=24, verbose=False, logger=None)

    return output_path


# ==========================================
# 15. UNICODE FONT STYLES
# ==========================================
def bold_unicode(text):
    bold_map = {
        'a':'𝗮','b':'𝗯','c':'𝗰','d':'𝗱','e':'𝗲','f':'𝗳','g':'𝗴',
        'h':'𝗵','i':'𝗶','j':'𝗷','k':'𝗸','l':'𝗹','m':'𝗺','n':'𝗻',
        'o':'𝗼','p':'𝗽','q':'𝗾','r':'𝗿','s':'𝘀','t':'𝘁','u':'𝘂',
        'v':'𝘃','w':'𝘄','x':'𝘅','y':'𝘆','z':'𝘇',
        'A':'𝗔','B':'𝗕','C':'𝗖','D':'𝗗','E':'𝗘','F':'𝗙','G':'𝗚',
        'H':'𝗛','I':'𝗜','J':'𝗝','K':'𝗞','L':'𝗟','M':'𝗠','N':'𝗡',
        'O':'𝗢','P':'𝗣','Q':'𝗤','R':'𝗥','S':'𝗦','T':'𝗧','U':'𝗨',
        'V':'𝗩','W':'𝗪','X':'𝗫','Y':'𝗬','Z':'𝗭'
    }
    return ''.join(bold_map.get(c, c) for c in text)


def italic_unicode(text):
    italic_map = {
        'a':'𝘢','b':'𝘣','c':'𝘤','d':'𝘥','e':'𝘦','f':'𝘧','g':'𝘨',
        'h':'𝘩','i':'𝘪','j':'𝘫','k':'𝘬','l':'𝘭','m':'𝘮','n':'𝘯',
        'o':'𝘰','p':'𝘱','q':'𝘲','r':'𝘳','s':'𝘴','t':'𝘵','u':'𝘶',
        'v':'𝘷','w':'𝘸','x':'𝘹','y':'𝘺','z':'𝘻'
    }
    return ''.join(italic_map.get(c, c) for c in text)


def smallcaps_unicode(text):
    caps_map = {
        'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ғ','g':'ɢ',
        'h':'ʜ','i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ',
        'o':'ᴏ','p':'ᴘ','q':'ǫ','r':'ʀ','s':'s','t':'ᴛ','u':'ᴜ',
        'v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ'
    }
    return ''.join(caps_map.get(c.lower(), c) for c in text)


# ==========================================
# 16. CAPTION GENERATOR (WITH EMAIL)
# ==========================================
def generate_caption(topic_text):
    """Stylish caption with unicode fonts + hashtags + EMAIL"""
    fact = random.choice(FACTS)
    tip = random.choice(TIPS)
    review = random.choice(REVIEWS)

    title_raw = random.choice(TITLE_TEMPLATES).format(fact=fact, tip=tip, review=review)
    body = random.choice([fact, tip, review])

    english_words = ["Web Dev", "React JS", "Python", "API", "Tech", "Code", "Flutter"]
    style_fn = random.choice([bold_unicode, italic_unicode, smallcaps_unicode])
    styled_word = style_fn(random.choice(english_words))

    fixed = random.sample(FIXED_HASHTAGS, 4)
    trending = fetch_trending_tags()
    extra = random.sample(TRENDING_TAGS, 3)
    all_tags = " ".join(fixed + trending + extra)

    divider = "━" * 32

    caption = (
        f"{divider}\n"
        f"🔥 {title_raw}\n"
        f"{divider}\n\n"
        f"{body}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💼 {bold_unicode('Service')}: {styled_word}\n"
        f"📧 {italic_unicode('Email')}: rahulhaku52@gmail.com\n"
        f"📱 {italic_unicode('Telegram')}: t.me/hacker_52\n"
        f"🌐 {smallcaps_unicode('Follow Us')} for daily tips!\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{all_tags}"
    )

    return caption


# ==========================================
# 17. FACEBOOK UPLOAD
# ==========================================
def upload_to_facebook(video_path, title, description):
    """Upload video to Facebook Page"""
    if not PAGE_ID or not ACCESS_TOKEN:
        print("❌ Facebook credentials missing!")
        return {"error": "Missing credentials"}

    url = f"https://graph.facebook.com/{PAGE_ID}/videos"

    try:
        with open(video_path, 'rb') as vf:
            files = {'source': vf}
            data = {
                'access_token': ACCESS_TOKEN,
                'title': title[:100],
                'description': description[:2000],
                'published': True
            }
            resp = requests.post(url, files=files, data=data, timeout=180)
            result = resp.json()

        if 'id' in result:
            print(f"✅ Uploaded! Video ID: {result['id']}")
        else:
            print(f"⚠️ Upload response: {result}")

        return result

    except Exception as e:
        print(f"❌ Upload error: {e}")
        return {"error": str(e)}


# ==========================================
# 18. MAIN
# ==========================================
def main():
    print("=" * 50)
    print(f"🚀 Bot Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Pixabay : {'✅ Ready' if PIXABAY_API_KEY  else '❌ Missing'}")
    print(f"🔑 Pexels  : {'✅ Ready' if PEXELS_API_KEY   else '❌ Missing'}")
    print(f"🔑 Unsplash: {'✅ Ready' if UNSPLASH_API_KEY  else '❌ Missing'}")
    print(f"🔑 Facebook: {'✅ Ready' if PAGE_ID and ACCESS_TOKEN else '❌ Missing'}")
    print("=" * 50)

    img_path = None
    voice_path = None
    video_path = None

    try:
        content_pool = FACTS + TIPS + REVIEWS
        main_text = random.choice(content_pool)
        print(f"📝 Content: {main_text[:70]}...")

        img_path = generate_image(main_text)
        print(f"🖼️  Image saved: {img_path}")

        voice_path, lang = generate_voice(main_text)
        print(f"🎙️  Voice saved (lang={lang}): {voice_path}")

        video_path = create_video(img_path, voice_path, main_text)
        print(f"🎬 Video saved: {video_path}")

        caption = generate_caption(main_text)
        print(f"\n📋 Caption preview:\n{caption[:300]}\n...")

        print("📤 Uploading to Facebook...")
        result = upload_to_facebook(video_path, main_text[:80], caption)
        print(f"📊 Final result: {result}")

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        for label, path in [("image", img_path), ("voice", voice_path), ("video", video_path)]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                    print(f"🧹 Cleaned {label}: {path}")
                except Exception:
                    pass

    print("=" * 50)
    print(f"✅ Done: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)


if __name__ == "__main__":
    main()
