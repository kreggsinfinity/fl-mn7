"""
SOOTHING ENGLISH STORIES & PODCAST - 16:9 FULL HD (1920x1080) VIDEO GENERATOR
Theme: Midnight Celestial Acoustic Studio
Visuals: Vintage Chrome Ribbon Mic + 30-Bar Starlight Ripple Equalizer + Single-Line Highlighted Subtitles
"""
import os, sys, json, math, subprocess, random, requests, re, asyncio
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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
SUBFRAMES_PER_SEC = 2

STARLIGHT_GOLD = (253, 224, 71)
MOON_SILVER = (224, 231, 255)
MIDNIGHT_INDIGO = (99, 102, 241)
CYAN_MIST = (125, 211, 252)
WHITE = (255, 255, 255)
DARK_BG = (10, 11, 26)
CARD_BG = (18, 20, 44)
CARD_BORDER = (48, 52, 98)
MUTED_TEXT = (165, 175, 215)

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
        "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
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

def draw_vintage_ribbon_mic(draw, center_x, center_y, is_active, host_label):
    # Desk circular base
    base_c = STARLIGHT_GOLD if is_active else (45, 50, 85)
    draw.ellipse([(center_x - 65, center_y + 115), (center_x + 65, center_y + 135)], fill=(20, 24, 48), outline=base_c, width=3)
    # Stand column
    draw.rectangle([(center_x - 7, center_y - 10), (center_x + 7, center_y + 115)], fill=(60, 68, 110))

    # Chrome Ribbon Mic Housing (Classic rectangular broadcast ribbon mic)
    mic_c = (28, 34, 68) if not is_active else (40, 52, 105)
    draw.rounded_rectangle([(center_x - 34, center_y - 95), (center_x + 34, center_y - 15)], radius=12, fill=mic_c, outline=STARLIGHT_GOLD if is_active else CARD_BORDER, width=3)

    # Front perforated diamond mesh
    for gy in range(center_y - 85, center_y - 25, 10):
        draw.line([(center_x - 26, gy), (center_x + 26, gy)], fill=CYAN_MIST if is_active else (55, 65, 105), width=2)

    # Glowing halo when active
    if is_active:
        draw.ellipse([(center_x - 60, center_y - 85), (center_x + 60, center_y + 15)], outline=STARLIGHT_GOLD, width=2)

    # Host Label
    f_p = load_font(22, bold=True)
    box_c = (22, 28, 58) if not is_active else (38, 48, 98)
    draw.rounded_rectangle([(center_x - 85, center_y + 145), (center_x + 85, center_y + 180)], radius=8, fill=box_c, outline=STARLIGHT_GOLD, width=2)
    tag = f"🎙️ {host_label}" + (" (NARRATING)" if is_active else "")
    draw.text((center_x, center_y + 162), tag, fill=STARLIGHT_GOLD if is_active else MUTED_TEXT, font=f_p, anchor="mm")

