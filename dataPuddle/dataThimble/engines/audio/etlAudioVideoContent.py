# Last modified: 2025-04-03 10:02:51
# Version: 0.0.44
import os
import subprocess
import gradio as gr
from typing import Iterator
from pathlib import Path
from engines.util.zDataEngine import removeEmptyListItems, groupListItems


def extractWavFromMp4(mp4_path, wav_path):
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


def extractWavFromMp4CPU(mp4_path, wav_path):
    cmd = [
        "ffmpeg",
        "-y",  # overwrite output if exists
        "-i",
        str(mp4_path),  # input file
        "-ac",
        "1",  # mono
        "-ar",
        "16000",  # 16kHz
        "-c:a",
        "pcm_s16le",  # 16-bit PCM WAV
        str(wav_path),
    ]
    subprocess.run(cmd, check=True)


def processAsrObject(contentIdFolderPath, filename, txtFolderPath, asrObject):
    transcript_text = ""
    transcript_time = ""
    thirtySecChunk = ""
    thirtySecChunkList = []
    threeMinChunkList = []

    for idx, chunk in enumerate(asrObject.get("chunks", [])):

        start = f"{chunk['timestamp'][0]:.2f}"
        # end = f"{chunk['timestamp'][1]:.2f}"
        end = f"{chunk['timestamp'][1] or 0:.2f}"
        transcript_time += f"[{start} - {end}] {chunk['text']}\n"
        transcript_text += f" {chunk['text'].strip()}"
        if "0.00" in start or "0.00" in end:
            thirtySecChunk += f" {chunk['text'].strip()}"
            thirtySecChunkList.append(thirtySecChunk)
            thirtySecChunk = ""
        else:
            thirtySecChunk += f" {chunk['text'].strip()}"

    thirtySecChunkList.append(thirtySecChunk) if thirtySecChunk else None

    thirtySecChunkList = removeEmptyListItems(thirtySecChunkList)
    threeMinChunkList = groupListItems(thirtySecChunkList, 6)

    vtt_text = makevtt(asrObject["chunks"])

    with open(
        os.path.join(txtFolderPath, f"{filename}.vtt"), "w", encoding="utf-8"
    ) as v:
        v.write(vtt_text)
        v.close()

    with open(
        os.path.join(txtFolderPath, f"{filename}.cap"), "w", encoding="utf-8"
    ) as v:
        v.write(transcript_time)
        v.close()

    with open(
        os.path.join(txtFolderPath, f"{filename}.txt"), "w", encoding="utf-8"
    ) as t:
        t.write(transcript_text)
        t.close()

    return [
        {
            "contentIdFolderPath": contentIdFolderPath,
            "filename": filename,
            "transcript_text": transcript_text,
            "transcript_time": transcript_time,
            "vtt_text": vtt_text,
            "thirtySecChunkList": thirtySecChunkList,
            "threeMinChunkList": threeMinChunkList,
        }
    ]


def makevtt(timeChunks: Iterator[dict]):
    # timeChunks = sorted(unsortedTimeChunks, key=lambda x: x["timestamp"][0])
    theCaptionFile = "WEBVTT \n\n"
    for segment in timeChunks:
        # chunkStart = int(segment["timestamp"][0])
        # chunkStop = int(segment["timestamp"][1])

        theCaptionFile += (
            str(format_timestamp(segment["timestamp"][0]))
            + "  -->  "
            + str(format_timestamp(segment["timestamp"][1]))
            + "\n"
            + str(segment["text"].replace("-->", "->"))
            + "\n\n"
        )
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
