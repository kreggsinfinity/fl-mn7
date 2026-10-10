"""
SOOTHING ENGLISH STORIES PODCAST - 16:9 FULL HD (1920x1080)
Format: 1920x1080 Landscape Studio Broadcast (Directly inspired by velocitykorean/fl-eng-std)
Features:
- Studio Host Setting on the left with twilight midnight indigo broadcast grading
- Minimalist, elegant top pills (NO clutter, NO extra boxes)
- HUGE high-contrast subtitle typography with word-by-word karaoke highlighting
- REALISTIC audio equalizer at the bottom reacting directly to actual voice frequencies
- Real-time elapsed timeline progress bar
"""
import os, sys, json, math, subprocess, random, requests, re, asyncio
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from dotenv import load_dotenv
import edge_tts

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

load_dotenv()

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30

# Colors
STARLIGHT_GOLD = (253, 224, 71)      # Starlight Gold (#FDE047)
WHITE = (255, 255, 255)
MUTED_WHITE = (220, 225, 235)
DARK_BAR = (18, 20, 38)
EQ_BG = (14, 16, 32, 215)
EQ_BORDER = (50, 55, 95)

CHANNEL_NAME = "SOOTHING ENGLISH STORYTIME"
EQ_COLORS_FFMPEG = "0xFDE047|0xE0E7FF"

EMMA_VOICE = "en-US-AvaNeural"
ANDREW_VOICE = "en-US-AndrewNeural"
VOICE_RATE = "-18%"

STORIES = [
    {
        "title": "THE OLD BOOKSHOP IN THE RAIN",
        "icon": "🌧️",
        "turns": [
            {"speaker": "Host1", "text": "Outside the cobblestone window, a gentle autumn rain was falling quietly over the city."},
            {"speaker": "Host2", "text": "Inside the cozy shop, the warm aroma of cinnamon tea filled every corner of the wooden shelves."},
            {"speaker": "Host1", "text": "Notice how the word **gentle** describes soft, calming rain, perfect for relaxing listening practice."},
            {"speaker": "Host2", "text": "Taking a deep breath, she opened a leather-bound book and stepped into another **peaceful** world."}
        ]
    },
    {
        "title": "THE MIDNIGHT TRAIN TO THE MOUNTAINS",
        "icon": "🚂",
        "turns": [
            {"speaker": "Host1", "text": "The midnight train glided smoothly through snow-covered pine forests beneath the glowing moon."},
            {"speaker": "Host2", "text": "Passengers wrapped themselves in warm wool blankets, listening to the rhythmic hum of the tracks."},
            {"speaker": "Host1", "text": "The phrase **rhythmic hum** paints a soothing picture of continuous, peaceful mechanical sounds."},
            {"speaker": "Host2", "text": "As the peaks appeared in the distance, a profound sense of **serenity** settled over everyone."}
        ]
    }
]

def load_font(size, bold=True):
    fonts_to_try = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/trebucbd.ttf" if bold else "C:/Windows/Fonts/trebuc.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in fonts_to_try:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

def clean_text(text):
    text = re.sub(r'\b(mm+|um+|uh+|ah+)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

async def generate_audio_files(turns, run_dir):
    audio_dir = run_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    audio_list = []
    for i, turn in enumerate(turns):
        mp3_p = audio_dir / f"turn_{i:03d}.mp3"
        spoken = re.sub(r'\*\*(.*?)\*\*', r'\1', turn["text"])
        voice = EMMA_VOICE if turn["speaker"] == "Host1" else ANDREW_VOICE
        comm = edge_tts.Communicate(spoken, voice, rate=VOICE_RATE)
        await comm.save(str(mp3_p))

        try:
            r = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(mp3_p)],
                capture_output=True, text=True, check=True
            )
            duration = float(r.stdout.strip())
        except:
            duration = 5.0
        audio_list.append({"path": str(mp3_p), "duration": duration, "speaker": turn["speaker"]})
    return audio_list

def load_base_studio_canvas():
    woman_path = ASSETS_DIR / "woman_base.png"
    if woman_path.exists():
        img = Image.open(woman_path).convert("RGB")
        # Twilight midnight indigo studio grade
        r, g, b = img.split()
        b = b.point(lambda i: min(255, int(i * 1.15)))
        g = g.point(lambda i: int(i * 0.96))
        r = r.point(lambda i: int(i * 0.90))
        graded = Image.merge("RGB", (r, g, b))
        graded = ImageEnhance.Contrast(graded).enhance(1.06)
        return graded.convert("RGBA").resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
    else:
        canvas = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (12, 14, 30, 255))
        return canvas

