import os
import requests
import tempfile
import textwrap
import urllib.request
import threading
import subprocess
import re
import time
import random
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify

app = Flask(__name__)

HF_API_TOKEN = "YOUR_HUGGINGFACE_TOKEN_HERE"
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

FONT_URL = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Black.ttf"
FONT_PATH = "Roboto-Black.ttf"
FONT_REGULAR_URL = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf"
FONT_REGULAR_PATH = "Roboto-Regular.ttf"

# Rich, curated list covering cinematic, dark aesthetic, synthwave and phonk tracks for perfect news atmosphere
# Used natively by Python instead of relying on the N8N payload map to beat caching entirely.
DIVERSE_TRACK_LIST = [
    "memory reboot v0j",
    "the lost soul down",
    "snowfall oneheart",
    "after dark mr kitty",
    "metamorphosis interworld",
    "sahara hensonn",
    "murder in my mind kordhell",
    "neon blade moondeity",
    "goth von muller",
    "resonance home",
    "sweater weather slowed version",
    "supervillain playboi carti instrumental",
    "midnight city slowed reverb",
    "vidiya slater",
    "past lives borns slowed",
    "in essence kaos",
    "close eyes dvrst",
    "rapture interworld",
    "sigma male grindset song dark",
    "tokyo drift slowed"
]

def download_fonts():
    if not os.path.exists(FONT_PATH):
        try: urllib.request.urlretrieve(FONT_URL, FONT_PATH)
        except: pass
    if not os.path.exists(FONT_REGULAR_PATH):
        try: urllib.request.urlretrieve(FONT_REGULAR_URL, FONT_REGULAR_PATH)
        except: pass

def remove_emojis(text):
    if not text: return ""
    text = text.replace('\u2018', "'").replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')
    return text.encode('ascii', 'ignore').decode('ascii').strip()

