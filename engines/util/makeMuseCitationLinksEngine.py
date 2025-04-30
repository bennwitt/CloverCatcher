# Last modified: 2025-01-01 21:56:31
# Version: 0.0.34
import os
import sys
import gradio as gr
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Any, Union
from engines.util.zTextEngine import *
from engines.util.zDataEngine import *
from engines.util.zFileEngine import *
from engines.util.zTimeEngine import *


def makeCitationLinks(uniqueContentSourceCitationsList):

    mediaURLList = []

    for citation in uniqueContentSourceCitationsList:
        # Determine the file extension
        ext = citation.split(".")[-1].lower()

        # Construct the appropriate URL based on the file extension
        if ext == "docx":
            mediaURLList.append(f"{base_doc_url}/{citation}")
        elif ext == "vtt":
            mediaURLList.append(f"{base_vtt_url}/{citation}")
        elif ext == "wav":
            mediaURLList.append(f"{base_wav_url}/{citation}")
        elif ext == "mp4":
            mediaURLList.append(f"{base_vid_url}/{citation}")
        elif ext in ["jpg", "jpeg", "png", "gif"]:
            if "mooreMUSE" not in citation:
                mediaURLList.append(f"{base_img_url}/{citation}")
            else:
                mediaURLList.append(citation)
        elif ext in ["pdf"]:
            mediaURLList.append(f"{base_pdf_url}/{citation}")

    mediaURLListMd = []
    markdownLinks = [f"\n\nResponse Citations\n"]
    for url in mediaURLList:
        # Extract the last part of the URL as the label
        label = url.split("/")[-1]
        # Create a markdown link
        markdown_link = f"[{label}]({url})"
        markdownLinks.append(markdown_link)

    # Join each markdown link with a new line
    mediaURLListMd = "\n".join(markdownLinks)

    return mediaURLListMd
