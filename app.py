import streamlit as st
import yt_dlp
import instaloader
import os
import shutil
import re
import random
import platform
import string

# 🪜 Sanitize filename
def clean_filename(name):
    return ''.join(c for c in name if c.isalnum() or c in (' ', '.', '_')).strip()

# 🔁 Detect platform for download path
if platform.system() == "Linux" and os.path.exists("/sdcard/Download"):
    DOWNLOAD_DIR = "/sdcard/Download/Instube"
else:
    DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")

try:
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
except Exception:
    DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

os.makedirs("temp", exist_ok=True)

# 🌐 Proxy list
proxy_list = [
    "http://194.67.213.110:8080",
    "http://138.199.14.68:8080",
    "http://45.94.47.66:8080",
    "http://195.154.255.194:80",
    "http://94.237.3.45:8080",
    "http://64.225.8.121:9988",
    "http://134.209.29.120:3128",
    "http://209.38.243.174:3128",
    "http://51.91.144.39:80",
    "http://51.158.154.173:3128",
    "http://51.75.147.42:3128",
    "http://167.172.238.168:3128",
    "http://103.155.197.38:3125",
    "http://103.86.49.182:3128",
    "http://181.129.183.19:53281"
]

proxy_url = random.choice(proxy_list)

# 🌐 Streamlit UI
st.set_page_config(page_title="📅 InstaTube Downloader", page_icon="📅")
st.title("📅 YouTube & Instagram Reels Downloader")

url = st.text_input("🔗 Paste YouTube or Instagram Reel URL:")

# Extract Instagram shortcode from URL
def extract_shortcode(insta_url):
    match = re.search(r"reel/([A-Za-z0-9_-]+)", insta_url)
    return match.group(1) if match else None

if st.button("Download"):
    if url:
        try:
            # ▶️ YOUTUBE
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
                        status.info(f"📅 Downloading: {percent*100:.1f}% at {speed} | ETA: {eta}s")
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
                    title = clean_filename(info.get('title', 'video'))
                    temp_file = ydl.prepare_filename(info).replace(".webm", ".mp4").replace(".mkv", ".mp4")
                    temp_file_clean = os.path.join("temp", f"{title}.mp4")
                    os.rename(temp_file, temp_file_clean)
                    final_path = os.path.join(DOWNLOAD_DIR, os.path.basename(temp_file_clean))
                    shutil.move(temp_file_clean, final_path)

                    st.success(f"🎉 Downloaded: {title}")
                    st.info(f"📂 Saved to: {final_path}")

                    with open(final_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Click to Download",
                            data=file,
                            file_name=os.path.basename(final_path),
                            mime="video/mp4"
                        )

            # ▶️ INSTAGRAM using yt-dlp (same logic)
            elif "instagram.com/reel" in url:
                st.info(f"📅 Using proxy: {proxy_url}")
                status = st.empty()
                progress = st.progress(0.0)

                def insta_hook(d):
                    if d['status'] == 'downloading':
                        percent = float(d.get('_percent_str', '0%').replace('%', '').strip()) / 100
                        speed = d.get('_speed_str', '0 KB/s')
                        eta = d.get('eta', '?')
                        status.info(f"📥 Downloading: {percent*100:.1f}% at {speed} | ETA: {eta}s")
                        progress.progress(min(percent, 1.0))
                    elif d['status'] == 'finished':
                        status.success("✅ Instagram Reel download complete.")

                ydl_opts = {
                    'outtmpl': 'temp/insta_%(title)s.%(ext)s',
                    'progress_hooks': [insta_hook],
                    'format': 'best[ext=mp4]/best',
                    'proxy': proxy_url
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = clean_filename(info.get('title', 'insta_reel'))
                    temp_file = ydl.prepare_filename(info).replace(".webm", ".mp4").replace(".mkv", ".mp4")
                    temp_file_clean = os.path.join("temp", f"{title}.mp4")
                    os.rename(temp_file, temp_file_clean)
                    final_path = os.path.join(DOWNLOAD_DIR, os.path.basename(temp_file_clean))
                    shutil.move(temp_file_clean, final_path)

                    st.success(f"🎉 Downloaded: {title}")
                    st.info(f"📂 Saved to: {final_path}")

                    with open(final_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Click to Download",
                            data=file,
                            file_name=os.path.basename(final_path),
                            mime="video/mp4"
                        )

            else:
                st.warning("⚠️ Please enter a valid YouTube or Instagram Reel URL.")

        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.warning("⚠️ Please enter a URL to start download.")

# 👨‍💼 Developer Info
st.markdown("<h2 style='color:#90EE90;'>ℹ️ Developer Info</h2>", unsafe_allow_html=True)
st.markdown("👨‍💼 Created by: [Yash Tak](https://www.linkedin.com/in/yash-tak7)")
st.markdown("🤙 GitHub: [takyash7](https://www.github.com/takyash7)")
st.markdown("📧 Contact: [yashtak@gmail.com](mailto:yashtak@gmail.com)")
