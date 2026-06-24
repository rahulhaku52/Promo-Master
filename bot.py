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
    VideoFileClip, ImageClip, AudioFileClip,
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
GEMINI_API_KEY   = os.environ.get('GEMINI_API_KEY')

LOGO_PATH = "logo.png"

# Duration
MIN_DURATION    = 15
MAX_DURATION    = 25
TARGET_DURATION = 20

# Bengali Font
BENGALI_FONT_BOLD = "/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf"
BENGALI_FONT_REG  = "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf"

# edge-tts voices (Bengali + Hindi + English)
EDGE_VOICES = [
    "bn-BD-NabanitaNeural",
    "bn-BD-PradeepNeural",
    "bn-IN-TanishaaNeural",
    "hi-IN-SwaraNeural",
    "hi-IN-MadhurNeural",
    "en-US-JennyNeural",
]

# ==========================================
# 2. TOPICS — AI generation এর জন্য seed
# ==========================================
TECH_TOPICS = [
    "website optimization and page speed",
    "React JS and modern frontend development",
    "Python web development and automation",
    "mobile app development with Flutter",
    "SEO and digital marketing strategies",
    "Node JS and backend development",
    "TypeScript and large scale projects",
    "UI UX design principles",
    "Git version control best practices",
    "API integration and REST services",
    "Docker and deployment strategies",
    "database optimization techniques",
    "cybersecurity basics for developers",
    "cloud computing and AWS basics",
    "machine learning for beginners",
    "freelancing tips for developers",
    "open source contribution guide",
    "VS Code tips and productivity hacks",
    "JavaScript async programming",
    "full stack development roadmap"
]

VIDEO_SEARCH_KEYWORDS = [
    "technology workspace",
    "coding programmer",
    "computer screen code",
    "software development",
    "tech startup office",
    "digital innovation",
    "laptop programming",
    "developer working",
    "tech business",
    "modern office workspace"
]

# ==========================================
# 3. FALLBACK CONTENT
# ==========================================

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

FALLBACK_VOICE_SCRIPTS_BN = [
    "আজকের টেক টিপস নিয়ে আমরা কথা বলব। ওয়েবসাইটের লোড টাইম যদি তিন সেকেন্ডের বেশি হয়, তাহলে প্রায় পঞ্চাশ ভাগ ভিজিটর চলে যায়। তাই আপনার সাইটের স্পিড অপ্টিমাইজ করা খুবই জরুরি। ইমেজ কম্প্রেস করুন, ক্যাশিং চালু করুন, এবং অপ্রয়োজনীয় প্লাগিন বন্ধ করুন। আজই এই পরিবর্তনগুলো করুন এবং আপনার ওয়েবসাইটকে আরও দ্রুত করুন। প্রতিদিনের টেক আপডেটের জন্য আমাদের ফলো করুন।",
    "React JS আজকের দিনে সবচেয়ে জনপ্রিয় জাভাস্ক্রিপ্ট লাইব্রেরি। ২০২৬ সালে এটি সবচেয়ে বেশি চাহিদার স্কিল হিসেবে বিবেচিত হচ্ছে। কম্পোনেন্ট বেসড আর্কিটেকচার দিয়ে আপনি খুব দ্রুত ওয়েব অ্যাপ বানাতে পারবেন। ভার্চুয়াল ডম ব্যবহার করে React অ্যাপ অনেক দ্রুত চলে। আজই React শেখা শুরু করুন এবং আপনার ক্যারিয়ারকে নতুন উচ্চতায় নিয়ে যান। আমাদের সাথে থাকুন প্রতিদিন নতুন কিছু শেখার জন্য।",
]

FALLBACK_VOICE_SCRIPTS_HI = [
    "आज हम बात करेंगे वेबसाइट ऑप्टिमाइजेशन के बारे में। अगर आपकी वेबसाइट तीन सेकंड से ज्यादा लोड होती है, तो आधे से ज्यादा विजिटर चले जाते हैं। इसलिए अपनी साइट की स्पीड बढ़ाना बहुत जरूरी है। इमेज कंप्रेस करें, कैशिंग चालू करें और अनावश्यक प्लगइन हटाएं। आज ही ये बदलाव करें और अपनी वेबसाइट को तेज बनाएं। हर रोज टेक अपडेट के लिए हमें फॉलो करें।",
]

