"""
Complete Pipeline to Build 1080p MP4 Demo Video with Neural AI Voiceover.
Calibrated for exact target duration between 1:00 and 1:20 (Target: ~1:10 - 1:12).
"""

import os
import subprocess
import json
import time

VIDEO_DIR = r"D:\Project\WARRANT\video"
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
VOICE = "en-US-ChristopherNeural"

# Precisely timed narration to hit 70-74 seconds total (1:10 - 1:14)
SCENES = [
    {
        "id": "scene1_intro",
        "title": "The Problem: Lost Human Intent",
        "url": "https://warrant-web-ncno.onrender.com/",
        "text": "When engineering teams let autonomous coding agents modify production code, human authorization is lost. Nobody can prove who approved a change, or whether the agent stayed within approved scope.",
        "type": "web"
    },
    {
        "id": "scene2_switch",
        "title": "Switch Room: Multi-Agent Collaboration",
        "file": os.path.join(VIDEO_DIR, "scene2_switch.html"),
        "text": "Introducing Warrant, powered by Switch. In a shared Switch room, a tech lead assigns a task. Claude Code drafts a plan, explicitly lists target files, and binds it to a SHA-256 plan hash.",
        "type": "html"
    },
    {
        "id": "scene3_approved",
        "title": "Human Approval & Skeuomorphic Stamp",
        "url": "https://warrant-web-ncno.onrender.com/w/W-014",
        "text": "Priya approves the plan hash in chat. Warrant Clerk validates Priya's identity and locks in the plan. On the Warrant ledger, an oxblood APPROVED stamp presses onto the paper card.",
        "type": "web"
    },
    {
        "id": "scene4_scope",
        "title": "Deterministic Scope Check & Independent Audit",
        "url": "https://warrant-web-ncno.onrender.com/ledger",
        "text": "Claude Code implements the fix. Clerk deterministically verifies that all touched files are authorized. Codex runs unit tests, passes the audit, and GitHub commit status turns green.",
        "type": "web"
    },
    {
        "id": "scene5_drift",
        "title": "Catching Scope Drift: Payments Blocked",
        "url": "https://warrant-web-ncno.onrender.com/w/W-015",
        "text": "When an agent drifts—like modifying payments in Warrant W-015—Clerk catches it instantly. Touched files is not a subset of planned files. The commit is rejected, and GitHub blocks the merge.",
        "type": "web"
    },
    {
        "id": "scene6_blame_cli",
        "title": "Provenance Blame & CLI Verification",
        "file": os.path.join(VIDEO_DIR, "scene6_outro.html"),
        "text": "Every line of code is traced to the human who said yes in chat. And with the Warrant CLI, anyone can verify the cryptographic hash chain in seconds. Warrant: No Switch, no warrant.",
        "type": "html"
    }
]

def run(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Command failed ({res.returncode}): {' '.join(str(c) for c in cmd)}")
        print(res.stderr)
        raise RuntimeError(res.stderr)
    return res

def get_audio_duration(audio_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    res = run(cmd)
    return float(res.stdout.strip())

def main():
    print("=" * 60)
    print(" WARRANT AI DEMO VIDEO GENERATOR (Target: 1:00 - 1:20)")
    print("=" * 60)

    total_duration = 0.0
    scene_videos = []

    for i, scene in enumerate(SCENES, 1):
        sid = scene["id"]
        print(f"\n[{i}/{len(SCENES)}] Processing {sid}: {scene['title']}...")

        # 1. Generate Voiceover Audio with +12% rate for punchy tech demo pacing
        audio_path = os.path.join(VIDEO_DIR, f"{sid}_audio.mp3")
        tts_cmd = [
            "edge-tts",
            "--voice", VOICE,
            "--rate", "+12%",
            "--text", scene["text"],
            "--write-media", audio_path
        ]
        run(tts_cmd)
        dur = get_audio_duration(audio_path)
        print(f"  -> Generated Voiceover: {dur:.2f}s")
        total_duration += dur

        # 2. Capture Screenshot with virtual-time-budget for full rendering
        img_path = os.path.join(VIDEO_DIR, f"{sid}_shot.png")
        target_url = scene["url"] if scene["type"] == "web" else f"file:///{scene['file'].replace('\\', '/')}"
        
        edge_cmd = [
            EDGE_PATH,
            "--headless=new",
            "--disable-gpu",
            "--window-size=1920,1080",
            "--virtual-time-budget=4000",
            f"--screenshot={img_path}",
            target_url
        ]
        run(edge_cmd)
        print(f"  -> Captured 1080p Screenshot ({os.path.getsize(img_path)} bytes)")

        # 3. Render Scene Video Segment (Image + Audio)
        # Pad slightly (+0.25s) for smooth audio pacing
        segment_video = os.path.join(VIDEO_DIR, f"{sid}.mp4")
        padded_dur = dur + 0.25
        
        ffmpeg_seg = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-t", str(padded_dur),
            "-shortest",
            segment_video
        ]
        run(ffmpeg_seg)
        print(f"  -> Rendered Segment: {segment_video}")
        scene_videos.append(segment_video)

    print("\n" + "=" * 60)
    print(f"All 6 scenes rendered! Total Voice Duration: {total_duration:.2f}s")

    # 4. Concatenate into Final Video
    concat_list_path = os.path.join(VIDEO_DIR, "concat_list.txt")
    with open(concat_list_path, "w") as f:
        for sv in scene_videos:
            f.write(f"file '{sv}'\n")

    output_final = os.path.join(VIDEO_DIR, "warrant_demo_video.mp4")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        output_final
    ]
    run(concat_cmd)

    final_dur = get_audio_duration(output_final)
    print("=" * 60)
    print(f"SUCCESS! Video created: {output_final}")
    print(f"Final Total Video Duration: {final_dur:.2f}s ({int(final_dur)//60}:{int(final_dur)%60:02d})")
    print(f"Target Check: 1:00 to 1:20 -> {'PERFECT MATCH!' if 60 <= final_dur <= 80 else 'Check timing'}")
    print(f"Size: {os.path.getsize(output_final) / (1024*1024):.2f} MB")
    print("=" * 60)

if __name__ == "__main__":
    main()
