import base64
import requests
import sys
import os
import json
import shutil
from typing import List, Tuple, Dict, Any
import gradio as gr
import random
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def saveImgWithSizeLimit(imageArtifact, file_path, max_size_mb=16):
    max_size_bytes = max_size_mb * 1024 * 1024

    quality = 90

    imageArtifact.save(file_path, optimize=True, quality=quality)

    file_size = os.path.getsize(file_path)

    if file_size > max_size_bytes:
        width, height = imageArtifact.size
        new_size = (width // 2, height // 2)
        scaledImageArtifact = imageArtifact.resize(new_size, Image.Resampling.LANCZOS)
        scaledImageArtifact.save(file_path, optimize=True, quality=quality)

    file_size = os.path.getsize(file_path)

    while file_size > max_size_bytes and quality > 10:
        quality -= 10
        imageArtifact.save(file_path, optimize=True, quality=quality)
        file_size = os.path.getsize(file_path)

    if file_size > max_size_bytes:
        print("Warning: The image could not be saved under the specified size limit.")

    return file_size, quality


def processImageContent(
    contentArtifact, collectionMediaFolders, content_collection, mediaID, insightPrompt
):

    imgGuid = makeGuid()
    imgFileNameGuid = f"{imgGuid}.png"
    imgFolderPath = collectionMediaFolders["imgFolder"]
    txtFolderPath = collectionMediaFolders["txtFolder"]
    wavFolderPath = collectionMediaFolders["wavFolder"]
    imgFilePath = os.path.join(collectionMediaFolders["imgFolder"], imgFileNameGuid)

    try:
        os.makedirs(os.path.dirname(imgFilePath), exist_ok=True)

        saveImgWithSizeLimit(contentArtifact, imgFilePath, max_size_mb=16)

    except Exception as e:
        errTxt = f"An error occurred while saving the file: {e}"
        return errTxt, errTxt

    insightStatus, imgInsightResponseTextRaw, imgInsightResponseTextClean = (
        sendImageForInsights(
            imgFileNameGuid,
            imgFilePath,
            insightPrompt,
        )
    )
    if insightStatus == False:
        return insightStatus, imgInsightResponseTextRaw

    sendToArango(
        content_collection,
        mediaID,
        imgFileNameGuid,
        imgFilePath,
        imgInsightResponseTextClean,
        insightPrompt,
    )

    return imgInsightResponseTextRaw, imgInsightResponseTextRaw


def sendToArango(
    content_collection,
    mediaID,
    imgFileNameGuid,
    imgFilePath,
    imgInsightResponseTextFull,
    insightPrompt,
):
    imgInsightContent = {
        "mediaID": mediaID,
        "imgFileNameGuid": imgFileNameGuid,
        "imgFilePath": imgFilePath,
        "imgInsightResponseTextFull": imgInsightResponseTextFull,
        "insightPrompt": insightPrompt,
        "contentType": "imgInsights",
    }

    arangoAction(
        dbID,
        content_collection,
        imgInsightContent,
    )
    return