def render_podcast_frame(base_canvas, turn, s_idx, total_subframes, elapsed, total_dur, out_path):
    canvas = base_canvas.copy()
    draw = ImageDraw.Draw(canvas)

    # 1. Clean Top Left Pill (NO clutter)
    font_tab = load_font(30, bold=True)
    draw.rounded_rectangle([(60, 40), (580, 105)], radius=18, fill=DARK_BAR, outline=STARLIGHT_GOLD, width=3)
    # Wave icon
    for b in range(6):
        bh = int(12 + 10 * abs(math.sin(s_idx * 0.5 + b * 1.2)))
        bx = 90 + b * 12
        draw.line([(bx, 72 - bh//2), (bx, 72 + bh//2)], fill=STARLIGHT_GOLD, width=3)
    draw.text((180, 72), CHANNEL_NAME, fill=WHITE, font=font_tab, anchor="lm")

    # 2. Clean Top Right Speaker Pill
    speaker_name = "EMMA" if turn["speaker"] == "Host1" else "ANDREW"
    font_spk = load_font(30, bold=True)
    draw.rounded_rectangle([(1520, 40), (1880, 105)], radius=18, fill=DARK_BAR, outline=STARLIGHT_GOLD, width=3)
    # Vector microphone icon
    draw.rounded_rectangle([(1555, 62), (1567, 78)], radius=4, fill=STARLIGHT_GOLD)
    draw.arc([(1551, 70), (1571, 84)], start=0, end=180, fill=STARLIGHT_GOLD, width=3)
    draw.line([(1561, 84), (1561, 90)], fill=STARLIGHT_GOLD, width=3)
    draw.line([(1555, 90), (1567, 90)], fill=STARLIGHT_GOLD, width=3)
    draw.text((1585, 72), f"HOST: {speaker_name}", fill=STARLIGHT_GOLD, font=font_spk, anchor="lm")

    # 3. Huge Subtitle Typography in Safe Zone (x: 800 to 1800)
    raw_text = turn["text"]
    words_raw = raw_text.split()
    clean_words = [re.sub(r'[\*\*\.]', '', w).strip() for w in words_raw if w.strip()]
    if not clean_words: clean_words = ["Listen", "carefully"]

    active_idx = min(len(clean_words) - 1, int((s_idx / max(1, total_subframes)) * len(clean_words)))

    font_main = load_font(78, bold=True)
    max_w = 980
    lines = []
    curr_line = []
    curr_w = 0

    for w_i, raw_w in enumerate(words_raw):
        clean_w = re.sub(r'\*\*(.*?)\*\*', r'\1', raw_w)
        wb = draw.textbbox((0, 0), clean_w + " ", font=font_main)
        wl = wb[2] - wb[0]
        if curr_w + wl > max_w and curr_line:
            lines.append(curr_line)
            curr_line = [(w_i, clean_w, wl)]
            curr_w = wl
        else:
            curr_line.append((w_i, clean_w, wl))
            curr_w += wl
    if curr_line:
        lines.append(curr_line)

    line_h = 108
    total_h = len(lines) * line_h
    start_y = 500 - total_h // 2
    text_center_x = 1320

    # Gaussian blur drop shadow
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    for l_idx, line in enumerate(lines):
        lw = sum(item[2] for item in line)
        lx = text_center_x - lw // 2
        ly = start_y + l_idx * line_h
        for (w_i, clean_w, wl) in line:
            sdraw.text((lx + 4, ly + 4), clean_w, fill=(0, 0, 0, 240), font=font_main)
            lx += wl
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    canvas.paste(shadow, (0, 0), shadow)

    # Foreground text with active spoken word highlighted in Starlight Gold
    draw = ImageDraw.Draw(canvas)
    for l_idx, line in enumerate(lines):
        lw = sum(item[2] for item in line)
        lx = text_center_x - lw // 2
        ly = start_y + l_idx * line_h
        for (w_i, clean_w, wl) in line:
            is_active = (w_i == active_idx)
            col = STARLIGHT_GOLD if is_active else WHITE
            draw.text((lx, ly), clean_w, fill=col, font=font_main)
            lx += wl

    # 4. Realistic Sound Equalizer Plate at the Bottom Right
    draw.rounded_rectangle([(840, 885), (1800, 965)], radius=14, fill=EQ_BG, outline=EQ_BORDER, width=2)
    f_eq_lbl = load_font(18, bold=True)
    draw.text((865, 925), "AUDIO SPECTRUM", fill=(195, 205, 235), font=f_eq_lbl, anchor="lm")

    # 5. Bottom Timeline & Progress Bar
    draw.line([(0, 1025), (VIDEO_WIDTH, 1025)], fill=(35, 40, 75), width=2)
    ratio = min(1.0, elapsed / max(1.0, total_dur))
    draw.line([(0, 1025), (int(VIDEO_WIDTH * ratio), 1025)], fill=STARLIGHT_GOLD, width=5)

    f_bot = load_font(26, bold=False)
    draw.text((70, 1052), "Soothing Short Stories • Slow Bedtime English Immersion", fill=MUTED_WHITE, font=f_bot, anchor="lm")
    time_str = f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d} / {int(total_dur // 60):02d}:{int(total_dur % 60):02d}"
    draw.text((1850, 1052), time_str, fill=STARLIGHT_GOLD, font=f_bot, anchor="rm")

    canvas.convert("RGB").save(out_path, quality=92)

def assemble_video(story, turns, audio_list, run_dir):
    frames_dir = run_dir / "frames"
    clips_dir = run_dir / "clips"
    frames_dir.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)

    base_canvas = load_base_studio_canvas()
    total_dur = sum(a["duration"] for a in audio_list)
    elapsed = 0.0
    clips = []

    for i, (turn, audio) in enumerate(zip(turns, audio_list)):
        dur = audio["duration"]
        words_count = len(turn["text"].split())
        subframes_count = max(words_count, int(dur * 2))
        fps_sub = subframes_count / dur

        turn_frames_dir = frames_dir / f"turn_{i:03d}"
        turn_frames_dir.mkdir(parents=True, exist_ok=True)

        for s in range(subframes_count):
            frame_p = turn_frames_dir / f"frame_{s:04d}.png"
            sub_elapsed = elapsed + (s / subframes_count) * dur
            render_podcast_frame(base_canvas, turn, s, subframes_count, sub_elapsed, total_dur, str(frame_p))

        clip_p = clips_dir / f"clip_{i:03d}.mp4"
        input_pattern = str(turn_frames_dir / "frame_%04d.png")

        filter_str = (
            f"[1:a]showfreqs=s=740x55:mode=bar:ascale=log:fscale=log:colors={EQ_COLORS_FFMPEG}:win_size=1024[eq];"
            f"[0:v][eq]overlay=x=1030:y=895:shortest=1[v]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps_sub),
            "-i", input_pattern,
            "-i", audio["path"],
            "-filter_complex", filter_str,
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-preset", "fast", "-shortest",
            str(clip_p)
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        clips.append(clip_p)
        elapsed += dur

    concat_txt = run_dir / "concat.txt"
    with open(concat_txt, "w") as f:
        for c in clips:
            f.write(f"file '{c.resolve().as_posix()}'\n")

    final_video = run_dir / "story_listening_podcast_final.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(final_video)], check=True, capture_output=True)
    return final_video, total_dur

async def run_story_generation(idx=0, turns_count=4):
    story = STORIES[idx % len(STORIES)]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / f"run_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    turns = story["turns"][:turns_count]
    print(f"[Story Podcast] Generating 16:9 Broadcast: '{story['title']}' ({len(turns)} turns)...")
    audio_list = await generate_audio_files(turns, run_dir)
    video_p, dur = assemble_video(story, turns, audio_list, run_dir)

    meta = {
        "title": f"Soothing English Story: {story['title']} 🌙 Slow English Podcast",
        "description": f"Relax, unwind, and improve your English listening with our soothing bedtime immersion story: '{story['title']}'. 🌧️✨",
        "story": story["title"],
        "duration_seconds": dur
    }
    with open(run_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"[Story Podcast] Final Video ready: {video_p}")
    return video_p, meta

if __name__ == "__main__":
    asyncio.run(run_story_generation(idx=0, turns_count=2))