def draw_starlight_equalizer(draw, center_x, center_y, width, height, sub_idx, is_speaking):
    num_bars = 30
    bar_w = 8
    gap = (width - (num_bars * bar_w)) // (num_bars - 1)

    draw.rounded_rectangle([(center_x - width//2 - 18, center_y - height//2 - 12),
                            (center_x + width//2 + 18, center_y + height//2 + 12)],
                           radius=16, fill=(16, 18, 40), outline=MIDNIGHT_INDIGO, width=2)

    f_hud = load_font(18, bold=True)
    draw.text((center_x, center_y - height//2 - 1), "✨ CELESTIAL ACOUSTIC SOUND RIPPLE ✨", fill=CYAN_MIST, font=f_hud, anchor="mm")

    start_x = center_x - width//2
    for b in range(num_bars):
        if is_speaking:
            phase = sub_idx * 0.82 + b * 0.35
            wave = abs(math.sin(phase)) * 0.76 + abs(math.cos(phase * 1.25)) * 0.24
            bar_h = int(10 + wave * (height - 26))
        else:
            bar_h = 8

        bx = start_x + b * (bar_w + gap)
        by = center_y + height//2 - 8 - bar_h

        # Silver to starlight gold gradient
        fill_c = STARLIGHT_GOLD if b % 2 == 0 else MOON_SILVER
        draw.rounded_rectangle([(bx, by), (bx + bar_w, center_y + height//2 - 8)], radius=3, fill=fill_c)

def render_podcast_subframe(story, turn, turn_idx, sub_idx, total_subframes, elapsed, total_dur, out_path):
    canvas = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), DARK_BG)
    draw = ImageDraw.Draw(canvas)

    # Midnight Celestial Twilight gradient background
    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        r = int(10 + ratio * 12)
        g = int(11 + ratio * 14)
        b = int(26 + ratio * 32)
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(r, g, b, 255))

    # Add gentle ambient star specks in upper sky
    random.seed(101)
    for _ in range(70):
        sx = random.randint(30, VIDEO_WIDTH - 30)
        sy = random.randint(20, 600)
        alpha = random.randint(70, 220)
        draw.point((sx, sy), fill=(225, 235, 255, alpha))

    # Top Header Deck
    # Left: Channel badge
    draw.rounded_rectangle([(60, 36), (560, 106)], radius=16, fill=CARD_BG, outline=MIDNIGHT_INDIGO, width=2)
    f_brand = load_font(28, bold=True)
    draw.text((310, 71), "🌙 CELESTIAL STORY LOUNGE", fill=MOON_SILVER, font=f_brand, anchor="mm")

    # Center: Story Title Pill
    draw.rounded_rectangle([(590, 36), (1450, 106)], radius=16, fill=(22, 26, 56), outline=STARLIGHT_GOLD, width=2)
    f_scen = load_font(26, bold=True)
    draw.text((1020, 71), f"{story['icon']} STORY: {story['title']}", fill=STARLIGHT_GOLD, font=f_scen, anchor="mm")

    # Right: Calming Mode Pill
    draw.rounded_rectangle([(1480, 36), (1860, 106)], radius=16, fill=(25, 22, 50), outline=CYAN_MIST, width=2)
    f_air = load_font(26, bold=True)
    draw.text((1670, 71), "IMMERSION & RELAX", fill=CYAN_MIST, font=f_air, anchor="mm")

    # Visual Studio Centerpiece: Chrome Ribbon Mics & Starlight Ripple
    is_emma = (turn["speaker"] == "Host1")
    is_andrew = not is_emma

    # Left Mic: Emma
    draw_vintage_ribbon_mic(draw, center_x=320, center_y=370, is_active=is_emma, host_label="EMMA")

    # Center Equalizer Deck
    draw_starlight_equalizer(draw, center_x=960, center_y=350, width=560, height=140, sub_idx=sub_idx, is_speaking=True)

    # Center Story Atmosphere Quote Card
    draw.rounded_rectangle([(680, 460), (1240, 540)], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    f_top = load_font(24, bold=True)
    draw.text((960, 500), "Slow English Listening • Comprehension", fill=MOON_SILVER, font=f_top, anchor="mm")

    # Right Mic: Andrew
    draw_vintage_ribbon_mic(draw, center_x=1600, center_y=370, is_active=is_andrew, host_label="ANDREW")

    # LOWER THIRD: SLEEK SINGLE-LINE SUBTITLE DISPLAY WITH WORD-BY-WORD HIGHLIGHTING
    draw.rounded_rectangle([(100, 680), (1820, 930)], radius=24, fill=(14, 16, 38, 240), outline=MIDNIGHT_INDIGO, width=3)

    # Speaker Tag Pill
    active_name = "EMMA (Narrator)" if is_emma else "ANDREW (Guide)"
    draw.rounded_rectangle([(140, 650), (450, 705)], radius=12, fill=MIDNIGHT_INDIGO)
    f_spk = load_font(26, bold=True)
    draw.text((295, 677), f"🎙️ {active_name}", fill=WHITE, font=f_spk, anchor="mm")

    # Sentence & Spoken Word Highlighting
    raw_text = turn["text"]
    words_clean = [re.sub(r'[\*\*\.]', '', w).strip() for w in raw_text.split() if w.strip()]
    if not words_clean:
        words_clean = ["Listen", "carefully"]

    active_word_idx = min(len(words_clean) - 1, int((sub_idx / max(1, total_subframes)) * len(words_clean)))

    f_sub = load_font(42, bold=True)
    rendered_words = raw_text.split()

    line_words = []
    lines = []
    max_w = 1600
    curr_w = 0

    for w_i, w in enumerate(rendered_words):
        clean_w = re.sub(r'\*\*(.*?)\*\*', r'\1', w)
        wb = draw.textbbox((0, 0), clean_w + " ", font=f_sub)
        w_len = wb[2] - wb[0]
        if curr_w + w_len > max_w and line_words:
            lines.append(line_words)
            line_words = [(w_i, w, clean_w, w_len)]
            curr_w = w_len
        else:
            line_words.append((w_i, w, clean_w, w_len))
            curr_w += w_len
    if line_words:
        lines.append(line_words)

    y_start = 740 if len(lines) == 1 else 725
    line_h = 55
    for l_idx, line in enumerate(lines[:2]):
        total_line_w = sum(item[3] for item in line)
        start_x = 960 - total_line_w // 2
        curr_x = start_x
        y_pos = y_start + l_idx * line_h

        for (w_i, raw_w, clean_w, w_len) in line:
            is_active_word = (w_i == active_word_idx)
            is_key_word = ("**" in raw_w)

            if is_active_word:
                # Starlight Gold active karaoke pill
                draw.rounded_rectangle([(curr_x - 4, y_pos - 6), (curr_x + w_len - 2, y_pos + 46)], radius=8, fill=STARLIGHT_GOLD)
                draw.text((curr_x, y_pos), clean_w, fill=(12, 14, 30), font=f_sub)
            elif is_key_word:
                draw.text((curr_x, y_pos), clean_w, fill=CYAN_MIST, font=f_sub)
            else:
                draw.text((curr_x, y_pos), clean_w, fill=WHITE, font=f_sub)
            curr_x += w_len

    # Tip Ribbon inside the Lower Third
    f_tip = load_font(22, bold=False)
    draw.text((960, 885), "✨ Immersion Tip: Close your eyes or relax while listening to absorb sentence cadences naturally.", fill=MUTED_TEXT, font=f_tip, anchor="mm")

    # Bottom Progress Deck
    draw.line([(0, 1020), (VIDEO_WIDTH, 1020)], fill=(32, 38, 70), width=3)
    ratio = min(1.0, elapsed / max(1.0, total_dur))
    draw.line([(0, 1020), (int(VIDEO_WIDTH * ratio), 1020)], fill=STARLIGHT_GOLD, width=6)

    f_bot = load_font(24, bold=False)
    draw.text((70, 1050), "Soothing Short Stories • Slow English Audio • Effortless Immersion", fill=MUTED_TEXT, font=f_bot, anchor="lm")
    time_str = f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d} / {int(total_dur // 60):02d}:{int(total_dur % 60):02d}"
    draw.text((1850, 1050), time_str, fill=STARLIGHT_GOLD, font=f_bot, anchor="rm")

    canvas.convert("RGB").save(out_path, quality=90)

def assemble_video(story, turns, audio_list, run_dir):
    frames_dir = run_dir / "frames"
    clips_dir = run_dir / "clips"
    frames_dir.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)

    total_dur = sum(a["duration"] for a in audio_list)
    elapsed = 0.0
    clips = []

    for i, (turn, audio) in enumerate(zip(turns, audio_list)):
        dur = audio["duration"]
        subframes_count = max(8, int(dur * SUBFRAMES_PER_SEC))

        turn_frames_dir = frames_dir / f"turn_{i:03d}"
        turn_frames_dir.mkdir(parents=True, exist_ok=True)

        for s_idx in range(subframes_count):
            frame_p = turn_frames_dir / f"frame_{s_idx:04d}.png"
            sub_elapsed = elapsed + (s_idx / subframes_count) * dur
            render_podcast_subframe(
                story, turn, i, s_idx, subframes_count,
                sub_elapsed, total_dur, str(frame_p)
            )

        clip_p = clips_dir / f"clip_{i:03d}.mp4"
        input_pattern = str(turn_frames_dir / "frame_%04d.png")

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(SUBFRAMES_PER_SEC),
            "-i", input_pattern,
            "-i", audio["path"],
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-preset", "veryfast",
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
    print(f"[Story Podcast] Generating 16:9 Celestial Lounge: '{story['title']}' ({len(turns)} turns)...")
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

    print(f"[Story Podcast] Video ready: {video_p}")
    return video_p, meta

if __name__ == "__main__":
    asyncio.run(run_story_generation(idx=0, turns_count=2))
