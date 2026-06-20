import os
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
import urllib.parse

# ==========================================
# ১. কনফিগারেশন (API Keys)
# ==========================================
PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID')
ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN')
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')
UNSPLASH_API_KEY = os.environ.get('UNSPLASH_API_KEY')  # ঐচ্ছিক

# ==========================================
# ২. ভ্যারিয়েবল লাইব্রেরি
# ==========================================

# ২.১ টাইটেল টেমপ্লেট (৬টি)
TITLE_TEMPLATES = [
    "আপনি কি জানেন? {fact}",
    "{tip} — মাত্র ৩০ সেকেন্ডে শিখুন",
    "ক্লায়েন্ট বললো: {review}",
    "🚀 {fact} — এখনই শুরু করুন",
    "💡 {tip} — প্রো টিপস",
    "📱 {fact} — শর্টস ভার্সন"
]

# ২.২ ফ্যাক্ট/টিপ/রিভিউ লাইব্রেরি
FACTS = [
    "ওয়েবসাইটের লোড টাইম ৩ সেকেন্ডের বেশি হলে ৫০% ভিজিটর চলে যায়",
    "মোবাইল ফ্রেন্ডলি ওয়েবসাইট Google-এ বেশি র্যাঙ্ক পায়",
    "React JS ২০২৬-এ সবচেয়ে ডিমান্ডেড স্কিল",
    "Python দিয়ে ১০ মিনিটেই ওয়েব অ্যাপ বানানো যায়",
    "API ইন্টিগ্রেশন ছাড়া আধুনিক অ্যাপ অসম্পূর্ণ"
]
TIPS = [
    "CSS গ্রিড দিয়ে লেআউট ডিজাইন করুন",
    "JavaScript-এ async/await ব্যবহার করুন",
    "Git দিয়ে কোড ভার্সন কন্ট্রোল করুন",
    "VS Code-এ শর্টকাট শিখুন"
]
REVIEWS = [
    "আমার ওয়েবসাইট ২ দিনে তৈরি করে দিয়েছে!",
    "অ্যাপটা ফাস্ট আর ইউজার ফ্রেন্ডলি",
    "ডিজাইনটা ছিল আমার স্বপ্নের মতো"
]

# ২.৩ ডেসক্রিপশন টেমপ্লেট (৫টি)
DESC_TEMPLATES = [
    "💻 {title}\n\n{body}\n\n📩 যোগাযোগ: t.me/hacker_52\n🔗 আরও টিপসের জন্য ফলো করুন!",
    "🔥 {title}\n\n{body}\n\n📱 আমাদের সাথে থাকুন: t.me/hacker_52",
    "✨ {title}\n\n{body}\n\n🤝 স্মার্ট ওয়েব সলিউশনের জন্য @hacker_52",
    "⚡ {title}\n\n{body}\n\n💡 আপনার প্রোজেক্টের কথা বলুন: t.me/hacker_52",
    "🎯 {title}\n\n{body}\n\n📌 ভুলে যাবেন না: শেয়ার করুন আর লাইক দিন!"
]

# ২.৪ ফিক্সড হ্যাশট্যাগ
FIXED_HASHTAGS = [
    "#webdevelopment", "#appdevelopment", "#shorts", 
    "#codingtips", "#programming", "#tech"
]

# ২.৫ ট্রেন্ডিং হ্যাশট্যাগ পুল (Pexels থিম থেকে)
TRENDING_TAGS = [
    "#webdesign", "#developer", "#coder", "#frontend",
    "#backend", "#fullstack", "#reactjs", "#python",
    "#javascript", "#nodejs", "#flutter", "#android",
    "#ios", "#uiux", "#startup", "#entrepreneur",
    "#digitalmarketing", "#seo", "#wordpress", "#laravel"
]

# ২.৬ ভাষা (বাংলা, ইংরেজি, হিন্দি)
LANGUAGES = ['bn', 'en', 'hi']

# ২.৭ টেক্সট পজিশন ভ্যারিয়েশন
TEXT_POSITIONS = [
    ('center', 'bottom'),
    ('center', 'top'),
    ('left', 'bottom'),
    ('right', 'bottom'),
    ('center', 'center')
]

# ২.৮ ইমেজ থিম (Unsplash সার্চের জন্য)
UNSPLASH_THEMES = [
    "technology", "coding", "developer", "web design",
    "laptop", "programming", "startup", "digital"
]