FALLBACK_VOICE_SCRIPTS_EN = [
    "Today we are talking about website optimization. Did you know that if your website takes more than three seconds to load, you lose about fifty percent of your visitors? This is a huge problem for any business. You need to compress your images, enable browser caching, and remove unnecessary plugins. These simple steps can dramatically improve your website speed. Follow us every day for more amazing tech tips and tricks that will help you grow your online presence.",
    "React JS is the most popular JavaScript library in the world right now. In 2026, it is expected to be the most demanded skill in the job market. With component based architecture, you can build complex web applications very quickly and efficiently. The virtual DOM makes React apps extremely fast and responsive. If you want to build a successful career in web development, start learning React today. Stay with us for daily programming tips and tutorials.",
]

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

# ==========================================
# 4. COLOR THEMES
# ==========================================
COLOR_THEMES = [
    {
        "name": "Deep Ocean",
        "accent": (0, 200, 255),
        "highlight": (0, 230, 255)
    },
    {
        "name": "Sunset Fire",
        "accent": (255, 150, 0),
        "highlight": (255, 200, 50)
    },
    {
        "name": "Purple Galaxy",
        "accent": (180, 0, 255),
        "highlight": (220, 150, 255)
    },
    {
        "name": "Forest Dark",
        "accent": (0, 200, 100),
        "highlight": (100, 255, 180)
    },
    {
        "name": "Steel Blue",
        "accent": (80, 160, 255),
        "highlight": (150, 220, 255)
    },
    {
        "name": "Neon Dark",
        "accent": (255, 0, 150),
        "highlight": (0, 255, 200)
    }
]

# ==========================================
# 5. GEMINI AI GENERATOR
# ==========================================
def call_gemini(prompt, max_tokens=500):
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY not set")
        return None

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": max_tokens,
            "topP": 0.95,
        }
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
                .strip()
            )
            if text:
                print(f"✅ Gemini response received ({len(text)} chars)")
                return text
            else:
                print("⚠️ Gemini: empty response")
                return None
        else:
            print(f"⚠️ Gemini HTTP {resp.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Gemini error: {e}")
        return None


def generate_voice_script_ai(lang, topic):
    if lang == 'bn':
        lang_instruction = (
            "বাংলা ভাষায় লিখুন। "
            "স্ক্রিপ্টটি স্বাভাবিক গতিতে পড়লে ঠিক ১৫ থেকে ২০ সেকেন্ড সময় নেয়। "
            "মোট শব্দ সংখ্যা ১২০ থেকে ১৫০ এর মধ্যে রাখুন। "
            "কথ্য ভাষায় লিখুন যাতে text-to-speech ভালো শোনায়।"
        )
        fallback_list = FALLBACK_VOICE_SCRIPTS_BN
    elif lang == 'hi':
        lang_instruction = (
            "हिंदी भाषा में लिखें। "
            "स्क्रिप्ट को सामान्य गति से पढ़ने पर ठीक 15 से 20 सेकंड लगने चाहिए। "
            "कुल शब्द संख्या 120 से 150 के बीच रखें। "
            "बोलचाल की भाषा में लिखें।"
        )
        fallback_list = FALLBACK_VOICE_SCRIPTS_HI
    else:
        lang_instruction = (
            "Write in clear, simple English. "
            "The script should take exactly 15 to 20 seconds to read at normal pace. "
            "Keep total word count between 120 and 150 words. "
            "Write in conversational style."
        )
        fallback_list = FALLBACK_VOICE_SCRIPTS_EN

    prompt = f"""You are a social media content creator for a tech page.

Write a voice-over script for a short tech video about: {topic}

Rules:
- {lang_instruction}
- Topic: {topic}
- Make it engaging and informative
- End with a call to action (follow us, contact us)
- Contact: rahulhaku52@gmail.com or Telegram t.me/hacker_52
- NO hashtags in script
- NO markdown formatting
- Write ONLY the script text directly"""

    result = call_gemini(prompt, max_tokens=400)

    if result and len(result.split()) >= 80:
        result = result.strip().replace('**', '').replace('*', '').replace('#', '')
        print(f"✅ Voice script AI ({lang}) — {len(result.split())} words")
        return result, 'ai'
    else:
        print(f"⚠️ Voice script fallback ({lang})")
        return random.choice(fallback_list), 'fallback'


