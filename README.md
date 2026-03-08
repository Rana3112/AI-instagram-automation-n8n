# AI Instagram Automation Pipeline (N8N + Python) 🚀

This repository contains an advanced, fully automated, and production-ready **N8N + Python architecture** built to dominate Instagram Reels & Carousels.

It fully automates content scraping, AI captioning/formatting, image generation modeling (FLUX.1 / SDXL), dynamic video/audio rendering, and direct Graph API Publishing without any human interference.

## 🧬 Architecture Overview

### 1. Multi-Slide Carousel Workflows (`/workflows`)
*   **`tech_news_multi_carousel_v25.json`**: An ultra-stable pipeline pulling daily Tech News, extracting Top 10 articles, routing to LLMs (GPT-4o/Gemini) for summarization, and exporting massive cinematic carousels. Wait-states dialled perfectly to prevent Graph API 400 errors.
*   **`ai_news_multi_carousel_v1.json`**: Same backbone, but natively filtered via highly targetted queries strictly locking into AI industry updates (Anthropic, DeepSeek, OpenAI).

### 2. Single-Reel High-Impact Workflows (`/workflows`)
*   **`movie_anime_single_reel_v7.json`**: Mathematical bounding shuffle selects completely random top stories. Outputs dynamic "IGN-Style" Hook Images with rich dual-colored subtitles.
*   **`ai_tech_single_reel_v2.json`**: Uses identical Single-Reel architectures but dynamically injects tech/circuit aesthetic prompts.

### 3. Core Image/Video Engines (`/scripts`)
Custom-built Flask Python servers serving as native translation layers between N8N and Generative AI imagery models:
*   **`carousel_generator_v24.py`**: The raw backbone iterating massive asynchronous arrays and mixing randomly sourced copyright-free aesthetic TikTok phonk music via `yt-dlp`. 
*   **`carousel_generator_v25.py`**: Integrates HuggingFace **FLUX.1-schnell** endpoint explicitly. Leverages math-heavy textwrap canvas logic printing glowing main headers & contextual subtext wrappers perfectly centered.
*   **`carousel_generator_v26_cloudflare.py`**: A strict failover server bypassing HF quotas entirely by pointing identically designed rendering engines toward the **Cloudflare SDXL** network. 

## 🛠️ Usage
1. Clone repository and run `pip install flask pillow requests yt-dlp`.
2. Open python files and input your APIs (`HF_API_TOKEN` / `CF_API_TOKEN`).
3. Boot desired server: `python scripts/carousel_generator_v26_cloudflare.py`
4. Import desired JSON to your N8N canvas. Update HTTP Request Authorization headers natively.
5. Click **Execute Workflow**.

> **Note:** All credentials have been strictly sanitized. Provide your own Meta developer tokens, OpenRouter keys, and hosting environments.
