import os
import subprocess
import yt_dlp
import whisper
import re
import json
import requests

# =========================
# CONFIGURAÇÕES
# =========================
VIDEO_URL = "https://www.youtube.com/watch?v=mjpOUbIDs18" # ESCOLHA O SEU VIDEO LONGO
OUTPUT_DIR = "videos"
BLOCK_DURATION = 600 #
OLLAMA_MODEL = "llama3:8b"  # Ex: llama3:70b ou mistral
OLLAMA_URL = "http://localhost:11434/api/generate"
PLATFORMS = ["shorts"]
MIN_DURATION = 45
MAX_DURATION = 300

# =========================
# UTILITÁRIAS
# =========================
def slugify(text):
    return re.sub(r'[^\w\s-]', '', text.lower()).strip().replace(' ', '_')[:50]

# =========================
# CRIA DIRETÓRIO DO VÍDEO
# =========================
print("📁 Verificando diretório do vídeo...")
ydl_opts_info = {'quiet': True, 'skip_download': True}
with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
    info = ydl.extract_info(VIDEO_URL, download=False)
    video_title = re.sub(r'[\\/*?:"<>|]', "_", info.get("title", "video")).replace(" ", "_")
    channel_name = info.get("uploader", "CanalDesconhecido")
    video_folder = os.path.join(OUTPUT_DIR, video_title)
    os.makedirs(video_folder, exist_ok=True)
    video_path = os.path.join(video_folder, f"{video_title}.mp4")
    transcript_path = os.path.join(video_folder, "transcript.json")

# =========================
# 1. BAIXA O VÍDEO
# =========================
if os.path.exists(video_path):
    print("✅ Vídeo já existe. Pulando download.")
else:
    print("📥 Baixando vídeo do YouTube...")
    ydl_opts = {'outtmpl': video_path, 'format': 'mp4/bestvideo+bestaudio'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([VIDEO_URL])

# =========================
# 2. TRANSCRIÇÃO COM WHISPER
# =========================
if os.path.exists(transcript_path):
    print("✅ Transcrição já existe. Carregando...")
    with open(transcript_path, "r", encoding="utf-8") as f:
        result = json.load(f)
else:
    print("🧠 Transcrevendo com Whisper...")
    model = whisper.load_model("base")
    result = model.transcribe(video_path, verbose=False)
    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

segments = result["segments"]
full_transcript = " ".join([s["text"] for s in segments])

# =========================
# 3. ANALISA COM OLLAMA (mudança de assunto)
# =========================
print("🧠 Solicitando sugestões de cortes com base em mudança de assunto...")

prompt = f"""
You are a professional video editor specializing in viral short content for social media. Your task is to split the transcript of a long video into multiple short clips based on **topic changes**, such as questions, answers, stories, or explanations.

Requirements:
- Each clip must have a "start" and "end" time in seconds.
- Each clip must be at least {MIN_DURATION} seconds and at most {MAX_DURATION} seconds.
- All clips must be sequential and **cover the entire video** without gaps or overlaps.
- Each clip must have a descriptive title starting with its number (e.g., "1 The reason behind...").
- Use clear, concise, lowercase titles without special characters.
- Response must be a **pure JSON array**, no comments or text outside the JSON.

Example format:
[
  {{
    "start": 0,
    "end": 58,
    "description": "1 Why he left his job",
    "platform": "shorts"
  }},
  ...
]

Transcript:
\"\"\"{full_transcript}\"\"\"
"""

cut_suggestions = []
used_titles = set()

try:
    response = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    })

    if response.status_code == 200:
        output_raw = response.json()["response"]

        try:
            json_text = re.search(r'\[\s*{.*?}\s*]', output_raw, re.DOTALL).group()
            parsed = json.loads(json_text)
        except Exception:
            print("⚠️ Nenhum JSON válido encontrado na resposta do modelo.")
            print("Resposta bruta:", output_raw)
            parsed = []

        for p in parsed:
            try:
                start = float(p["start"])
                end = float(p["end"])
                desc = p.get("description", "No title").strip()
                platform = p.get("platform", "shorts").lower()

                duration = end - start
                if platform not in PLATFORMS or not (MIN_DURATION <= duration <= MAX_DURATION):
                    continue

                title_key = slugify(desc)
                if title_key in used_titles:
                    continue

                used_titles.add(title_key)
                cut_suggestions.append((start, end, desc, platform))
            except Exception as inner:
                print("⚠️ Erro ao processar corte:", inner)

        if not cut_suggestions:
            print("⚠️ Nenhum corte válido encontrado. Verifique o modelo ou o prompt.")
        else:
            print(f"✅ {len(cut_suggestions)} cortes gerados com sucesso.")
    else:
        print("❌ Erro na requisição Ollama:", response.text)

except Exception as e:
    print("❌ Erro geral:", e)


# =========================
# 4. GERA OS CORTES COM FFMPEG + DESCRIÇÕES
# =========================

print(f"🎬 Gerando {len(cut_suggestions)} cortes e descrições...")

for i, (start, end, desc, platform) in enumerate(cut_suggestions):
    safe_title = slugify(desc)
    duration = end - start
    numbered_title = f"{i+1} - {desc.strip().lower()}"
    output_video_path = os.path.join(video_folder, f"{platform}-{safe_title}.mp4")
    output_desc_path = os.path.join(video_folder, f"{platform}-{safe_title}.txt")

    print(f"🎞️ {platform.upper()} — {numbered_title} ({start:.1f}s → {end:.1f}s)")

    # Criação do vídeo
    subprocess.run([
        "ffmpeg", "-ss", str(start), "-i", video_path, "-t", str(duration),
        "-c", "copy", output_video_path
    ], check=True)

    # Criação da descrição com título no topo
    description_text = f"{numbered_title}\n{desc.strip()}\n\n📌 Extraído do canal: {channel_name}"
    with open(output_desc_path, "w", encoding="utf-8") as f:
        f.write(description_text)

print("✅ Todos os cortes e descrições foram gerados com sucesso!")