def generate_image_text_ai(topic):
    prompt = f"""Create a short, punchy headline for a tech social media video.

Topic: {topic}

Rules:
- Maximum 5-6 words only
- Catchy and attention-grabbing
- No hashtags, no emojis
- Title case
- Examples: "React JS Pro Tips", "Build Apps Faster"
- Write ONLY the headline"""

    result = call_gemini(prompt, max_tokens=30)

    if result:
        result = result.strip().strip('"').strip("'")
        result = result.replace('**', '').replace('*', '').replace('#', '')
        words = result.split()
        if 2 <= len(words) <= 8:
            print(f"✅ Image text AI: '{result}'")
            return result, 'ai'

    print("⚠️ Image text fallback")
    return random.choice(IMAGE_TEXTS), 'fallback'


def generate_hook_ai(topic):
    prompt = f"""Create an attention-grabbing hook for a tech video.

Topic: {topic}

Rules:
- Maximum 8-10 words
- Start with emoji
- Make it urgent, exciting
- Examples: "🔥 This trick will save you hours!", "💡 Secret developers hide!"
- Write ONLY the hook"""

    result = call_gemini(prompt, max_tokens=40)

    if result:
        result = result.strip().strip('"').strip("'")
        words = result.split()
        if 3 <= len(words) <= 15:
            print(f"✅ Hook AI: '{result}'")
            return result, 'ai'

    print("⚠️ Hook fallback")
    return random.choice(HOOKS), 'fallback'


def generate_caption_ai(hook, image_text, topic):
    prompt = f"""Write a Facebook post caption for a tech video.

Hook: {hook}
Title: {image_text}
Topic: {topic}

Rules:
- English language
- Use emojis
- Include 3-4 facts/tips
- Call to action
- Contact: rahulhaku52@gmail.com | t.me/hacker_52
- Length: 150-250 words
- NO hashtags (added separately)
- Write caption directly"""

    result = call_gemini(prompt, max_tokens=500)

    if result and len(result.split()) >= 50:
        result = result.strip().replace('**', '').replace('*', '')
        print(f"✅ Caption AI ({len(result.split())} words)")
        return result, 'ai'

    print("⚠️ Caption fallback")
    return None, 'fallback'


# ==========================================
# 6. PIL TEXT OVERLAY
# ==========================================
def create_text_overlay(text, img_width=854, accent_color=(0, 200, 255)):
    font_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    font_path = next((p for p in font_paths if os.path.exists(p)), None)

    try:
        font       = ImageFont.truetype(font_path, 32) if font_path else ImageFont.load_default()
        font_small = ImageFont.truetype(font_path, 20) if font_path else ImageFont.load_default()
    except Exception:
        font = font_small = ImageFont.load_default()

    words, lines, current = text.split(), [], ""
    for word in words:
        test = f"{current} {word}".strip()
        if len(test) * 20 <= img_width - 60:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    lines = lines[:3]

    line_h = 45
    pad    = 15
    box_h  = len(lines) * line_h + pad * 2 + 38

    overlay = Image.new('RGBA', (img_width, box_h), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)

    for y in range(box_h):
        alpha = int(160 + 60 * (y / box_h))
        draw.line([(0, y), (img_width, y)], fill=(0, 0, 0, alpha))

    draw.rectangle([(0, 0), (img_width, 3)], fill=(*accent_color, 230))

    y_pos = pad
    for i, line in enumerate(lines):
        draw.text((42, y_pos + 2), line, font=font, fill=(0, 0, 0, 210))
        color = (*accent_color, 255) if i == 0 else (255, 255, 255, 255)
        draw.text((40, y_pos), line, font=font, fill=color)
        y_pos += line_h

    contact = "📧 rahulhaku52@gmail.com  |  📱 t.me/hacker_52"
    draw.rectangle([(0, box_h - 33), (img_width, box_h)], fill=(0, 0, 0, 230))
    draw.text((40, box_h - 26), contact, font=font_small, fill=(200, 200, 200, 255))

    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    overlay.save(tmp.name)
    print("✅ Text overlay created")
    return tmp.name