def download_audio_from_youtube(song_name, dir_path):
    print(f"Downloading uniquely randomized audio track: {song_name}")
    audio_path = os.path.join(dir_path, 'music.mp3')
    cmd = [
        "yt-dlp", f"ytsearch1:{song_name} audio",
        "-x", "--audio-format", "mp3",
        "--output", os.path.join(dir_path, "music.%(ext)s"),
        "--force-overwrites"
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return audio_path

def fetch_real_image(query, output_path):
    print(f"HuggingFace FLUX.1 generating: {query}")
    success = False
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": f"{query}, breathtaking masterpiece, highly detailed photography, 8k resolution, cinematic lighting, photorealistic, NO TEXT, textless"}
    
    for attempt in range(4):
        try:
            r = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(r.content)
                success = True
                print("Successfully rendered FLUX.1 image!")
                break
            elif r.status_code == 503:
                print(f"HF Model loading (Attempt {attempt+1}/4), waiting 10s... ({r.text})")
                time.sleep(10)
            else:
                print(f"HuggingFace API failed with status {r.status_code}: {r.text}")
                break
        except Exception as e:
            print(f"HuggingFace FLUX generation exception: {e}")
            break
            
    if not success:
        print(f"Applying emergency fallback for {query}...")
        try:
            r = requests.get("https://images.unsplash.com/photo-1518770660439-4636190af475?w=1080", stream=True, timeout=5)
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(8192): f.write(chunk)
        except: pass

def wrap_rich_text(text, font, max_width, draw):
    tokens = re.split(r'(</?c>)', text, flags=re.IGNORECASE)
    words = []; is_colored = False
    for t in tokens:
        if t.lower() == '<c>': is_colored = True
        elif t.lower() == '</c>': is_colored = False
        else:
            for chunk in re.findall(r'\S+', t):
                words.append({"text": chunk, "space": " ", "colored": is_colored})
    if words: words[-1]['space'] = ""
    lines = []; curr_line = []; curr_width = 0
    for w in words:
        w_width = draw.textlength(w["text"] + " ", font=font)
        if curr_width + w_width <= max_width:
            curr_line.append(w); curr_width += w_width
        else:
            if curr_line: lines.append(curr_line)
            curr_line = [w]; curr_width = w_width
    if curr_line: lines.append(curr_line)
    return lines

def create_hook_slide(image_path, text, output_path, target_size=(1080, 1080)):
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
    try: img = Image.open(image_path).convert("RGBA")
    except: img = Image.new('RGBA', target_size, (50,50,50,255))
    w, h = img.size; min_dim = min(w, h)
    img = img.crop(((w-min_dim)/2, (h-min_dim)/2, (w+min_dim)/2, (h+min_dim)/2))
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    img = ImageEnhance.Brightness(img).enhance(0.75)
    gradient = Image.new('RGBA', img.size, (0,0,0,0))
    draw = ImageDraw.Draw(gradient)
    for y in range(int(h*0.35), h):
        a = min(245, int(255*((y-(h*0.35))/(h*0.65))))
        draw.line([(0,y),(w,y)], fill=(0,0,0,a))
    img = Image.alpha_composite(img.convert('RGBA'), gradient)
    draw = ImageDraw.Draw(img)
    try: fl = ImageFont.truetype(FONT_PATH, 42)
    except: fl = ImageFont.load_default()
    draw.ellipse([(60,65),(75,80)], fill=(255,100,0))
    draw.text((90,55), "TechNews.", font=fl, fill=(255,255,255,255), stroke_width=2, stroke_fill="black")
    try: font = ImageFont.truetype(FONT_PATH, 75)
    except: font = ImageFont.load_default()
    lines = wrap_rich_text(remove_emojis(text).upper(), font, target_size[0]-140, draw)
    lh = 75; pad = 10; th = len(lines)*(lh+pad); yt = target_size[1]-th-90
    for line in lines:
        tw = sum(draw.textlength(w['text']+w['space'], font=font) for w in line)
        xt = (target_size[0]-tw)/2
        for w in line:
            rs = w['text']+w['space']; fc = (255,100,0,255) if w['colored'] else (255,255,255,255)
            draw.text((xt+4,yt+4), rs, font=font, fill=(0,0,0,230))
            draw.text((xt,yt), rs, font=font, fill=fc, stroke_width=2, stroke_fill="black")
            xt += draw.textlength(rs, font=font)
        yt += lh+pad
    img.convert("RGB").save(output_path, quality=95)
    return output_path

def create_detail_slide(data, output_path):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (1080,1080), (240,242,245))
    draw = ImageDraw.Draw(img)
    try: draw.rounded_rectangle([(40,40),(1040,1040)], radius=35, fill=(255,255,255))
    except: draw.rectangle([(40,40),(1040,1040)], fill=(255,255,255))
    try:
        fl = ImageFont.truetype(FONT_PATH, 42); fh = ImageFont.truetype(FONT_PATH, 55)
        fs = ImageFont.truetype(FONT_PATH, 34); fb = ImageFont.truetype(FONT_REGULAR_PATH, 32)
    except: fl=fh=fs=fb=ImageFont.load_default()
    draw.ellipse([(90,95),(105,110)], fill=(255,100,0))
    draw.text((120,85), "TechNews.", font=fl, fill=(0,0,0))
    y = 200
    for line in textwrap.TextWrapper(width=34).wrap(text=remove_emojis(data.get('headline',''))):
        draw.text((90,y), line, font=fh, fill=(0,0,0)); y+=70
    y += 40
    def dp(title, text, cy):
        if not text: return cy
        draw.text((90,cy), remove_emojis(title), font=fs, fill=(0,0,0)); cy+=48
        for bl in textwrap.TextWrapper(width=52).wrap(text=remove_emojis(text)):
            draw.text((90,cy), bl, font=fb, fill=(70,70,70)); cy+=42
        return cy+35
    if data.get('what_is_it'): y=dp("What is it:", data['what_is_it'], y)
    if data.get('how_it_helps'): y=dp("How it will help:", data['how_it_helps'], y)
    if data.get('implication'): y=dp("Implication:", data['implication'], y)
    img.save(output_path, quality=95)
    return output_path

