import sys
import asyncio
from story_generator import run_story_generation

def main():
    print("Starting Soothing English Storytime generator (16:9 Landscape Video)...")
    video_p, meta = asyncio.run(run_story_generation(idx=0))
    print(f"Done! Final video generated: {video_p}")

if __name__ == "__main__":
    main()
