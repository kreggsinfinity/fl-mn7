"""
Soothing Short Stories & Comprehension - Video Generator (16:9 Landscape)
Slow, calming bedtime and immersion stories with paragraph-by-paragraph reading and vocabulary spotlight.
"""
import os, sys, json, subprocess, random, requests, re, asyncio
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv
import edge_tts

load_dotenv()

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 1920
HEIGHT = 1080
FPS = 30

BG_TWILIGHT = (8, 12, 28)
AMBER_STARLIGHT = (253, 230, 138)
CYAN_MIST = (125, 211, 252)
WHITE = (255, 255, 255)
CARD_BG = (18, 24, 48)

VOICE_NARRATOR = "en-US-AvaNeural"
VOICE_RATE = "-20%"    # Very slow, calming, peaceful reading pace

STORIES = [
    {
        "title": "THE OLD BOOKSHOP IN THE RAIN",
        "icon": "🌧️",
        "paragraphs": [
            {
                "text": "Outside, a gentle autumn rain was falling over the cobblestone streets.",
                "vocab": [("Gentle", "mild and soft"), ("Autumn", "the season of fall")]
            },
            {
                "text": "Inside the cozy bookshop, the warm aroma of hot cinnamon tea filled the quiet room.",
                "vocab": [("Aroma", "a pleasant, comforting smell"), ("Cozy", "warm and comfortable")]
            },
            {
                "text": "An old brass clock ticked softly by the fireplace, creating a peaceful rhythm.",
                "vocab": [("Brass", "a bright yellow metal"), ("Peaceful", "calm and free from noise")]
            },
            {
                "text": "Taking a deep breath, she opened a leather-bound book and began to read.",
                "vocab": [("Leather-bound", "wrapped in leather cover"), ("Deep breath", "slow relaxing inhale")]
            }
        ]
    }
]

