import os
import requests
import random
from moviepy.editor import ImageClip, AudioFileClip, VideoFileClip, CompositeVideoClip, TextClip, CompositeVideoClip
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import io

# ==========================================
# ১. কনফিগারেশন (API Keys)
# ==========================================
PEXELS_API_KEY = "তোমার_Pexels_API_Key_দাও"  # Pexels কী বসাও
PIXABAY_API_KEY = "তোমার_Pixabay_API_Key_দাও"  # Pixabay কী বসাও

# ==========================================
# ২. পেক্সেলস (Pexels) থেকে ভিডিও সার্চ
# ==========================================
def search_pexels_video(query, per_page=5):
    """Pexels API থেকে ভিডিও সার্চ করে"""
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page, "orientation": "landscape"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('videos'):
            # শুধু HD বা SD কোয়ালিটির ভিডিও ফিল্টার করা
            for video in data['videos']:
                for file in video.get('video_files', []):
                    if file.get('quality') in ['hd', 'sd'] and file.get('width') >= 1280:
                        return file.get('link')  # প্রথম ভালো ভিডিওর লিংক রিটার্ন
        return None
    except Exception as e:
        print(f"⚠️ Pexels Error: {e}")
        return None

# ==========================================
# ৩. পিক্সাবে (Pixabay) থেকে ভিডিও সার্চ
# ==========================================
def search_pixabay_video(query):
    """Pixabay API থেকে ভিডিও সার্চ করে (Pexels না পেলে ব্যাকআপ)"""
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": 5,
        "orientation": "horizontal"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('hits'):
            for hit in data['hits']:
                if hit.get('videos'):
                    # সবথেকে ভালো কোয়ালিটির ভিডিও বেছে নেওয়া
                    videos = hit['videos']
                    for quality in ['large', 'medium', 'small']:
                        if quality in videos:
                            return videos[quality]['url']
        return None
    except Exception as e:
        print(f"⚠️ Pixabay Error: {e}")
        return None

# ==========================================
# ৪. ভিডিও ডাউনলোড
# ==========================================
def download_video(url, filename="temp_video.mp4"):
    """URL থেকে ভিডিও ডাউনলোড করে"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return filename
    except Exception as e:
        print(f"⚠️ Download Error: {e}")
        return None

# ==========================================
# ৫. অডিও (ভয়েস) তৈরি
# ==========================================
def create_voiceover(text, filename="voiceover.mp3"):
    """টেক্সট থেকে ভয়েস ওভার তৈরি করে"""
    try:
        tts = gTTS(text=text, lang='bn', slow=False)
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"⚠️ TTS Error: {e}")
        return None

# ==========================================
# ৬. ভিডিও এডিটিং (ইমেজ + অডিও + টেক্সট)
# ==========================================
def create_final_video(video_path, audio_path, output_path="final_video.mp4", 
                        text="ওয়েবসাইট বানাই কম দামে", duration=None):
    """
    ডাউনলোড করা ভিডিওর সাথে অডিও ও টেক্সট ওভারলে যুক্ত করে
    """
    try:
        # ভিডিও লোড
        video = VideoFileClip(video_path)
        
        # অডিও লোড
        audio = AudioFileClip(audio_path)
        
        # অডিওর দৈর্ঘ্য অনুযায়ী ভিডিও ক্রপ বা লুপ
        if duration is None:
            duration = audio.duration
        
        if video.duration < duration:
            # ভিডিও লুপ করা
            video = video.loop(duration=duration)
        else:
            video = video.subclip(0, duration)
        
        # অডিও সেট করা
        final = video.set_audio(audio)
        
        # টেক্সট ওভারলে যোগ করা (নিচের অংশে)
        txt_clip = TextClip(text, fontsize=40, color='white', font='Arial', 
                            stroke_color='black', stroke_width=2)
        txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(duration)
        
        # সবকিছু একত্রিত করা
        final = CompositeVideoClip([final, txt_clip])
        
        # আউটপুট সেভ
        final.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
        return output_path
        
    except Exception as e:
        print(f"⚠️ Video Editing Error: {e}")
        return None

# ==========================================
# ৭. মেইন ফাংশন (পুরো প্রক্রিয়া)
# ==========================================
def main():
    search_query = "web development"
    voice_text = "ওয়েবসাইট বানাই কম দামে। যোগাযোগ: t.me/hacker_52"
    
    print("🚀 শুরু হচ্ছে...")
    
    # ১. Pexels থেকে ভিডিও খোঁজা
    print("📹 Pexels এ খুঁজছি...")
    video_url = search_pexels_video(search_query)
    
    # ২. Pexels না পেলে Pixabay ব্যবহার
    if not video_url:
        print("📹 Pexels এ না পেয়ে Pixabay এ খুঁজছি...")
        video_url = search_pixabay_video(search_query)
    
    if not video_url:
        print("❌ কোনো ভিডিও পাওয়া যায়নি!")
        return
    
    print(f"✅ ভিডিও পাওয়া গেছে: {video_url[:50]}...")
    
    # ৩. ভিডিও ডাউনলোড
    video_file = download_video(video_url)
    if not video_file:
        print("❌ ভিডিও ডাউনলোড ব্যর্থ!")
        return
    
    # ৪. ভয়েস তৈরি
    audio_file = create_voiceover(voice_text)
    if not audio_file:
        print("❌ ভয়েস তৈরি ব্যর্থ!")
        return
    
    # ৫. ফাইনাল ভিডিও তৈরি
    final_video = create_final_video(video_file, audio_file, 
                                     output_path="web_promo_video.mp4",
                                     text=voice_text)
    
    if final_video:
        print(f"🎉 সফল! ভিডিও তৈরি হয়েছে: {final_video}")
    else:
        print("❌ ভিডিও তৈরি ব্যর্থ!")
    
    # ৬. টেম্প ফাইল মুছে ফেলা (ঐচ্ছিক)
    # os.remove(video_file)
    # os.remove(audio_file)

if __name__ == "__main__":
    main()