# ==========================================
# 7. VOICE GENERATOR
# ==========================================
async def _edge_generate(text, voice, path):
    await edge_tts.Communicate(text, voice).save(path)


def generate_voice(text, lang='en'):
    tmp = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)

    if lang == 'bn':
        voice_priority = [
            "bn-BD-NabanitaNeural",
            "bn-BD-PradeepNeural",
            "bn-IN-TanishaaNeural",
        ]
    elif lang == 'hi':
        voice_priority = [
            "hi-IN-SwaraNeural",
            "hi-IN-MadhurNeural",
        ]
    else:
        voice_priority = [
            "en-US-JennyNeural",
            "en-US-GuyNeural",
        ]

    for voice in voice_priority:
        try:
            asyncio.run(_edge_generate(text, voice, tmp.name))
            if os.path.exists(tmp.name) and os.path.getsize(tmp.name) > 1000:
                print(f"✅ Voice: {voice}")
                return tmp.name, voice
        except Exception as e:
            print(f"⚠️ edge-tts {voice}: {e}")

    try:
        from gtts import gTTS
        gtts_lang = 'bn' if lang == 'bn' else ('hi' if lang == 'hi' else 'en')
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save(tmp.name)
        print(f"✅ Voice: gTTS ({gtts_lang})")
        return tmp.name, f'gTTS-{gtts_lang}'
    except Exception as e:
        print(f"❌ All voice failed: {e}")

    return tmp.name, 'none'


def pick_voice_text(topic):
    lang = random.choices(
        ['bn', 'hi', 'en'],
        weights=[40, 30, 30]
    )[0]

    script, source = generate_voice_script_ai(lang, topic)
    return script, lang, source


# ==========================================
# 8. ✅ UPDATED PEXELS VIDEO DOWNLOADER
# ==========================================
def fetch_pexels_video(query):
    """
    ✅ Downloads SD quality video (5-10MB) from Pexels
    """
    if not PEXELS_API_KEY:
        print("⚠️ PEXELS_API_KEY not set")
        return None

    try:
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=landscape"
        
        r = requests.get(
            url,
            headers={"Authorization": PEXELS_API_KEY},
            timeout=20
        )

        if r.status_code != 200:
            print(f"⚠️ Pexels video API: {r.status_code}")
            return None

        data = r.json()
        videos = data.get("videos", [])

        if not videos:
            print(f"⚠️ No videos found for '{query}'")
            return None

        selected = random.choice(videos[:5])
        video_files = selected.get("video_files", [])

        # ✅ Prefer SD quality (800-1000px width) for smaller file size
        best_video = None
        for vf in video_files:
            width = vf.get("width", 0)
            if 800 <= width <= 1000:
                best_video = vf
                break
        
        # Fallback: any medium quality
        if not best_video:
            for vf in video_files:
                if vf.get("width", 0) >= 854:
                    best_video = vf
                    break

        # Last resort: first available
        if not best_video and video_files:
            best_video = video_files[0]

        if not best_video:
            print("⚠️ No video file found")
            return None

        video_url = best_video.get("link")
        
        print(f"⬇️ Downloading Pexels video ({best_video.get('width')}x{best_video.get('height')})...")

        vr = requests.get(video_url, timeout=90)

        if vr.status_code != 200:
            print(f"⚠️ Video download failed: {vr.status_code}")
            return None

        temp_video = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        
        with open(temp_video.name, "wb") as f:
            f.write(vr.content)

        file_size_mb = os.path.getsize(temp_video.name) / (1024 * 1024)
        print(f"✅ Pexels video downloaded: {file_size_mb:.1f}MB")
        
        return temp_video.name

    except Exception as e:
        print(f"❌ fetch_pexels_video error: {e}")
        return None