def load_font(size, bold=True):
    fonts_to_try = [
        "C:/Windows/Fonts/georgiab.ttf",
        "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in fonts_to_try:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

def render_story_frame(story, p_idx, total_p, elapsed, total_dur, out_path):
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), BG_TWILIGHT)
    draw = ImageDraw.Draw(canvas)

    # Twilight gradient background
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(8 + ratio * 14)
        g = int(12 + ratio * 16)
        b = int(28 + ratio * 32)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    # Add soft ambient star specks
    random.seed(42)
    for _ in range(80):
        sx = random.randint(20, WIDTH - 20)
        sy = random.randint(20, HEIGHT - 100)
        alpha = random.randint(80, 200)
        draw.point((sx, sy), fill=(220, 230, 255, alpha))

    # 1. Header Banner
    draw.rounded_rectangle([(80, 40), (WIDTH - 80, 120)], radius=20, fill=(18, 26, 52), outline=AMBER_STARLIGHT, width=2)
    f_hdr = load_font(32, bold=True)
    draw.text((120, 80), f"🌙 SLOW ENGLISH STORYTIME • RELAX & LEARN", fill=AMBER_STARLIGHT, font=f_hdr, anchor="lm")
    draw.text((WIDTH - 120, 80), f"{story['icon']} {story['title']}", fill=WHITE, font=f_hdr, anchor="rm")

    current_p = story["paragraphs"][p_idx]

    # 2. Left Story Card (70% width)
    story_card_w = 1220
    draw.rounded_rectangle([(80, 160), (80 + story_card_w, 940)], radius=25, fill=CARD_BG, outline=(50, 65, 105), width=3)

    f_p_tag = load_font(26, bold=True)
    draw.text((120, 210), f"CHAPTER 1  •  PASSAGE {p_idx+1} OF {total_p}", fill=CYAN_MIST, font=f_p_tag, anchor="lm")

    # Render large readable narrative sentence
    f_story = load_font(52, bold=True)
    words = current_p["text"].split()
    lines = []
    cw = []
    for w in words:
        tb = draw.textbbox((0, 0), " ".join(cw + [w]), font=f_story)
        if tb[2] - tb[0] > (story_card_w - 120):
            lines.append(" ".join(cw))
            cw = [w]
        else:
            cw.append(w)
    if cw: lines.append(" ".join(cw))

    start_y = 520 - (len(lines) * 75) // 2
    for l_idx, line in enumerate(lines):
        # Shadow
        draw.text((123, start_y + l_idx * 75 + 3), line, fill=(0, 0, 0, 200), font=f_story, anchor="lm")
        # Text
        draw.text((120, start_y + l_idx * 75), line, fill=WHITE, font=f_story, anchor="lm")

    # 3. Right Vocabulary Spotlight Drawer (30% width)
    vocab_left = 80 + story_card_w + 30
    vocab_right = WIDTH - 80
    draw.rounded_rectangle([(vocab_left, 160), (vocab_right, 940)], radius=25, fill=(16, 22, 44), outline=AMBER_STARLIGHT, width=3)

    f_vhdr = load_font(28, bold=True)
    draw.text((vocab_left + 30, 210), "📖 VOCABULARY SPOTLIGHT", fill=AMBER_STARLIGHT, font=f_vhdr, anchor="lm")

    vy = 280
    for vword, vdef in current_p["vocab"]:
        draw.rounded_rectangle([(vocab_left + 25, vy), (vocab_right - 25, vy + 240)], radius=18, fill=(24, 32, 60), outline=(60, 75, 120), width=2)
        f_vw = load_font(38, bold=True)
        draw.text((vocab_left + 50, vy + 55), f"✨ {vword}", fill=AMBER_STARLIGHT, font=f_vw, anchor="lm")

        f_vd = load_font(28, bold=False)
        dwords = vdef.split()
        dlines = []
        cd = []
        for dw in dwords:
            tb = draw.textbbox((0, 0), " ".join(cd + [dw]), font=f_vd)
            if tb[2] - tb[0] > (vocab_right - vocab_left - 100):
                dlines.append(" ".join(cd))
                cd = [dw]
            else:
                cd.append(dw)
        if cd: dlines.append(" ".join(cd))
        for dl_idx, dl in enumerate(dlines):
            draw.text((vocab_left + 50, vy + 120 + dl_idx * 40), dl, fill=WHITE, font=f_vd, anchor="lm")
        vy += 270

    # 4. Bottom Footer & Progress
    draw.line([(0, 1000), (WIDTH, 1000)], fill=(30, 40, 70), width=2)
    ratio = min(1.0, elapsed / max(1.0, total_dur))
    draw.line([(0, 1000), (int(WIDTH * ratio), 1000)], fill=AMBER_STARLIGHT, width=5)

    f_foot = load_font(26, bold=False)
    draw.text((80, 1040), "Relax • Close Your Eyes • Listen to English Naturally", fill=(180, 195, 225), font=f_foot, anchor="lm")
    t_str = f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d} / {int(total_dur // 60):02d}:{int(total_dur % 60):02d}"
    draw.text((WIDTH - 80, 1040), t_str, fill=AMBER_STARLIGHT, font=f_foot, anchor="rm")

    canvas.convert("RGB").save(out_path, quality=92)

async def assemble_story_video(story, run_dir):
    frames_dir = run_dir / "frames"
    clips_dir = run_dir / "clips"
    audio_dir = run_dir / "audio"
    for d in [frames_dir, clips_dir, audio_dir]:
        d.mkdir(parents=True, exist_ok=True)

    total_p = len(story["paragraphs"])
    audio_durations = []

    # 1. Synthesize all audio
    for i, p in enumerate(story["paragraphs"]):
        mp3_p = audio_dir / f"p_{i}.mp3"
        await edge_tts.Communicate(p["text"], VOICE_NARRATOR, rate=VOICE_RATE).save(str(mp3_p))
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(mp3_p)], capture_output=True, text=True, check=True)
        dur = float(r.stdout.strip())
        audio_durations.append(dur)

    total_dur = sum(audio_durations)
    elapsed = 0.0
    clips = []

    # 2. Render clips
    for i, p in enumerate(story["paragraphs"]):
        mp3_p = audio_dir / f"p_{i}.mp3"
        dur = audio_durations[i]
        frame_p = frames_dir / f"frame_{i}.png"
        render_story_frame(story, i, total_p, elapsed, total_dur, str(frame_p))

        clip_p = clips_dir / f"clip_{i}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(frame_p), "-i", str(mp3_p),
            "-vf", f"scale={WIDTH}:{HEIGHT},fps={FPS}",
            "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p", "-preset", "fast", "-t", f"{dur:.3f}", str(clip_p)
        ], check=True, capture_output=True)

        clips.append(clip_p)
        elapsed += dur

    concat_txt = run_dir / "concat.txt"
    with open(concat_txt, "w") as f:
        for c in clips:
            f.write(f"file '{c.resolve().as_posix()}'\n")

    final_v = run_dir / "story_listening_final.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(final_v)], check=True, capture_output=True)
    return final_v, total_dur

async def run_story_generation(idx=0):
    story = STORIES[idx % len(STORIES)]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / f"run_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"[Story Listening] Generating Calming Story: '{story['title']}'...")
    final_v, dur = await assemble_story_video(story, run_dir)

    meta = {
        "title": f"Slow English Story: {story['title']} | Relax, Sleep & Comprehend",
        "description": f"Listen to a relaxing, slow English bedtime story with sentence highlighting and vocabulary definitions: '{story['title']}'. Enjoy peaceful English listening! 🌙☕📚",
        "story": story["title"],
        "duration_seconds": dur
    }
    with open(run_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"[Story Listening] Video ready: {final_v}")
    return final_v, meta
