# Last modified: 2024-12-31 23:35:22
# Version: 0.0.3
import markdown2
from fpdf import FPDF
import os
import sys
import gradio as gr
import pdfkit
import base64

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Any, Union

from engines.util.zTextEngine import *
from engines.util.zDataEngine import *
from engines.util.zFileEngine import *
from engines.util.zTimeEngine import *


def mark2pdf(markDownString, pdfFilePath):
    try:
        html = markdown2.markdown(markDownString)
        pdfkit.from_string(html, pdfFilePath)

        statusText = "Saved"
        return statusText

    except Exception as e:
        errMsg = f"Error in Chat To PDF: {e}"
        print(errMsg)
        return errMsg


def mark2html2pdfandImg(userName, markDownString, imgFilePath, pdfFilePath):
    # imgFile can be HTTP, localPath or Base64
    def encode_image(imgFilePath):
        with open(imgFilePath, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    try:
        imgFileBase64 = encode_image(imgFilePath)
        htmlTextBody = markdown2.markdown(markDownString)
        fullHTML = f"""<!DOCTYPE html>
        <html>
        <head>
            <title>Your Output {userName}</title>
            <style>
                body {{
                    text-align: center;
                    page-break-inside: avoid;
                }}
                img {{
                    border: 3px solid black;
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                }}
                .left-justify {{
                    text-align: left;
                    display: inline-block;
                }}
                div {{
                    page-break-inside: avoid;
                }}
            </style>
        </head>
        <body>
            <h1>Hello, {userName}</h1>
            <p>Your Engagement Artifacts</p>
            <img src="data:image/png;base64,{imgFileBase64}" alt="IMG">
            <div class="left-justify">
                {htmlTextBody}
            </div>
        </body>
        </html>"""

        pdfkit.from_string(fullHTML, pdfFilePath)

        statusText = "File Saved. Use Download Button To Retrieve."
        return statusText

    except Exception as e:
        errMsg = f"Error in To PDF: {e}"
        print(errMsg)
        return errMsg
