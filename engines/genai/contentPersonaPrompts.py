# Last modified: 2025-02-26 03:13:26
# Version: 0.0.135
import tiktoken
import random
import gradio as gr
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Tuple, Any, Union
from engines.util.zTextEngine import *
from engines.util.zDataEngine import *
from engines.util.zFileEngine import *
from engines.util.zTimeEngine import *


def buildVariantGenerationPersonaPrompt(sesh):
    knowledgeScope = ""
    completeUserDirectivePrompt = ""
    randomAct = random.choice(actAsRoleList)

    promptText = sesh["personaStyleConf"].promptContentDict
    personaConfObj = sesh["personaStyleConf"]
    personaConf = {
        key: value if value else None for key, value in asdict(personaConfObj).items()
    }

    assistantName = personaConf["assistantName"]
    rolePersona = personaConf["rolePersona"]
    domainTopic = personaConf["domainTopic"]
    prePromptTextInput = promptText["prePromptTextInput"]
    assistantTaskDirective = personaConf["assistantTaskDirective"]
    sourceContentTextInput = promptText["sourceContentTextInput"]
    contentSwipeTextInput = promptText["contentSwipeTextInput"]
    supplementalContentText = promptText["supplementalContentText"]
    responsePurpose = personaConf["responsePurpose"]
    targetAudience = personaConf["targetAudience"]
    energyLevel = personaConf["energyLevel"]
    responseTone = personaConf["responseTone"]
    responseLength = personaConf["responseLength"]
    responseFormat = personaConf["responseFormat"]
    tknWordCount = int(personaConf["maxTokens"] * 1.5)
    postPromptTextInput = promptText["postPromptTextInput"]
    prePrompt = ""
    supplementalContentPrompt = ""
    swipeFormatGuideContentPrompt = ""
    postPrompt = ""
    noFluffPrompt = "Only output the requested content—no explanations, elaboration, preamble, follow-up, or additional text. Strictly follow the directive with no commentary or justifications."

    if prePromptTextInput != None:
        prePrompt = prePromptTextInput

    if supplementalContentText != None:
        supplementalContentPrompt = f"""Review, analyze, extract a deep understanding and determine the key subjects, concepts, points, identify language, vocabulary, intent, messaging, and uncover insights and find corelations and contridictions with the provided source content. Incorporate the provided supplemental content for incorporation where contextually appropriate here is the supplemental content: {supplementalContentText}"""

    if contentSwipeTextInput != None:
        swipeFormatGuideContentPrompt = f"""Analyze the text provided called 'swipe text' for its overall layout, composition, style, and formatting scheme. Identify the key structural features, stylistic elements, and formatting choices that define its presentation, format and composition. Apply the found features, format, style and composition to the newly generated content ensure the generated version follows the same visual and structural organization. Maintain consistency in headings, paragraph structure, spacing, bullet points, and any other distinct formatting elements you observe. Incorporate only its layout, composition, style, and formatting scheme. Here is the Swipe Text: {contentSwipeTextInput}"""

    if postPromptTextInput != None:
        postPrompt = postPromptTextInput

    establishSystemBasePrompt = f"""You refer to yourself as {assistantName} a {rolePersona} you are {energyLevel} and {responseTone} in your {responseLength} responses, your rigorous knowledge, skills, and experience in {domainTopic} establishes you as an authority in all facts, feelings, emotions, behaviors, and activities that influence, impact, and are related to the {domainTopic}."""
    establishSelfBasePrompt = f"""I will provide you content to review, analyze, to gain an expert understanding of the contents intent and messaging, determine the key elements, the essence and intent of the content, gain a deep understanding of the provided content to generate versions of the content."""
    establishAssistantPrompt = f"""I am called {assistantName}, and I am very {energyLevel} and knowledgable in all aspects of {domainTopic} domain. How shall I be of assistance to you for {assistantTaskDirective}?"""

    userOffContextPrompt = f"""{assistantName}, I have a request for you. I will be providing source content and materials related to the {domainTopic} domain. You will be {responseLength} and use your knowledge and insights based in the {domainTopic} domain and respond to my input. Here is my input: Why does rain occur when it is Tuesday? Here is the content: Universally an old clock in the town square realized a breeze as the cat leaped onto the cobblestones."""
    assistantOffContextResponse = f"""I am your {assistantName}, I am obliged to refer to only the provided source materials, content, context and stay relevant in my responses. Please let me know if you would like to alter the way we interact."""

    assistantDirectiveBasePrompt = f"""I have a task for you {assistantName}, {randomAct} {rolePersona}, analyze and determine the provided materials and content for its facts, message, essence, intent, and purpose, use your knowledge and insights based in the {domainTopic} domain for this directive task, {assistantTaskDirective} that is intended for {targetAudience}. The purpose and goal is {responsePurpose} with a tone that is {responseTone} while being {responseLength} in length, the format must be {responseFormat}. Here is the source content that is the focus for the task: {sourceContentTextInput} {noFluffPrompt}."""

    useInternetKnowledge = f"When performing tasks you provide and introduce new information from other sources and knowledge you have in the {domainTopic} domain. Reference your knowledge from the Internet that may be related to the provided {domainTopic} content provided."
    noInternetKnowledge = f"When performing tasks you DO NOT introduce any new information. Focus SOLEY ON the context, subject and topic of the content provided. If there is no relevant or correlation found between the provided content in your interactions, you {responseTone} explain results are best with interactions contextualy related and relevant with the content subject matter and domain."

    if personaConf["knowledgeScope"] == False:
        knowledgeScope = noInternetKnowledge
        modelTemp = 0.25

    else:
        knowledgeScope = useInternetKnowledge
        modelTemp = personaConf["modelTemp"]

    completeUserDirectivePrompt = f"{assistantDirectiveBasePrompt} {prePrompt} {supplementalContentPrompt} {swipeFormatGuideContentPrompt}"

    personaPrompt = [
        {
            "role": "system",
            "name": assistantName,
            "content": f"{establishSystemBasePrompt} {knowledgeScope}",
        },
        {
            "role": "user",
            "content": f"{establishSelfBasePrompt}",
        },
        {
            "role": "assistant",
            "content": f"{establishAssistantPrompt}",
        },
        {
            "role": "user",
            "content": f"{userOffContextPrompt} {noInternetKnowledge}",
        },
        {
            "role": "assistant",
            "content": f"{assistantOffContextResponse}",
        },
        {
            "role": "user",
            "content": f"{establishSelfBasePrompt} {completeUserDirectivePrompt} {postPrompt} {knowledgeScope} {promptStop}",
        },
    ]

    fullPromptString = ""

    encoding = tiktoken.get_encoding("cl100k_base")
    fullPromptString = str(personaPrompt)
    fullPromptTokenCount = len(encoding.encode(fullPromptString))
    scaling_factor = min(
        1 + personaConf["maxTokens"] / 175, 1.2
    )  # Caps at 1.2x increase
    fullPromptTokenCountCal = fullPromptTokenCount * scaling_factor

    genMaxTokens = int(fullPromptTokenCountCal)
    print(
        f"fullprompt char{len(fullPromptString)} tok{fullPromptTokenCount} tokbuff{fullPromptTokenCount}"
    )
    completePrompt = personaPrompt

    return genMaxTokens, modelTemp, completePrompt
