# Last modified: 2025-04-29 13:04:37
# Version: 0.0.1
import ffmpeg
import os
from pathlib import Path


def normalize_video(input_path, output_dir="converted_videos", crf=23, bitrate="5M"):
    """
    Converts input video (e.g. .mov) to a CUDA-accelerated h264 MP4 file.
    Ensures web-safe, ffmpeg-friendly format for downstream processing.
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{input_path.stem}_converted.mp4"

    if output_path.exists():
        print(f"[✓] Skipping: {output_path} already exists.")
        return str(output_path)

    print(f"[🔁] Converting: {input_path} → {output_path}")

    (
        ffmpeg.input(str(input_path), hwaccel="cuda")
        .output(
            str(output_path),
            vcodec="h264_nvenc",
            preset="p3",
            rc="vbr",
            cq=crf,
            b="5M",
            maxrate="10M",
            bufsize="20M",
            movflags="+faststart",
            acodec="aac",
            audio_bitrate="128k",
            format="mp4",
        )
        .global_args("-loglevel", "error")
        .run()
    )

    print(f"[✅] Done: {output_path}")
    return str(output_path)
