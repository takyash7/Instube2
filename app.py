import streamlit as st
import yt_dlp
import instaloader
import os
import shutil
import re
import random
import platform

# 🔁 Detect platform
if platform.system() == "Linux" and os.path.exists("/sdcard/Download"):
    DOWNLOAD_DIR = "/sdcard/Download/Instube"
else:
    DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs("temp", exist_ok=True)

# 🌐 Proxy list for Instagram
proxy_list = [
    "http://194.67.213.110:8080",
    "http://138.199.14.68:8080",
    "http://45.94.47.66:8080"
]
proxy_url = random.choice(proxy_list)

# 🌐 Streamlit UI
st.set_page_config(page_title="📥 InstaTube Downloader", page_icon="📥")
st.title("📥 YouTube & Instagram Reels Downloader")

# 🔗 Input
url = st.text_input("🔗 Paste YouTube or Instagram Reel URL:")

# 🔍 Shortcode extractor for Instagram
def extract_shortcode(insta_url):
    match = re.search(r"reel/([A-Za-z0-9_-]+)", insta_url)
    return match.group(1) if match else None

# ▶️ Download logic
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
                    st.info(f"📂 Saved to: {final_path}")

            # ------------------- INSTAGRAM SECTION -------------------
            elif "instagram.com/reel" in url:
                shortcode = extract_shortcode(url)
                if not shortcode:
                    st.error("❌ Invalid Instagram URL or shortcode could not be extracted.")
                    st.stop()

                st.info(f"📥 Using proxy: {proxy_url}")
                L = instaloader.Instaloader()
                L.context._default_http_proxy = proxy_url

                try:
                    post = instaloader.Post.from_shortcode(L.context, shortcode)
                    L.download_post(post, target=DOWNLOAD_DIR)
                    st.success("✅ Instagram Reel downloaded successfully!")
                    st.info(f"📂 Saved to: {DOWNLOAD_DIR}")

                except instaloader.exceptions.QueryReturnedNotFoundException:
                    st.error("❌ Reel not found or removed.")
                except instaloader.exceptions.BadResponseException:
                    st.warning("⏳ Instagram is blocking access. Try a different proxy or wait.")
                except Exception as e:
                    st.error(f"❌ Unexpected Error: {e}")

            else:
                st.warning("⚠️ Please enter a valid YouTube or Instagram Reel URL.")

        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.warning("⚠️ Please enter a URL to start download.")

# 👨‍💻 Developer Info
st.markdown("<h2 style='color:#90EE90;'>ℹ️ Developer Info</h2>", unsafe_allow_html=True)
st.markdown("👨‍💻 Created by: [Yash Tak](https://www.linkedin.com/in/yash-tak7)")
st.markdown("🐙 GitHub: [takyash7](https://www.github.com/takyash7)")
st.markdown("📧 Contact: [yashtak@gmail.com](mailto:yashtak@gmail.com)")
