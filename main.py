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
# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyC_TCYKvAx6qkxIXjc_Y5weu4JCDvXs6wo"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
VIDEO_URL = "https://www.youtube.com/watch?v=m7H3TQ6eq5g"  # ESCOLHA O SEU VIDEO LONGO
OUTPUT_DIR = "videos"
BLOCK_DURATION = 600
PLATFORMS = ["shorts"]
MIN_DURATION = 30
MAX_DURATION = 300

PROMPT_CORTES = f"""
        "Olá! Tenho um canal de cortes no YouTube focado em análise política com viés marxista. Meu objetivo é criar Reels curtos (até 60 segundos) que sejam impactantes e com alto potencial de viralização, para atrair um público interessado em crítica social, economia política e teoria marxista.

        Por favor, analise a transcrição de podcast abaixo e me sugira trechos para cortes que:

        Expliquem ou exemplifiquem conceitos marxistas (luta de classes, mais-valia, alienação, materialismo histórico, ideologia, etc.) de forma concisa.
        Critiquem o capitalismo ou sistemas neoliberais sob uma perspectiva marxista.
        Analise eventos políticos ou sociais atuais usando a lente da teoria marxista.
        Desmascarem narrativas dominantes ou "senso comum" que sirvam aos interesses do capital.
        Contenham frases de efeito, argumentos contundentes ou revelações que possam gerar debate e engajamento.
        Sejam didáticos, mas ao mesmo tempo provocativos, com o potencial de serem compartilhados e de iniciar conversas.

    """


# =========================
# UTILITÁRIAS
# =========================
def slugify(text):
    return re.sub(r'[^\w\s-]', '', text.lower()).strip().replace(' ', '_')[:50]