# ==========================================
# 9. ✅ UPDATED VIDEO CREATOR
# ==========================================
def create_video(background_video_path, voice_path, subtitle_text, theme_accent=(0, 200, 255)):
    """
    ✅ Creates compressed video (5-8MB) optimized for Facebook
    """
    output_path = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
    overlay_path = None

    try:
        audio_clip = AudioFileClip(voice_path)
        audio_dur = audio_clip.duration
        print(f"🎙️ Audio duration: {audio_dur:.1f}s")

        video_dur = max(audio_dur, MIN_DURATION)
        video_dur = min(video_dur, MAX_DURATION)
        print(f"🎬 Target video duration: {video_dur:.1f}s")

        bg_video = VideoFileClip(background_video_path)
        print(f"📹 Background video: {bg_video.duration:.1f}s")

        if bg_video.duration > video_dur:
            max_start = max(0, bg_video.duration - video_dur)
            start_time = random.uniform(0, max_start)
            bg_video = bg_video.subclip(start_time, start_time + video_dur)
            print(f"✂️ Video trimmed: {start_time:.1f}s to {start_time + video_dur:.1f}s")
        else:
            bg_video = bg_video.loop(duration=video_dur)
            print(f"🔁 Video looped to {video_dur:.1f}s")

        # ✅ Lower resolution = smaller file (854x480 is FB-friendly)
        bg_video = bg_video.resize((854, 480))

        overlay_path = create_text_overlay(subtitle_text, 854, theme_accent)
        
        subtitle_clip = (
            ImageClip(overlay_path)
            .set_duration(min(12, video_dur))
            .set_position(("center", "bottom"))
            .set_opacity(0.92)
        )

        logo_clip = _get_logo_clip(video_dur)

        clips = [bg_video, subtitle_clip]
        if logo_clip:
            clips.append(logo_clip)

        final = CompositeVideoClip(clips, size=(854, 480))
        final = final.set_audio(audio_clip)

        # ✅ Lower bitrate = smaller file
        final.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=24,              # Lower FPS
            preset="fast",
            bitrate="800k",      # Video bitrate 800kbps
            audio_bitrate="96k", # Audio bitrate 96kbps
            verbose=False,
            logger=None,
            threads=4
        )

        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ Video created: {file_size_mb:.1f}MB")
        
        return output_path

    except Exception as e:
        print(f"❌ create_video error: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        if overlay_path and os.path.exists(overlay_path):
            try:
                os.unlink(overlay_path)
            except Exception:
                pass


# ==========================================
# 10. LOGO CLIP
# ==========================================
def _get_logo_clip(video_dur):
    start_t = max(0, video_dur - 5)
    if os.path.exists(LOGO_PATH):
        try:
            return (
                ImageClip(LOGO_PATH)
                .resize(height=60)
                .set_position(('right', 'bottom'))
                .set_duration(5)
                .set_start(start_t)
                .set_opacity(0.88)
            )
        except Exception as e:
            print(f"⚠️ Logo clip: {e}")
    return None


# ==========================================
# 11. TRENDING HASHTAGS
# ==========================================
def fetch_trending_tags():
    return random.sample(TRENDING_TAGS, 3)


# ==========================================
# 12. UNICODE STYLES
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


# ==========================================
# 13. CAPTION GENERATOR
# ==========================================
def generate_caption(hook, image_text, topic):
    fixed    = random.sample(FIXED_HASHTAGS, 4)
    trending = fetch_trending_tags()
    tags     = " ".join(fixed + trending)

    ai_body, source = generate_caption_ai(hook, image_text, topic)

    d = "━" * 32

    if ai_body and source == 'ai':
        caption = (
            f"{d}\n"
            f"{hook}\n"
            f"🔥 {image_text}\n"
            f"{d}\n\n"
            f"{ai_body}\n\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"📧 {italic_unicode('Email')}: rahulhaku52@gmail.com\n"
            f"📱 {italic_unicode('Telegram')}: t.me/hacker_52\n"
            f"━━━━━━━━━━━━━━━━\n\n"
            f"{tags}"
        )
        print("✅ Caption: AI generated")
    else:
        caption = (
            f"{d}\n"
            f"{hook}\n"
            f"🔥 {image_text}\n"
            f"{d}\n\n"
            f"💡 Learn professional tech tips every day!\n"
            f"🚀 Build your skills with us.\n\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"📧 {italic_unicode('Email')}: rahulhaku52@gmail.com\n"
            f"📱 {italic_unicode('Telegram')}: t.me/hacker_52\n"
            f"━━━━━━━━━━━━━━━━\n\n"
            f"{tags}"
        )
        print("⚠️ Caption: Fallback used")

    return caption


# ==========================================
# 14. FACEBOOK UPLOAD
# ==========================================
def upload_to_facebook(video_path, title, description):
    if not PAGE_ID or not ACCESS_TOKEN:
        print("❌ Facebook credentials missing!")
        return {"error": "Missing credentials"}
    
    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"📦 Final video size: {file_size_mb:.1f}MB")
    
    try:
        with open(video_path, 'rb') as vf:
            resp = requests.post(
                f"https://graph-video.facebook.com/v18.0/{PAGE_ID}/videos",
                files={'source': vf},
                data={
                    'access_token': ACCESS_TOKEN,
                    'title': title[:80],
                    'description': description[:800],
                    'published': True
                },
                timeout=300
            )
        
        result = resp.json()
        
        if 'id' in result:
            video_id = result['id']
            print(f"✅ Uploaded! Video ID: {video_id}")
            print(f"🔗 URL: https://www.facebook.com/{video_id}")
        else:
            print(f"⚠️ Upload response: {result}")
        
        return result
    
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return {"error": str(e)}


