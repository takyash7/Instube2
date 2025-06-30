import streamlit as st
import yt_dlp
import instaloader
import os
import shutil
import re
import random
import platform
import string

# 🧼 Sanitize filename
def clean_filename(name):
    return ''.join(c for c in name if c.isalnum() or c in (' ', '.', '_')).strip()

# 📁 Detect Android or PC
if platform.system() == "Linux" and os.path.exists("/sdcard/Download"):
    DOWNLOAD_DIR = "/sdcard/Download/Instube"
    STATUS_BACKUP_DIR = "/sdcard/Download/MyStatuses"
else:
    DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
    STATUS_BACKUP_DIR = os.path.join(os.getcwd(), "MyStatuses")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs("temp", exist_ok=True)
os.makedirs(STATUS_BACKUP_DIR, exist_ok=True)

# 🌐 Proxy list for Instagram
proxy_list = [
    "http://194.67.213.110:8080", "http://138.199.14.68:8080", "http://45.94.47.66:8080",
    "http://195.154.255.194:80", "http://94.237.3.45:8080", "http://64.225.8.121:9988",
    "http://134.209.29.120:3128", "http://209.38.243.174:3128", "http://51.91.144.39:80",
    "http://51.158.154.173:3128", "http://51.75.147.42:3128", "http://167.172.238.168:3128",
    "http://103.155.197.38:3125", "http://103.86.49.182:3128", "http://181.129.183.19:53281"
]
proxy_url = random.choice(proxy_list)

# 🌐 Streamlit Config
st.set_page_config(page_title="📥 InstaTube & Status Downloader", page_icon="📥")
st.title("📥 InstaTube & WhatsApp Status Downloader")

# Tabs for separate sections
tab1, tab2, tab3 = st.tabs(["🎬 YouTube", "📸 Instagram", "🟢 WhatsApp Status"])

# ---------------------- 🎬 YOUTUBE ----------------------
with tab1:
    st.subheader("🎬 YouTube Video Downloader")
    url = st.text_input("🔗 Paste YouTube URL:", key="yt_url")

    if st.button("Download YouTube Video"):
        if url:
            try:
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
            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.warning("⚠️ Please enter a valid YouTube URL.")

# ---------------------- 📸 INSTAGRAM ----------------------
with tab2:
    st.subheader("📸 Instagram Reels Downloader")
    insta_url = st.text_input("🔗 Paste Instagram Reel URL:", key="insta_url")

    def extract_shortcode(insta_url):
        match = re.search(r"reel/([A-Za-z0-9_-]+)", insta_url)
        return match.group(1) if match else None

    if st.button("Download Instagram Reel"):
        if insta_url:
            shortcode = extract_shortcode(insta_url)
            if not shortcode:
                st.error("❌ Invalid Instagram URL or shortcode could not be extracted.")
            else:
                st.info(f"📥 Using proxy: {proxy_url}")
                L = instaloader.Instaloader()
                L.context._default_http_proxy = proxy_url

                try:
                    post = instaloader.Post.from_shortcode(L.context, shortcode)
                    L.download_post(post, target=DOWNLOAD_DIR)
                    st.success("✅ Instagram Reel downloaded successfully!")

                    video_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.mp4')]
                    video_files.sort(key=lambda f: os.path.getmtime(os.path.join(DOWNLOAD_DIR, f)), reverse=True)

                    if video_files:
                        latest_video = video_files[0]
                        final_path = os.path.join(DOWNLOAD_DIR, latest_video)
                        st.info(f"📂 Saved to: {final_path}")

                        with open(final_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Click to Download",
                                data=file,
                                file_name=latest_video,
                                mime="video/mp4"
                            )
                    else:
                        st.warning("⚠️ Downloaded reel not found.")

                except instaloader.exceptions.QueryReturnedNotFoundException:
                    st.error("❌ Reel not found or removed.")
                except instaloader.exceptions.BadResponseException:
                    st.warning("⏳ Instagram is blocking access. Try a different proxy or wait.")
                except Exception as e:
                    st.error(f"❌ Unexpected Error: {e}")
        else:
            st.warning("⚠️ Please enter a valid Instagram Reel URL.")

# ---------------------- 🟢 WHATSAPP STATUS ----------------------
with tab3:
    st.subheader("🟢 WhatsApp Status Downloader")
    st.markdown("📁 Please paste viewed WhatsApp status images/videos to `/sdcard/Download/MyStatuses/` manually.")

    if os.path.exists(STATUS_BACKUP_DIR):
        status_files = [f for f in os.listdir(STATUS_BACKUP_DIR) if f.endswith(('.jpg', '.mp4'))]
        if status_files:
            selected_file = st.selectbox("📂 Select a status to preview & download", status_files)
            file_path = os.path.join(STATUS_BACKUP_DIR, selected_file)

            with open(file_path, "rb") as f:
                if selected_file.endswith(".mp4"):
                    st.video(f)
                else:
                    st.image(f)

            with open(file_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download This Status",
                    data=f,
                    file_name=selected_file,
                    mime="video/mp4" if selected_file.endswith(".mp4") else "image/jpeg"
                )
        else:
            st.warning("⚠️ No files found in /Download/MyStatuses/. Please copy viewed statuses there manually.")
    else:
        st.error("❌ Folder /Download/MyStatuses/ not found. Create it and paste statuses there.")

# ℹ️ Developer Info
st.markdown("---")
st.markdown("<h2 style='color:#90EE90;'>ℹ️ Developer Info</h2>", unsafe_allow_html=True)
st.markdown("👨‍💻 Created by: [Yash Tak](https://www.linkedin.com/in/yash-tak7)")
st.markdown("🐙 GitHub: [takyash7](https://www.github.com/takyash7)")
st.markdown("📧 Contact: [yashtak@gmail.com](mailto:yashtak@gmail.com)")
