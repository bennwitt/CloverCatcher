# Last modified: 2025-03-31 13:08:34
# Version: 0.0.2
import os
import hashlib
import subprocess
from pathlib import Path
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch
import shutil

# --- Configuration ---
SOURCE_DIR = Path("./main")
PROCESSED_DIR = Path("./processed")
MODEL_ID = "openai/whisper-large-v3-turbo"

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# --- Load Whisper Pipeline ---
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    MODEL_ID, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
).to(device)
processor = AutoProcessor.from_pretrained(MODEL_ID)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    return_timestamps=True,
    chunk_length_s=30,
    torch_dtype=torch_dtype,
    device=device,
)


def format_timestamp(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:02}:{mins:02}:{secs:06.3f}".replace(".", ":")


def make_vtt(chunks: list[dict]) -> str:
    vtt = "WEBVTT\n\n"
    for i, segment in enumerate(chunks, 1):
        start = format_timestamp(segment["timestamp"][0])
        end = format_timestamp(segment["timestamp"][1])
        text = segment["text"].replace("-->", "->").strip()
        vtt += f"{start} --> {end}\n{text}\n\n"
    return vtt


# --- Utils ---
def hash_filename(path: Path) -> str:
    return hashlib.sha256(path.stem.encode()).hexdigest()


def extract_audio(video_path: Path, output_wav: Path):
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-hwaccel",
        "cuda",
        "-i",
        str(video_path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(output_wav),
    ]
    subprocess.run(cmd, check=True)


def find_media_files(root: Path):
    return [p for p in root.rglob("*") if p.suffix.lower() in [".mp4", ".wav"]]


# --- Main Pipeline ---
def process_file(file_path: Path):
    file_hash = hash_filename(file_path)
    target_dir = PROCESSED_DIR / file_hash
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy original
    shutil.copy(file_path, target_dir / file_path.name)

    # Prepare audio
    if file_path.suffix.lower() == ".mp4":
        wav_path = target_dir / (file_path.stem + ".wav")
        extract_audio(file_path, wav_path)
    else:
        wav_path = file_path

    # Run Whisper
    result = pipe(str(wav_path))
    transcript_path = target_dir / "transcript.txt"
    with open(transcript_path, "w", encoding="utf-8") as f:
        for chunk in result.get("chunks", []):
            f.write(
                f"[{chunk['timestamp'][0]:.2f} - {chunk['timestamp'][1]:.2f}] {chunk['text']}\n"
            )

    vtt_text = make_vtt(result["chunks"])
    with open(transcript_path / "captions.vtt", "w", encoding="utf-8") as f:
        f.write(vtt_text)

    print(f"✔ Processed {file_path.name} → {target_dir}")


def run():
    files = find_media_files(SOURCE_DIR)
    print(f"🎯 Found {len(files)} media file(s). Processing...")
    for file in files:
        try:
            process_file(file)
        except Exception as e:
            print(f"❌ Failed to process {file.name}: {e}")


if __name__ == "__main__":
    run()