# ==========================================
# 15. MAIN
# ==========================================
def main():
    print("=" * 60)
    print(f"🚀 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Pexels   : {'✅' if PEXELS_API_KEY   else '❌'}")
    print(f"🔑 Gemini   : {'✅' if GEMINI_API_KEY    else '❌'}")
    print(f"🔑 Facebook : {'✅' if PAGE_ID and ACCESS_TOKEN else '❌'}")
    print(f"🖼️  Logo     : {'✅' if os.path.exists(LOGO_PATH) else '⚠️'}")
    print(f"⏱️  Duration : {MIN_DURATION}-{MAX_DURATION}s")
    print("=" * 60)

    voice_path = video_path = bg_video_path = None

    try:
        topic = random.choice(TECH_TOPICS)
        print(f"\n📌 Topic: {topic}")

        hook, hook_source = generate_hook_ai(topic)
        print(f"🎣 Hook [{hook_source}]: {hook}")

        image_text, img_text_source = generate_image_text_ai(topic)
        print(f"🖼️  Text [{img_text_source}]: {image_text}")

        voice_text, lang, voice_source = pick_voice_text(topic)
        print(f"🎙️  Script [{voice_source}] ({lang}): {len(voice_text.split())} words")
        print(f"   Preview: {voice_text[:100]}...")

        video_keyword = random.choice(VIDEO_SEARCH_KEYWORDS)
        print(f"\n🎬 Searching Pexels video: '{video_keyword}'")
        
        bg_video_path = fetch_pexels_video(video_keyword)
        
        if not bg_video_path:
            print("⚠️ Video download failed, trying another keyword...")
            video_keyword = random.choice(VIDEO_SEARCH_KEYWORDS)
            bg_video_path = fetch_pexels_video(video_keyword)

        if not bg_video_path:
            print("❌ Could not download background video. Exiting.")
            return

        voice_path, voice_id = generate_voice(voice_text, lang)
        print(f"🎙️  Voice generated: {voice_id}")

        theme = random.choice(COLOR_THEMES)
        print(f"\n🎨 Theme: {theme['name']}")
        
        video_path = create_video(
            bg_video_path,
            voice_path,
            image_text,
            theme['accent']
        )

        if not video_path:
            print("❌ Video creation failed. Exiting.")
            return

        caption = generate_caption(hook, image_text, topic)
        print(f"\n📋 Caption preview:\n{caption[:250]}...\n")

        print("📤 Uploading to Facebook...")
        result = upload_to_facebook(
            video_path,
            f"{hook} — {image_text}",
            caption
        )
        print(f"📊 Upload result: {result}")

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        for label, path in [
            ("voice", voice_path),
            ("background video", bg_video_path),
            ("final video", video_path)
        ]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                    print(f"🧹 {label} cleaned")
                except Exception:
                    pass

    print("=" * 60)
    print(f"✅ Done: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
