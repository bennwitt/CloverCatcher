# Last modified: 2025-04-01 02:27:10
# Version: 0.0.68
# high_quality_transcriber.py
from typing import Iterator
import subprocess
from pathlib import Path
import torch._dynamo

torch._dynamo.config.suppress_errors = True
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from engines.util.zCypherEngine import encode_string, decode_string

# --- Config ---
SOURCE_DIR = Path("/ai/aiMooreLearnings/contentLibrary/src")
OUTPUT_DIR = Path("/ai/aiMooreLearnings/contentLibrary/dist")
MODEL_ID = "openai/whisper-large-v3-turbo"

# --- Device & Precision ---
torch.set_float32_matmul_precision("high")
device = "cuda:0" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# --- Load & Compile Model ---
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    MODEL_ID,
    torch_dtype=dtype,
    low_cpu_mem_usage=True,
    use_safetensors=True,
).to(device)

# Optional: enable caching for faster autoregressive decoding
model.generation_config.cache_implementation = "static"
model.generation_config.max_new_tokens = 445

# Compile model forward for speed
model.forward = torch.compile(
    model.forward,
    fullgraph=True,
    # mode="reduce-overhead",
    options={"triton.cudagraphs": True},
)

# Load processor
processor = AutoProcessor.from_pretrained(MODEL_ID)

"""generate_kwargs = {
    "max_new_tokens": 448,
    "num_beams": 1,
    "condition_on_prev_tokens": False,
    "compression_ratio_threshold": 1.35,  # zlib compression ratio threshold (in token space)
    "temperature": (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
    "logprob_threshold": -1.0,
    "no_speech_threshold": 0.6,
    "return_timestamps": True,
    }
    result = pipe(sample, generate_kwargs=generate_kwargs)
"""

# ASR Pipeline – Sequential mode (no chunking)
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    return_timestamps=True,  # Sentence-level by default
    torch_dtype=dtype,
    device=device,
)


def extract_audio(mp4_path: Path, wav_path: Path):
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-hwaccel",
        "cuda",
        "-i",
        str(mp4_path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(wav_path),
    ]
    subprocess.run(cmd, check=True)


def makevtt(timeChunks: Iterator[dict]):
    #timeChunks = sorted(unsortedTimeChunks, key=lambda x: x["timestamp"][0])
    theCaptionFile = "WEBVTT \n\n"
    for segment in timeChunks:
        chunkStart = int(segment["timestamp"][0])
        chunkStop = int(segment["timestamp"][1])


        theCaptionFile += 
        
        '''theCaptionFile += (
            str(format_timestamp(segment["timestamp"][0]))
            + "  -->  "
            + str(format_timestamp(segment["timestamp"][1]))
            + "\n"
            + str(segment["text"].replace("-->", "->"))
            + "\n\n"
        )'''
    return theCaptionFile


def format_timestamp(seconds: float):
    if not isinstance(seconds, float):
        return seconds
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)
    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000
    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000
    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000
    return (
        f"{hours}:" if hours > 0 else ""
    ) + f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def find_input_files(root: Path):
    return list(root.rglob("*.[wmm][akp][vv4]"))  # .wav or .mp4


def transcribe_and_save(
    org_filename: str, wav_path: Path, OUTPUT_DIR: Path, original_path: Path
):
    result = pipe(str(wav_path), generate_kwargs={"language": "english"})
    txt_path = str(wav_path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    transcript_text = ""
    with open(txt_path.replace(".wav", ".cap"), "w", encoding="utf-8") as f:
        for chunk in result.get("chunks", []):
            floatstart = f"{chunk['timestamp'][0]:.2f}"
            floatend = f"{chunk['timestamp'][1]:.2f}"
            start = int(floatstart)
            end = int(floatend)
            f.write(f"[{start} - {end}] {chunk['text']}\n")
            transcript_text += f" {chunk['text'].strip()}"
        f.close()

    vtt_text = makevtt(result["chunks"])
    with open(txt_path.replace(".wav", ".vtt"), "w", encoding="utf-8") as v:
        v.write(vtt_text)
        v.close()

    with open(txt_path.replace(".wav", ".txt"), "w", encoding="utf-8") as t:
        t.write(transcript_text)
        t.close()


def main():
    input_files = find_input_files(SOURCE_DIR)

    for file_path in input_files:
        file_name = file_path.stem
        file_hash = encode_string(file_path.stem)
        target_dir = OUTPUT_DIR / file_hash

        if file_path.suffix.lower() in [".mp4", ".mkv"]:
            wav_path = target_dir / (file_path.stem + ".wav")
            extract_audio(file_path, wav_path)
        else:
            wav_path = file_path

        try:
            transcribe_and_save(file_name, wav_path, target_dir, file_path)
        except Exception as e:
            print(f"❌ Error with {file_path.name}: {e}")

