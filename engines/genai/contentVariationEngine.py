# Last modified: 2025-03-01 04:00:48
# Version: 0.0.53
from datetime import datetime
import tiktoken
import gradio as gr
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Any, Union
from engines.util.zTextEngine import listToString


def genContentVariationsOpenai(
    genMaxTokens,
    modelTemp,
    topP,
    fPen,
    pPen,
    modelChoice,
    completePrompt,
):
    contentGenResponse = ""
    contentGenInfo = {}
    contentGenInfoTrunc = {}
    try:
        e = ""
        modelTemp = modelTemp
        maxT = genMaxTokens
        topP = topP
        fPen = fPen
        pPen = pPen

        modelChoice = validateModelChoiceCapacity(
            str(completePrompt), maxT, modelChoice
        )

        gr.Info(f"Versioning your content and modifiers...")

        contentGenResponse = oaClient.chat.completions.create(
            model=modelChoice,
            messages=completePrompt,
            temperature=modelTemp,
            max_tokens=maxT,
            top_p=topP,
            frequency_penalty=fPen,
            presence_penalty=pPen,
            stop=[promptStop],
        )

        if contentGenResponse.choices[0].finish_reason == "stop":
            contentGenResponseText = contentGenResponse.choices[0].message.content
            cleanPrompt = listToString(completePrompt)
            contentGenInfo = {
                "model": modelChoice,
                "messages": cleanPrompt,
                "responseText": contentGenResponseText,
                "temperature": modelTemp,
                "max_tokens": maxT,
                "top_p": topP,
                "frequency_penalty": fPen,
                "presence_penalty": pPen,
            }
            return contentGenResponseText, contentGenInfo

        if contentGenResponse.choices[0].finish_reason == "length":
            truncatedContentGenResponseText = contentGenResponse.choices[
                0
            ].message.content

            gr.Info(f"Additional content being generated.")

            finishThoughtPrompt = [
                {
                    "role": "system",
                    "name": assistantName,
                    "content": f"You are {assistantName}, an expert linguist, copywriter, rewriter and textual analyst, You excel at analyzing and completing incomplete text and content.",
                },
                {
                    "role": "user",
                    "content": f"Complete the following truncated and incomplete content and text based on the provided content and context:",
                },
                {
                    "role": "user",
                    "content": f"Here is the text and content to complete: {truncatedContentGenResponseText} {promptStop}",
                },
            ]

            tokenTip = int(maxT // 2)
            completeContentGenResponse = oaClient.chat.completions.create(
                model=modelChoice,
                messages=finishThoughtPrompt,
                temperature=modelTemp,
                max_tokens=tokenTip,
                top_p=topP,
                frequency_penalty=fPen,
                presence_penalty=pPen,
                stop=[promptStop],
            )
            completeContentGenResponseText = completeContentGenResponse.choices[
                0
            ].message.content

            fullContentGenText = (
                truncatedContentGenResponseText + completeContentGenResponseText
            )
            cleanFinshThoughtPrompt = listToString(finishThoughtPrompt)
            contentGenInfoTrunc = {
                "model": modelChoice,
                "messages": cleanFinshThoughtPrompt,
                "responseText": completeContentGenResponseText,
                "temperature": modelTemp,
                "max_tokens": tokenTip,
                "top_p": topP,
                "frequency_penalty": fPen,
                "presence_penalty": pPen,
            }

            return fullContentGenText, {
                "contentGenInfo": contentGenInfo,
                "contentGenInfoTrunc": contentGenInfoTrunc,
            }

    except Exception as e:
        fullContentGenText = f"Error ChatComp {e}"
        return fullContentGenText, contentGenInfo


def reportContentDiffs(modelChoice, srcText, genText):
    gr.Info(f"Generating report on Differences of Versions...")
    uniquePortionsPrompt = [
        {
            "role": "system",
            "name": "Assistant",
            "content": f"Task: Identify and show the unique portions between the Source Text and the Generated Variant Text provided.",
        },
        {"role": "user", "content": f"Source Text: {srcText} "},
        {"role": "user", "content": f"Generated Variant Text: {genText} "},
        {
            "role": "user",
            "content": f"Find, Identify, and show the unique and varied portions between the Source Text and Generated Variant Text in a suscintly formated report highlighting the differences. Do NOT include any additional banter, dialog, commentary, or conversation ONLY analyze and provide the report on the differences between the two texts. {promptStop}",
        },
    ]

    tokensNeeded = tokenCounter(f"{srcText}{genText}{genText}")

    try:
        contentDiffsResponse = oaClient.chat.completions.create(
            model=modelChoice,
            messages=uniquePortionsPrompt,
            temperature=0.33,
            max_tokens=tokensNeeded,
            top_p=1,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            stop=[promptStop],
        )
        contentDiffsResponseText = contentDiffsResponse.choices[0].message.content

        return contentDiffsResponseText

    except Exception as e:
        contentDiffsResponseText = f"Error ChatComp {e}"
        return contentDiffsResponseText


def validateModelChoiceCapacity(
    fullPromptText: str,
    maxT: int,
    modelChoice: str,
):
    try:
        e = ""
        modelChoiceOrg = "org"
        modelChoiceNew = "new"
        encoding = tiktoken.get_encoding("cl100k_base")
        fullPromptTokenCount = len(encoding.encode(fullPromptText))
        gr.Info(f"Validating Model For Content Size...{modelChoice}")
        modelChoiceMaxTok = modelsMaxTokens.get(modelChoice)
        modelChoiceAltered = False
        if modelChoiceMaxTok <= fullPromptTokenCount - maxT:
            modelChoiceAltered = True
            modelChoiceOrg = modelChoice
            suitable_models = sorted(
                modelsMaxTokens.items(), key=lambda x: x[1], reverse=True
            )
            for model, maxTok in suitable_models:
                if maxTok >= fullPromptTokenCount:
                    modelChoice = model
                    modelChoiceNew = model
            gr.Info(f"Updating Model For Content Size...{modelChoice}")
        return modelChoice
    except Exception as e:
        er = f"Error ModelValidation {e}"
        return er


def tokenCounter(contentToCount):
    encoding = tiktoken.get_encoding("cl100k_base")
    contentToCountString = str(contentToCount)
    fullContentTokenCount = len(encoding.encode(contentToCountString))
    countOfTokens = int(fullContentTokenCount)
    return countOfTokens