def gemini_generate_content(prompt):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    resp = requests.post(GEMINI_URL, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()['candidates'][0]['content']['parts'][0]['text']

def gerar_titulo_gemini(texto_corte):
    prompt = f"""
        Dado o texto a seguir, gere um título curto, chamativo e descritivo para um corte de vídeo **com foco em análise política e crítica social de viés marxista**.

        O título deve obrigatoriamente usar palavras, frases ou ideias presentes no texto do corte.
        Ele deve ser **instigante, polêmico ou revelador**, buscando despertar a curiosidade e o engajamento de um público interessado em teoria e crítica marxista.
        Priorize termos que remetam a: **luta de classes, capitalismo, ideologia, sistema, exploração, alienação, materialismo histórico, desmascaramento, burguesia, proletariado, desigualdade, crise, etc.**

        Evite títulos genéricos como "Corte", "Vídeo", "Trecho", "Parte", "Clip" ou similares. Seja fiel ao conteúdo do texto, mas com um toque de análise crítica.

        Exemplo:
        Se o corte fala sobre "como o capitalismo usa a mídia para controlar a narrativa", um bom título seria: "A Mídia é uma Arma Capitalista?" ou "Como a Mídia Manipula a Classe Trabalhadora".

        Sua resposta deve ser apenas o ttulo sem nenhum outro texto adicional, estou enviando essa sua resposta para um programa que vai formatar o título para o formato final.

        Texto do corte:
        \"\"\"{texto_corte}\"\"\"
        Título:
        """
    try:
        output = gemini_generate_content(prompt)
        for line in output.strip().split('\n'):
            titulo = line.strip()
            if titulo and not any(g in titulo.lower() for g in ["corte", "vídeo", "trecho", "parte", "clip"]):
                return titulo
        palavras = texto_corte.strip().split()
        return " ".join(palavras[:8]) + ("..." if len(palavras) > 8 else "")
    except Exception as e:
        print("Erro ao gerar título com Gemini:", e)
        palavras = texto_corte.strip().split()
        return " ".join(palavras[:8]) + ("..." if len(palavras) > 8 else "")

def gerar_tags_virais(texto_corte):
    prompt = f"""
        Você é um especialista em engajamento no YouTube para vídeos de análise política com viés marxista.

        Dado o texto a seguir, gere uma lista de até 10 **tags virais curtas**, separadas por vírgula e terminadas com vírgula, com foco em:
        - Crítica ao capitalismo
        - Conceitos marxistas
        - Termos populares na esquerda política
        - Palavras que gerem engajamento em plataformas como YouTube Shorts e Instagram Reels

        Texto:
        \"\"\"{texto_corte}\"\"\"

        Responda com uma única linha no formato:
        tag1, tag2, tag3, ..., tagN,
        """
    try:
        tags = gemini_generate_content(prompt)
        # Limpar e formatar a resposta
        tags_line = tags.strip().replace("\n", "").strip(",") + ","
        return tags_line
    except Exception as e:
        print("⚠️ Erro ao gerar tags:", e)
        return "marxismo, crítica_social, capitalismo, exploração, revolução,"

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
# 2. TRANSCRIÇÃO COM WHISPER NORMAL
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
# 3. ANALISA COM GEMINI (mudança de assunto)
# =========================
print("🧠 Solicitando sugestões de cortes com base em mudança de assunto...")

prompt = f"""

    {PROMPT_CORTES}

    Requisitos:
    - Cada corte deve ter "start" e "end" em segundos.
    - Cada corte deve ter pelo menos {MIN_DURATION} segundos e no máximo {MAX_DURATION} segundos.
    
    - Cada corte deve ter um título descritivo começando pelo número (ex: "1 O motivo de...").
    - Use títulos claros, concisos, em MAIUSCULAS e sem caracteres especiais.
    - A resposta deve ser um **array JSON puro**, sem comentários ou texto fora do JSON.

    Formato de exemplo:
    [
    {{
        "start": 0,
        "end": 58,
        "description": "1 por que ele saiu do emprego",
        "platform": "shorts"
    }},
    ...
    ]

    Transcrição:
    \"\"\"{full_transcript}\"\"\"
    """

cut_suggestions = []
used_titles = set()

try:
    output_raw = gemini_generate_content(prompt)
    try:
        json_text = re.search(r'\[\s*{.*?}\s*]', output_raw, re.DOTALL).group()
        parsed = json.loads(json_text)
    except Exception:
        print("⚠️ Nenhum JSON válido encontrado na resposta do Gemini.")
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
except Exception as e:
    print("❌ Erro geral:", e)

# =========================
# 4. GERA OS CORTES COM FFMPEG + DESCRIÇÕES
# =========================

print(f"🎬 Gerando {len(cut_suggestions)} cortes e descrições...")

for i, (start, end, desc, platform) in enumerate(cut_suggestions):
    corte_texto = " ".join([s["text"] for s in segments if s["end"] > start and s["start"] < end])
    titulo_auto = gerar_titulo_gemini(corte_texto)
    tags = gerar_tags_virais(corte_texto)
    safe_title = slugify(f"{i+1} {titulo_auto}")  # Prefixo com número do corte
    duration = end - start
    numbered_title = f"{i+1} - {titulo_auto.strip().lower()}"
    output_video_path = os.path.join(video_folder, f"{safe_title}.mp4")
    output_desc_path = os.path.join(video_folder, f"{safe_title}.txt")

    print(f"🎞️ {platform.upper()} — {numbered_title} ({start:.1f}s → {end:.1f}s)")

    # Criação do vídeo
    subprocess.run([
        "ffmpeg", "-ss", str(start), "-i", video_path, "-t", str(duration),
        "-c", "copy", output_video_path
    ], check=True)

    # Criação da descrição com título no topo
description_text = f"""
    **🔥 {numbered_title} 🔥**

    {desc.strip()}

    ---

    Se este vídeo te fez pensar, se inscreva no canal para mais análises profundas sobre política, economia e sociedade. Junte-se à nossa comunidade e venha desmascarar as narrativas dominantes!

    ---

    **Assista ao vídeo COMPLETO aqui:**
    🔗 {VIDEO_URL}

    ---

    **Não perca nossos próximos conteúdos!**
    🔔 Ative o sininho para receber notificações e se mantenha atualizado.

    ---

    **Para aprofundar sua crítica e expandir sua consciência:**
    📌 Extraído do canal: {channel_name}
    {tags}

    ---

    **Compartilhe este vídeo com quem precisa despertar!** #Marxismo #Politica #CríticaSocial #AnáliseMarxista #EconomiaPolitica #Desmascaramento
    """

with open(output_desc_path, "w", encoding="utf-8") as f:
    f.write(description_text)

print("✅ Todos os cortes e descrições foram gerados com sucesso!")

