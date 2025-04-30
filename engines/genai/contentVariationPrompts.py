# Last modified: 2025-02-28 18:40:39
# Version: 0.0.151
import tiktoken
import random
import gradio as gr
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Tuple, Any, Union
from engines.util.zTextEngine import *
from engines.util.zDataEngine import *
from engines.util.zFileEngine import *
from engines.util.zTimeEngine import *


def buildVariantGenerationPrompt(sesh):

    personaConfObj = sesh["personaStyleConf"]
    personaConf = {
        key: value if value else None for key, value in asdict(personaConfObj).items()
    }
    promptText = sesh["personaStyleConf"].promptContentDict

    assistantName = personaConf["assistantName"]

    prePromptTextInput = promptText.get("prePromptTextInput", "")
    sourceContentTextInput = promptText.get("sourceContentTextInput", "")
    contentSwipeTextInput = promptText.get("contentSwipeTextInput", "")
    supplementalContentText = promptText.get("supplementalContentText", "")
    levelOfVariation = personaConf.get("levelOfVariation", "Faithful Rewrite")
    lengthOfVariation = personaConf.get("lengthOfVariation", None)
    postPromptTextInput = promptText.get("postPromptTextInput", "")

    variConfig = variationModes.get(
        levelOfVariation, variationModes["Balanced Creativity and Relevance"]
    )
    modelTemp = variConfig["temperature"]
    topP = variConfig["top_p"]
    fPen = variConfig["frequency_penalty"]
    pPen = variConfig["presence_penalty"]
    levelOfVariationPrompt = variConfig["promptText"]

    sourceCharCount = len(sourceContentTextInput)
    steriletext, orgWordCount, orgCharCount, clnWordCount, clnCharCount = (
        saniCountAndClean(sourceContentTextInput)
    )

    textAnalysisDict = textCharWordAnalysis(sourceContentTextInput)
    avgWordLength = textAnalysisDict["AverageWordLength"]
    noFluffPrompt = "Strictly follow the directive. No preamble, explanation, justification, or additional commentary."
    useKnowledge = "Reference relevant external knowledge while ensuring coherence with the provided content."
    noKnowledge = "Do NOT introduce external knowledge. Work strictly within the provided content and context."
    knowledgeScopePrompt = useKnowledge

    if not personaConf.get("knowledgeScope"):
        knowledgeScopePrompt = noKnowledge
        modelTemp = 0.25

    if lengthOfVariation is None:
        lengthOfVariationPrompt = f"Generate a variation of approximately {clnWordCount} words, preserving meaning, context, and impact."
        targetCharCount = orgCharCount
        targetWordCount = orgWordCount
    else:
        targetCharCount = lengthOfVariation
        targetWordCount = lengthOfVariation // avgWordLength
        if lengthOfVariation > sourceCharCount:
            lengthOfVariationPrompt = f"Expand to ~{targetWordCount} words, adding clarity, depth, and context while maintaining impact."
        elif lengthOfVariation < sourceCharCount:
            lengthOfVariationPrompt = f"Condense to ~{targetWordCount} words, ensuring conciseness while retaining key messages."
        else:
            lengthOfVariationPrompt = f"Maintain a similar length (~{targetWordCount} words) while enhancing clarity and tone."

    special_length_prompts = {
        160: "Generate a concise SMS-friendly version (~160 characters) preserving the core message.",
        280: "Create an engaging Twitter post (~280 characters) while maintaining original intent.",
        1200: "Generate an Instagram-friendly variant (~1200 characters), balancing brevity and resonance.",
    }
    lengthOfVariationPrompt = special_length_prompts.get(
        lengthOfVariation, lengthOfVariationPrompt
    )

    # Content Incorporation Prompts
    supplementalContentPrompt = (
        f"Incorporate the following supplemental content contextually: {supplementalContentText}"
        if supplementalContentText
        else ""
    )

    swipeFormatGuideContentPrompt = (
        f"Ensure the generated variation adheres to the format, structure, and style of this reference: {contentSwipeTextInput}"
        if contentSwipeTextInput
        else ""
    )

    # Final Prompt Construction
    establishSystemBasePrompt = (
        f"You are {assistantName}, a masterful copywriting expert, skilled in replicating, adapting, and enhancing messaging "
        "while maintaining tone, intent, and emotional impact."
    )

    establishSelfBasePrompt = (
        "Analyze the provided content, identifying its key components: message, emotional drivers, tone, and structure. "
        "Extract the most impactful elements to inform the variation process."
    )

    assistantDirectiveBasePrompt = (
        f"{assistantName}, based on your analysis, generate a precise variation with the following directives: "
        f"\n- Length: {lengthOfVariationPrompt}"
        f"\n- Creativity Level: {levelOfVariationPrompt}"
        f"\n- Source Content: {sourceContentTextInput}"
        f"\n{noFluffPrompt}"
    )

    completeUserDirectivePrompt = " ".join(
        filter(
            None,
            [
                assistantDirectiveBasePrompt,
                prePromptTextInput,
                supplementalContentPrompt,
                swipeFormatGuideContentPrompt,
            ],
        )
    )

    contentVariationPrompt = [
        {
            "role": "system",
            "name": assistantName,
            "content": f"{establishSystemBasePrompt} {knowledgeScopePrompt}",
        },
        {
            "role": "user",
            "content": f"{establishSelfBasePrompt} {completeUserDirectivePrompt} {postPromptTextInput} {knowledgeScopePrompt}",
        },
    ]

    fullPromptString = ""
    encoding = tiktoken.get_encoding("cl100k_base")
    fullPromptString = str(contentVariationPrompt)

    fullPromptTokenCount = len(encoding.encode(fullPromptString))
    scaling_factor = min(
        1 + personaConf["maxTokens"] / 175, 0.96
    )  # Caps at 0.03x decrease
    fullPromptTokenCountCal = fullPromptTokenCount * scaling_factor
    genMaxTokens = int(fullPromptTokenCountCal)
    print(
        f"fullprompt char{len(fullPromptString)} tok{fullPromptTokenCount} tokbuff{fullPromptTokenCount}"
    )

    completePrompt = contentVariationPrompt

    return (
        genMaxTokens,
        targetCharCount,
        targetWordCount,
        clnCharCount,
        modelTemp,
        topP,
        fPen,
        pPen,
        completePrompt,
    )


def tokenCounter(contentToCount):
    encoding = tiktoken.get_encoding("cl100k_base")
    contentToCountString = str(contentToCount)
    fullContentTokenCount = len(encoding.encode(contentToCountString))
    countOfTokens = int(fullContentTokenCount)
    return countOfTokens
