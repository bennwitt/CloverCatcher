# Last modified: 2025-02-28 19:21:10
# Version: 0.0.129
import tiktoken
import random
import gradio as gr
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Tuple, Any, Union
from engines.models.appDataModel import CopyThatData as copyThatObj
from engines.models.appDataModel import PersonaStyleData as personaStyleConf
from engines.util.zTextEngine import *
from engines.util.zDataEngine import *
from engines.util.zFileEngine import *
from engines.util.zTimeEngine import *


def buildVariantGenerationPrompt(sesh):
    knowledgeScope = ""
    completeUserDirectivePrompt = ""
    lengthOfVariationPrompt = ""
    levelOfVariationPrompt = ""

    promptText = sesh["personaStyleConf"].promptContentDict
    personaConfObj = sesh["personaStyleConf"]
    personaConf = {
        key: value if value else None for key, value in asdict(personaConfObj).items()
    }

    assistantName = personaConf["assistantName"]
    prePromptTextInput = promptText["prePromptTextInput"]
    sourceContentTextInput = promptText["sourceContentTextInput"]
    contentSwipeTextInput = promptText["contentSwipeTextInput"]
    supplementalContentText = promptText["supplementalContentText"]
    levelOfVariation = personaConf["levelOfVariation"]
    lengthOfVariation = personaConf["lengthOfVariation"]
    postPromptTextInput = promptText["postPromptTextInput"]
    prePrompt = ""
    supplementalContentPrompt = ""
    swipeFormatGuideContentPrompt = ""
    postPrompt = ""
    noFluffPrompt = "Only output the requested content—no explanations, elaboration, preamble, follow-up, or additional text. Strictly follow the directive with no commentary or justifications."
    useInternetKnowledge = f"When performing tasks you provide and introduce new information from other sources and knowledge you have in the contents domain. Reference your knowledge from the Internet that may be related to the provided contents domain, affiliations, and associations."
    noInternetKnowledge = f"When performing tasks you DO NOT introduce any new information. Focus SOLEY ON the context, subject and topic of the content provided. If there is no relevant or correlation found between the provided content in your interactions, you uniquely explain with metaphors and simile that results are best with interactions contextualy related and relevant with the content subject matter and domain."

    sourceCharCount = len(sourceContentTextInput)
    sourceTokenCount = tokenCounter(sourceContentTextInput)

    steriletext, orgWordCount, orgCharCount, clnWordCount, clnCharCount = (
        saniCountAndClean(sourceContentTextInput)
    )

    if lengthOfVariation is None:
        lengthOfVariationPrompt = f"Generate a version of the source content of approximately {clnWordCount} words long, ensuring variation while retaining the full meaning, context, and impact."

    else:
        targetWordCount = lengthOfVariation // 5

        if lengthOfVariation > sourceCharCount:
            lengthOfVariationPrompt = (
                f"Expand the source content meaningfully to approximately {targetWordCount} words "
                f"while maintaining coherence, clarity, and impact. Elaborate where beneficial, add context, "
                f"explanations, or supporting details to naturally extend the generated text variation."
            )

        elif lengthOfVariation < sourceCharCount:
            lengthOfVariationPrompt = (
                f"Condense the source content to approximately {targetWordCount} words, retaining "
                f"its key message, clarity, and emotional impact. Prioritize conciseness by removing redundant phrases, "
                f"simplifying expressions, and focusing on core ideas for the generated text variation."
            )

        else:
            lengthOfVariationPrompt = (
                f"Generate a variation of similar length of {targetWordCount} words while maintaining "
                f"the source contents message, tone, and clarity."
            )

    if lengthOfVariation == 160:
        lengthOfVariationPrompt = (
            f"Generate a concise variant suitable for a single SMS message ~160 characters while preserving "
            f"the key message and emotional impact of the source content."
        )

    elif lengthOfVariation == 280:
        lengthOfVariationPrompt = (
            f"Generate a variant optimized for a Twitter post ~280 characters that is engaging, clear, and concise, "
            f"while maintaining the source content's intent."
        )

    elif lengthOfVariation == 1200:
        lengthOfVariationPrompt = (
            f"Generate a variant suitable for an Instagram post ~1200 characters that balances brevity with emotional resonance, "
            f"ensuring the message remains impactful and engaging based on the source content."
        )

    if levelOfVariation == "Stick to the Original Idea":
        levelOfVariationPrompt = "Maintain the original structure and message with minimal modifications while improving clarity or flow if necessary."
        fPen = 0.03
        pPen = 0.03

    elif levelOfVariation == "Balanced Creativity and Relevance":
        # A balance between original and variation
        levelOfVariationPrompt = "Introduce moderate creativity while ensuring the message retains its emotional and contextual integrity."
        fPen = 0.25
        pPen = 0.25
    else:
        # More adventurous variation
        levelOfVariationPrompt = "Explore a more creative and engaging variant while keeping the message's core meaning, intent, and impact intact."
        fPen = 0.51
        pPen = 0.51

    if prePromptTextInput != None:
        prePrompt = prePromptTextInput

    if supplementalContentText != None:
        supplementalContentPrompt = f"""Supplemental Content: You will incorporate the supplemental information where contextually appropriate the supplemental content may contain insights and new visionary outlooks, strategic goals, rules and regulations, vocabulary, messeging, branding, facts and figures, concepts and ideas the supplemental content is for you to weave and icorporate into the new generated variant based upon the source content while considering and accounting for the level of variation directive, review, analyze, extract a deep understanding and determine the key points, identify language, vocabulary, uncover insights, find the corelations and contridictions with the provided source content and the provided supplemental content. Here is the supplemental content to incorporate where contextually appropriate: {supplementalContentText}"""

    if contentSwipeTextInput != None:
        swipeFormatGuideContentPrompt = f"""Swip Content and Template: The format, structure of your generated variant based on the context of the source is to be determined by you analyzing the text provided called 'swipe text' for its overall layout, composition, style, and formatting scheme. Identify the key structural features, stylistic elements, and formatting choices that define its presentation. Then, apply those same features to the newly generated content to ensure it follows the same visual and structural organization. Maintain consistency in headings, paragraph structure, spacing, bullet points, and any other distinct formatting elements you observe. Incorporate only its layout, composition, style, and formatting scheme. Here is the Swipe Text: {contentSwipeTextInput}"""

    if postPromptTextInput != None:
        postPrompt = postPromptTextInput

    establishSystemBasePrompt = f"""You are {assistantName} a masterful copywriting replicator, capable of deeply understanding messaging, flawlessly duplicating any message while adapting it to new causes, new context, new sentiment, new challenges, and generating precise variations that maintain the original emotion, spirit, tone, and impact."""
    establishSelfBasePrompt = f"""I will provide content for you to thoroughly review and analyze. Your task is to break it down into its key components—identifying the core message, emotional drivers, psychological triggers, tone, style, and intent. Extract the most impactful elements, themes, and structural patterns, gaining a deep contextual understanding."""

    assistantDirectiveBasePrompt = f"""{assistantName}, with your insights from your review and analyze, generate precise variations that align with additional guidance regarding the following: The length of the new variation: {lengthOfVariationPrompt} The level of variation to generate: {levelOfVariationPrompt} Here is the source content for you to thoroughly review and analyze for your task of generating a variation based upon the directives: {sourceContentTextInput}. {noFluffPrompt} """

    if personaConf["knowledgeScope"] == False:
        knowledgeScope = noInternetKnowledge
        modelTemp = 0.25

    else:
        knowledgeScope = useInternetKnowledge
        modelTemp = personaConf["modelTemp"]

    completeUserDirectivePrompt = f"{assistantDirectiveBasePrompt} {prePrompt} {supplementalContentPrompt} {swipeFormatGuideContentPrompt}"

    contentVariationPrompt = [
        {
            "role": "system",
            "name": assistantName,
            "content": f"{establishSystemBasePrompt} {knowledgeScope}",
        },
        {
            "role": "user",
            "content": f"{establishSelfBasePrompt} {completeUserDirectivePrompt} {postPrompt} {knowledgeScope} {promptStop}",
        },
    ]

    fullPromptString = ""
    encoding = tiktoken.get_encoding("cl100k_base")
    fullPromptString = str(contentVariationPrompt)

    fullPromptTokenCount = len(encoding.encode(fullPromptString))
    scaling_factor = min(
        1 + personaConf["maxTokens"] / 175, 1.2
    )  # Caps at 1.2x increase
    fullPromptTokenCountCal = fullPromptTokenCount * scaling_factor
    genMaxTokens = int(fullPromptTokenCountCal)
    print(
        f"fullprompt char{len(fullPromptString)} tok{fullPromptTokenCount} tokbuff{fullPromptTokenCount}"
    )

    completePrompt = contentVariationPrompt

    return genMaxTokens, modelTemp, fPen, pPen, completePrompt


def tokenCounter(contentToCount):
    encoding = tiktoken.get_encoding("cl100k_base")
    contentToCountString = str(contentToCount)
    fullContentTokenCount = len(encoding.encode(contentToCountString))
    countOfTokens = int(fullContentTokenCount)
    return countOfTokens