# ==========================================
# ৩. ট্রেন্ডিং হ্যাশট্যাগ ফেচ (Pexels থেকে)
# ==========================================
def fetch_trending_tags():
    """Pexels থেকে ট্রেন্ডিং থিম খুঁজে হ্যাশট্যাগ বানায়"""
    try:
        url = "https://api.pexels.com/v1/popular?per_page=5"
        headers = {"Authorization": PEXELS_API_KEY}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            tags = [f"#{tag['title'].replace(' ', '')}" for tag in data.get('photos', [])[:2]]
            return tags if tags else random.sample(TRENDING_TAGS, 2)
    except:
        pass
    return random.sample(TRENDING_TAGS, 2)

# ==========================================
# ৪. ইমেজ জেনারেট (Unsplash + গ্রেডিয়েন্ট + স্ক্রিনশট স্টাইল)
# ==========================================
def generate_image(text, style='gradient'):
    """
    ইমেজ তৈরি: কখনো গ্রেডিয়েন্ট, কখনো Unsplash থেকে, কখনো পোর্টফোলিও স্টাইল
    """
    width, height = 1200, 628
    
    # স্টাইল সিলেক্ট
    if style == 'unsplash' and UNSPLASH_API_KEY:
        # Unsplash থেকে ইমেজ আনা
        theme = random.choice(UNSPLASH_THEMES)
        url = f"https://api.unsplash.com/photos/random?query={theme}&orientation=landscape&count=1"
        headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data:
                    img_url = data[0]['urls']['regular']
                    img_resp = requests.get(img_url, timeout=20)
                    if img_resp.status_code == 200:
                        img = Image.open(io.BytesIO(img_resp.content))
                        img = img.resize((width, height))
                        # ফিল্টার যোগ (ডার্কনেস)
                        img = img.filter(ImageFilter.GaussianBlur(2))
                        draw = ImageDraw.Draw(img)
                        # ওভারলে ডার্ক
                        overlay = Image.new('RGBA', (width, height), (0,0,0,100))
                        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        except:
            img = None
    else:
        img = None
    
    # যদি Unsplash না পাওয়া যায়, গ্রেডিয়েন্ট ইমেজ
    if img is None:
        color1 = (random.randint(10,60), random.randint(10,60), random.randint(40,90))
        color2 = (random.randint(100,200), random.randint(100,200), random.randint(200,255))
        img = Image.new('RGB', (width, height), color1)
        draw = ImageDraw.Draw(img)
        
        # গ্রেডিয়েন্ট ইফেক্ট (শুধু এক্সট্রা ডেকোরেশন)
        for i in range(height):
            alpha = int((i/height) * 150)
            r = int(color1[0] + (color2[0] - color1[0]) * (i/height))
            g = int(color1[1] + (color2[1] - color1[1]) * (i/height))
            b = int(color1[2] + (color2[2] - color1[2]) * (i/height))
            draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # টেক্সট যোগ করা
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 50)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 30)
    except:
        font = ImageFont.load_default()
        font_small = font
    
    # টেক্সট পজিশন ভ্যারিয়েশন
    pos_x, pos_y = random.choice(TEXT_POSITIONS)
    lines = text.split('\n')
    y_start = 100 if pos_y == 'top' else (height - 200 if pos_y == 'bottom' else 250)
    
    for i, line in enumerate(lines[:4]):
        if pos_x == 'center':
            x = width//2 - (draw.textsize(line, font=font)[0]//2)
        elif pos_x == 'left':
            x = 100
        else:
            x = width - 400
        draw.text((x, y_start + i*80), line, fill=(255,255,255), font=font)
    
    # ফুটার (লোগো/URL) শেষ ২ সেকেন্ডের জন্য আলাদা হবে
    temp_img = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_img.name)
    return temp_img.name

# ==========================================
# ৫. ভয়েস জেনারেট (একাধিক ভাষা)
# ==========================================
def generate_voice(text, lang=None):
    if lang is None:
        lang = random.choice(LANGUAGES)
    temp_audio = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
    tts = gTTS(text=text, lang=lang, slow=random.choice([True, False]))
    tts.save(temp_audio.name)
    return temp_audio.name, lang

# ==========================================
# ৬. ভিডিও তৈরি (ইমেজ + ভয়েস + লোগো ওভারলে)
# ==========================================
def create_video(image_path, voice_path, text, logo_text="@hacker_52", duration=12):
    output_path = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
    
    # ইমেজ ক্লিপ
    clip = ImageClip(image_path, duration=duration)
    
    # ভয়েস অডিও
    voice_audio = AudioFileClip(voice_path)
    
    # অডিও সেট
    final_clip = clip.set_audio(voice_audio)
    
    # টেক্সট ওভারলে (শুধু মেইন টেক্সট, ইমেজে তো আছেই)
    txt_clip = TextClip(
        text, 
        fontsize=30, 
        color='white', 
        stroke_color='black', 
        stroke_width=1,
        method='caption'
    )
    txt_pos = random.choice(['bottom', 'top', 'center'])
    txt_clip = txt_clip.set_position(('center', txt_pos)).set_duration(duration).set_opacity(0.8)
    
    # লোগো/ওয়েবসাইট টেক্সট (শেষ ২ সেকেন্ড)
    logo_clip = TextClip(
        logo_text,
        fontsize=40,
        color='yellow',
        stroke_color='black',
        stroke_width=2
    )
    logo_pos = random.choice([('left', 'bottom'), ('right', 'bottom'), ('center', 'bottom')])
    logo_clip = logo_clip.set_position(logo_pos).set_duration(2).set_start(duration-2)
    
    # সবকিছু কম্পোজিট
    final = CompositeVideoClip([final_clip, txt_clip, logo_clip])
    
    # ভিডিও রেন্ডার
    final.write_videofile(output_path, fps=24, verbose=False, logger=None)
    
    return output_path

