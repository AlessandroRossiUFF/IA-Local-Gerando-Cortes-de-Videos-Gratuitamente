import os
import re
import yt_dlp

# =========================
# CONFIGURAÇÃO EXEMPLO
# =========================
VIDEO_URL = "https://www.youtube.com/watch?v=vQ_AHyUdur8"
OUTPUT_DIR = "videos"

# =========================
# EXTRAI INFORMAÇÕES DO VÍDEO
# =========================
print("📁 Coletando informações do vídeo...")

ydl_opts_info = {'quiet': True, 'skip_download': True}
with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
    info = ydl.extract_info(VIDEO_URL, download=False)
    video_title = re.sub(r'[\\/*?:"<>|]', "_", info.get("title", "video")).replace(" ", "_")
    video_folder = os.path.join(OUTPUT_DIR, video_title)
    os.makedirs(video_folder, exist_ok=True)
    video_path = os.path.join(video_folder, f"{video_title}.mp4")

# =========================
# BAIXA O VÍDEO SE NECESSÁRIO
# =========================
if os.path.exists(video_path):
    print("✅ Vídeo já existe. Pulando download.")
else:
    print("📥 Baixando vídeo...")
    ydl_opts = {
        'outtmpl': video_path,
        'format': 'mp4/bestvideo+bestaudio'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([VIDEO_URL])

print("✅ Download concluído:", video_path)
