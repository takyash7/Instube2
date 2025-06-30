import streamlit as st
import yt_dlp
import instaloader
import os
import shutil
import re
import random

# 📁 Download path (Android visible)
DOWNLOAD_DIR = "/sdcard/Download/Instube"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs("temp", exist_ok=True)

# 🌐 Proxy list (rotate for Instagram)
proxy_list = [
    "http://194.67.213.110:8080",
    "http://138.199.14.68:8080",
    "http://45.94.47.66:8080"
]
proxy_url = random.choice(proxy_list)

# 🧠 Streamlit Page
st.set_page_config(page_title="📥 InstaTube Downloader", page_icon="📥")
st.title("📥 YouTube & Instagram Reels Downloader")

# 🔗 Input URL
url = st.text_input("🔗 Paste YouTube or Instagram Reel URL:")

# 🔎 Extract Instagram shortcode
def extract_shortcode(insta_url):
    match = re.search(r"reel/([A-Za-z0-9_-]+)", insta_url)
    return match.group(1) if match else None

# ▶️ Download Logic
if st.button("Download"):
    if url:
        try:
            # ------------------- YOUTUBE SECTION -------------------
            if "youtube.com" in url or "youtu.be" in url:
                if "shorts" in url or "youtu.be" in url:
                    video_id = url.split("/")[-1].split("?")[0]
                    url = f"https://www.youtube.com/watch?v={video_id}"
                if "watch?v=" in url:
                    url = url.split("&")[0].split("?si=")[0]

                status = st.empty()
                progress = st.progress(0.0)

                def hook(d):
                    if d['status'] == 'downloading':
                        percent = float(d.get('_percent_str', '0%').replace('%', '').strip()) / 100
                        speed = d.get('_speed_str', '0 KB/s')
                        eta = d.get('eta', '?')
                        status.info(f"📥 Downloading: {percent*100:.1f}% at {speed} | ETA: {eta}s")
                        progress.progress(min(percent, 1.0))
                    elif d['status'] == 'finished':
                        status.success("✅ YouTube download complete.")

                ydl_opts = {
                    'outtmpl': 'temp/%(title)s.%(ext)s',
                    'format': 'best[ext=mp4]/best',
                    'progress_hooks': [hook]
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get('title', 'video')
                    temp_file = ydl.prepare_filename(info).replace(".webm", ".mp4").replace(".mkv", ".mp4")
                    final_path = os.path.join(DOWNLOAD_DIR, os.path.basename(temp_file))
                    shutil.move(temp_file, final_path)
                    st.success(f"🎉 Downloaded: {title}")
                    st.info(f"📂 Saved to: Download/Instube")

            # ------------------- INSTAGRAM SECTION -------------------
            elif "instagram.com/reel" in url:
                shortcode = extract_shortcode(url)
st.markdown("<h2 style='color:	#90EE90;'>ℹ️ Deveper Info.</h2>", unsafe_allow_html=True)
st.markdown("👨‍💻 Created by: [Yash Tak](https://www.linkedin.com/in/yash-tak7)")
st.markdown("🐙 GitHub: [takyash7](https://www.github.com/takyash7)")
st.markdown("📧 Contact via mail: [yashtak@gmail.com](mailto:yashtak@gmail.com)")