# ==========================================
# ৭. ফেসবুকে আপলোড
# ==========================================
def upload_to_facebook(video_path, title, description):
    url = f"https://graph.facebook.com/{PAGE_ID}/videos"
    files = {'source': open(video_path, 'rb')}
    data = {
        'access_token': ACCESS_TOKEN,
        'title': title[:100],
        'description': description[:500],
        'published': True
    }
    resp = requests.post(url, files=files, data=data)
    return resp.json()

# ==========================================
# ৮. ক্যাপশন তৈরি (স্টাইলিশ + ফন্ট স্টাইল)
# ==========================================
def generate_caption(topic_text):
    """
    ক্যাপশন তৈরি: ফ্যাশনেবল ফন্ট স্টাইল + ইমোজি + ভাষা ভ্যারিয়েশন
    """
    # ইউনিকোড বোল্ড/ইটালিক মিক্স (ফন্ট স্টাইল)
    def style_text(t):
        chars = {
            'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ',
            'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
            'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ',
            'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ',
            'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ',
            'z': 'ᴢ'
        }
        return ''.join([chars.get(c.lower(), c) for c in t]) if random.choice([True, False]) else t.upper()
    
    # টাইটেল বাছাই
    title_template = random.choice(TITLE_TEMPLATES)
    fact = random.choice(FACTS)
    tip = random.choice(TIPS)
    review = random.choice(REVIEWS)
    
    title = title_template.format(
        fact=fact,
        tip=tip,
        review=review
    )
    
    # ডেসক্রিপশন বাছাই
    desc_template = random.choice(DESC_TEMPLATES)
    body = random.choice([fact, tip, review])
    
    # হ্যাশট্যাগ
    fixed_tags = " ".join(random.sample(FIXED_HASHTAGS, 3))
    trending = fetch_trending_tags()
    all_tags = f"{fixed_tags} {' '.join(trending)}"
    
    # স্টাইলিশ ক্যাপশন (ইমোজি + ফন্ট স্টাইল)
    caption = desc_template.format(
        title=style_text(title)[:50],
        body=body
    )
    caption += f"\n\n{all_tags}"
    
    # ভাষা ভ্যারিয়েশন (ইমোজি যোগ)
    if random.choice([True, False]):
        caption = caption.replace("🔥", "⚡").replace("💻", "📱").replace("✨", "🌟")
    
    return caption

# ==========================================
# ৯. মেইন ফাংশন
# ==========================================
def main():
    print(f"🚀 Starting Human-Like Video Poster at {datetime.now()}")
    
    # ১. টেক্সট সিলেক্ট
    fact = random.choice(FACTS)
    tip = random.choice(TIPS)
    review = random.choice(REVIEWS)
    main_text = random.choice([fact, tip, review])
    
    # ২. ইমেজ স্টাইল সিলেক্ট
    style = random.choice(['gradient', 'gradient', 'unsplash', 'unsplash', 'gradient'])
    img_path = generate_image(main_text, style=style)
    print("✅ Image generated")
    
    # ৩. ভয়েস জেনারেট (ভাষা ভ্যারিয়েশন)
    voice_path, lang = generate_voice(main_text)
    print(f"✅ Voice generated (lang: {lang})")
    
    # ৪. ভিডিও তৈরি
    video_path = create_video(img_path, voice_path, main_text)
    print("✅ Video generated")
    
    # ৫. ক্যাপশন তৈরি
    caption = generate_caption(main_text)
    print(f"📝 Caption: {caption[:100]}...")
    
    # ৬. ফেসবুকে আপলোড
    result = upload_to_facebook(video_path, main_text[:80], caption)
    print(f"📤 Upload result: {result}")
    
    # ৭. ক্লিনআপ
    for f in [img_path, voice_path, video_path]:
        try:
            os.unlink(f)
        except:
            pass
    print("🧹 Cleanup done")
    print(f"✅ Finished at {datetime.now()}")

if __name__ == "__main__":
    main()