def compile_video(image_path, audio_path, output_video_path, duration=20):
    """ KEEPING THE CRITICAL METADATA BUGFIX! """
    print(f"Compiling IG-compliant MP4: {output_video_path}")
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "30",
        "-i", image_path,
        "-i", audio_path,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "medium", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
        "-r", "30",
        "-vf", "scale=1080:1080",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-t", str(duration),
        output_video_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def upload_to_host(file_path):
    print(f"Uploading MP4: {file_path}")
    hosts = [
        ('https://envs.sh', 'file', lambda r: r.text.strip() if r.text.strip().startswith("http") else None),
        ('https://tmpfiles.org/api/v1/upload', 'file', lambda r: r.json().get("data",{}).get("url","").replace("org/","org/dl/") if "url" in r.json().get("data",{}) else None),
        ('https://uguu.se/upload.php', 'files[]', lambda r: r.json().get("files",[{}])[0].get("url"))
    ]
    for url, field, parser in hosts:
        try:
            with open(file_path, 'rb') as f:
                if field == 'files[]': r = requests.post(url, files={field: (file_path, f, 'video/mp4')}, timeout=30)
                else: r = requests.post(url, files={field: f}, timeout=30)
            if r.status_code == 200:
                result = parser(r)
                if result: return result
        except: pass
    raise Exception("ALL UPLOAD HOSTS FAILED!")

def process_single_slide(slide, i, temp_dir, audio_path):
    time.sleep(i * 3.0) 
    
    img_path = os.path.join(temp_dir, f'slide_{i}.jpg')
    vid_path = os.path.join(temp_dir, f'vid_{i}.mp4')
    if slide.get('type') == 'hook':
        raw_path = os.path.join(temp_dir, f'raw_{i}.jpg')
        query = slide.get('image_prompt', slide.get('search_query', 'futuristic technology innovation abstract'))
        fetch_real_image(query, raw_path)
        create_hook_slide(raw_path, slide.get('text',''), img_path)
    else:
        create_detail_slide(slide, img_path)
    compile_video(img_path, audio_path, vid_path, duration=20)
    host_url = upload_to_host(vid_path)
    return i, host_url

@app.route('/create_carousel_images', methods=['POST'])
def create_carousel_images():
    data = request.json
    if not data or 'slides' not in data:
        return jsonify({"error": "Missing slides"}), 400
    slides = data['slides']
    
    # -------------------------------------------------------------
    # V24 FIX: IGNORE N8N CACHED AUDIO INPUT. ENFORCE RANDOMIZATION!
    # -------------------------------------------------------------
    song_name = random.choice(DIVERSE_TRACK_LIST)
    print(f"\\n🎵 V24 Selected Audio Track: {song_name}\\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            audio_path = download_audio_from_youtube(song_name, temp_dir)
            results_dict = {}
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(process_single_slide, s, i, temp_dir, audio_path) for i, s in enumerate(slides)]
                for f in futures:
                    res = f.result()
                    if res: results_dict[res[0]] = res[1]
            video_urls = [results_dict[i] for i in range(len(slides)) if i in results_dict]
            if not video_urls:
                return jsonify({"error": "No valid videos processed."}), 500
            return jsonify({"video_urls": video_urls, "success": True})
        except Exception as e:
            import traceback; traceback.print_exc()
            return jsonify({"error": str(e), "success": False}), 500

if __name__ == '__main__':
    download_fonts()
    print("V24 HuggingFace FLUX.1 + Pure Audio Randomizer on port 5000...")
    app.run(port=5000, host="0.0.0.0", threaded=True)
