import os
import requests
import random
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip
import tempfile

# ========== ফেসবুক কনফিগ ==========
PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID')
ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN')

if not PAGE_ID or not ACCESS_TOKEN:
    print("❌ FACEBOOK_PAGE_ID or FACEBOOK_ACCESS_TOKEN missing!")
    exit(1)

# ========== প্রমোশনাল টেক্সট ==========
TEXTS = [
    "ওয়েবসাইট বানাই প্রিমিয়াম কোয়ালিটিতে\nকম খরচে, ফাস্ট ডেলিভারি\nযোগাযোগ: t.me/hacker_52",
    "Android ও iOS অ্যাপ ডেভেলপমেন্ট\nশুরু থেকে শেষ পর্যন্ত সম্পূর্ণ সাপোর্ট\nযোগাযোগ: t.me/hacker_52",
    "ফুল স্ট্যাক ওয়েব ডেভেলপমেন্ট\nReact, Node, Python\nযোগাযোগ: t.me/hacker_52"
]

# ==========================================
# ১. ইমেজ জেনারেট
# ==========================================
def generate_image(text):
    width, height = 1200, 628
    img = Image.new('RGB', (width, height), color=(10, 20, 40))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 50)
    except:
        font = ImageFont.load_default()
    
    y = 150
    for line in text.split('\n'):
        draw.text((100, y), line, fill=(255, 255, 255), font=font)
        y += 80
    
    temp_img = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_img.name)
    return temp_img.name

# ==========================================
# ২. ভয়েস জেনারেট
# ==========================================
def generate_voice(text):
    temp_audio = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
    tts = gTTS(text=text.replace('\n', ' '), lang='bn')
    tts.save(temp_audio.name)
    return temp_audio.name

# ==========================================
# ৩. ভিডিও তৈরি
# ==========================================
def create_video(image_path, voice_path, duration=12):
    output_path = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
    
    clip = ImageClip(image_path, duration=duration)
    voice_audio = AudioFileClip(voice_path)
    final_clip = clip.set_audio(voice_audio)
    final_clip.write_videofile(output_path, fps=24, verbose=False, logger=None)
    
    return output_path

# ==========================================
# ৪. ফেসবুকে আপলোড
# ==========================================
def upload_to_facebook(video_path, caption):
    url = f"https://graph.facebook.com/{PAGE_ID}/videos"
    files = {'source': open(video_path, 'rb')}
    data = {
        'access_token': ACCESS_TOKEN,
        'title': caption[:100],
        'description': caption
    }
    resp = requests.post(url, files=files, data=data)
    return resp.json()

# ==========================================
# ৫. মেইন
# ==========================================
def main():
    print("🚀 Starting Auto Video Poster...")
    
    caption = random.choice(TEXTS) + "\n🔗 t.me/hacker_52"
    print(f"📝 Caption: {caption}")
    
    img_path = generate_image(caption)
    print("✅ Image generated")
    
    voice_path = generate_voice(caption)
    print("✅ Voice generated")
    
    video_path = create_video(img_path, voice_path)
    print("✅ Video generated")
    
    result = upload_to_facebook(video_path, caption)
    print(f"📤 Upload result: {result}")
    
    os.unlink(img_path)
    os.unlink(voice_path)
    os.unlink(video_path)
    print("🧹 Cleanup done")

if __name__ == "__main__":
    main()
