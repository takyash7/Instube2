import streamlit as st
import yt_dlp
import instaloader
import os
import shutil
import re

# -- Folder setup
os.makedirs("downloads", exist_ok=True)
os.makedirs("temp", exist_ok=True)

# -- Streamlit Page Config
st.set_page_config(page_title="📥 InstaTube Downloader", page_icon="📥")
st.title("📥 YouTube & Instagram Reels Downloader")

# -- User Input
url = st.text_input("🔗 Paste YouTube or Instagram Reel URL:")

# -- Proxy (Instagram)
proxy_url = "http://45.94.47.66:8080"

# -- Extract shortcode safely
def extract_shortcode(insta_url):
    match = re.search(r"reel/([A-Za-z0-9_-]+)", insta_url)
    return match.group(1) if match else None

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
                    'format': 'best[ext=mp4]/best',  # No ffmpeg needed
                    'progress_hooks': [hook]
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get('title', 'video')
                    temp_file = ydl.prepare_filename(info).replace(".webm", ".mp4").replace(".mkv", ".mp4")
                    final_path = os.path.join("downloads", os.path.basename(temp_file))
                    shutil.move(temp_file, final_path)
                    st.success(f"🎉 Downloaded: {title}")
                    st.info(f"📂 Saved to: downloads/{os.path.basename(final_path)}")

            # ------------------- INSTAGRAM SECTION (NO LOGIN) -------------------
            elif "instagram.com/reel" in url:
                shortcode = extract_shortcode(url)
                if not shortcode:
                    st.error("❌ Invalid Instagram URL or shortcode could not be extracted.")
                    st.stop()

                st.info("📥 Downloading Reel anonymously (no login)...")
                L = instaloader.Instaloader()
                L.context._default_http_proxy = proxy_url

                try:
                    post = instaloader.Post.from_shortcode(L.context, shortcode)
                    L.download_post(post, target="downloads")
                    st.success("✅ Instagram Reel downloaded successfully!")

                except instaloader.exceptions.QueryReturnedNotFoundException:
                    st.error("❌ Reel not found or removed.")
                except instaloader.exceptions.BadResponseException:
                    st.warning("⏳ Instagram is blocking access. Wait or change proxy.")
                except Exception as e:
                    st.error(f"❌ Unexpected Error: {e}")

            else:
                st.warning("⚠️ Please enter a valid YouTube or Instagram Reel URL.")

        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.warning("⚠️ Please enter a URL to start download.")
