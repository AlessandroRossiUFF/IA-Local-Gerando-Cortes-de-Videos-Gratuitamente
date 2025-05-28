# 🎬 IA Local para Geração Automática de Cortes de Vídeos — 100% Gratuito e Ilimitado

Bem-vindo ao nosso projeto open-source que transforma vídeos longos do YouTube em **cortes virais otimizados para redes sociais** — tudo rodando **localmente, sem custos, sem limites e com total liberdade de evolução**.

---

## 🚀 Visão Geral do Projeto

Desenvolvemos uma solução funcional que utiliza inteligência artificial local para:
- 🎥 Baixar vídeos do YouTube
- 🧠 Transcrever o conteúdo em texto com o modelo **Whisper**
- 🧩 Detectar mudanças de assunto com **modelos de linguagem locais (via Ollama)**
- ✂️ Gerar cortes automáticos com **títulos, descrições e organização por plataforma**
- 💡 Sem depender de APIs pagas ou serviços em nuvem!

> **📌 Nosso diferencial:** o pipeline completo roda 100% local, com ferramentas gratuitas e open-source. Ideal para criadores de conteúdo, equipes de marketing, ou projetos de mídia social que desejam escalar sem depender de serviços caros.

---

## 🧱 Estamos no Início — e é Aqui que Você Entra!

O projeto está em fase inicial, mas **já funciona completamente de ponta a ponta**. Ainda há muito espaço para expandir com:
- Integração com modelos de linguagem maiores (LLaMA 3 70B, Mistral, etc.)
- Interfaces web e mobile
- Geração automática de **hashtags**, **thumbnails**, **scripts de narração**
- Análise de **emoção na voz**, **tópicos dominantes** e **engajamento esperado**
- Deploy em ambientes com GPU, nuvem ou apps desktop

Estamos buscando **colaboradores, apoiadores técnicos, investidores e entusiastas** que queiram construir algo revolucionário com a gente.

---

## 🔧 Como Funciona — Pipeline Inteligente

1. **Download automático do vídeo**
2. **Transcrição com OpenAI Whisper**
3. **Segmentação por tópico com LLM local (Ollama)**
4. **Corte automático com FFmpeg**
5. **Geração de títulos e descrições prontos para redes sociais**

Tudo isso ocorre em segundos com apenas um link do YouTube.

---

## 🛠️ Como Rodar Localmente

### 1. Pré-requisitos

- Python 3.10+
- ffmpeg instalado no sistema
- [Ollama](https://ollama.com) instalado e rodando localmente
- Modelos Whisper e LLaMA/Mistral baixados localmente

### 2. Instale as dependências

```bash
pip install -r requirements.txt
pip install git+https://github.com/openai/whisper.git
