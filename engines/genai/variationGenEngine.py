# Last modified: 2025-03-01 04:52:12
# Version: 0.0.190
from datetime import datetime

import gradio as gr
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Tuple, Any, Union
from engines.models.appDataModel import CopyThatData as copyThatObj
from engines.models.appDataModel import PersonaStyleData as personaStyleConf
from engines.genai.contentVariationPrompts import buildVariantGenerationPrompt
from engines.genai.contentPersonaPrompts import (
    buildVariantGenerationPersonaPrompt,
)

from engines.genai.contentVariationEngine import (
    genContentVariationsOpenai,
    reportContentDiffs,
)
from engines.arango.arangoBaseEngine import arangoAction
from engines.util.zTextEngine import count_words, saniCountAndClean, list2dict
from engines.logger.activityLoggingEngine import logActivity
from engines.util.zTimeEngine import getNowDateTime
from aiDojo.aiSenseiLearnings import sendAiDojo


def genContentVariations(
    authorizationStatus,
    authToken,
    userEmailAddress,
    prePromptTextInput,
    sourceContentTextInput,
    contentSwipeTextInput,
    supplementalContentText,
    clientRepoSelection,
    clientSwipesSelection,
    knowledgeScope,
    assistantTaskDirective,
    modelChoice,
    modelTemp,
    numberOfVariations,
    lengthOfVariation,
    levelOfVariation,
    personaToggle,
    rolePersona,
    targetAudience,
    responsePurpose,
    domainTopic,
    energyLevel,
    responseTone,
    responseLength,
    responseFormat,
    maxTokens,
    postPromptTextInput,
    sesh,
):

    if not sourceContentTextInput:
        errMsg = "🙈 Error: Source Input Text Box cannot be empty! 🙈"
        gr.Warning(f"{errMsg}")
        return (
            errMsg,
            errMsg,
            errMsg,
            gr.Textbox(
                value="",
                placeholder=f"{userEmailAddress} Share Your Findings and Opinions",
            ),
            errMsg,
            errMsg,
            sesh,
        )

    promptContentDict = {
        key: value if value else None
        for key, value in {
            "prePromptTextInput": prePromptTextInput,
            "sourceContentTextInput": sourceContentTextInput,
            "contentSwipeTextInput": contentSwipeTextInput,
            "supplementalContentText": supplementalContentText,
            "postPromptTextInput": postPromptTextInput,
        }.items()
    }

    # if "personaStyleConf" not in sesh:
    #    sesh["personaStyleConf"] = personaStyleConf()

    personaConf = sesh["personaStyleConf"]

    # Update the instance with the latest values
    personaConf.update(
        personaToggle=personaToggle,
        assistantTaskDirective=assistantTaskDirective,
        knowledgeScope=knowledgeScope,
        modelChoice=modelChoice,
        modelTemp=modelTemp,
        numberOfVariations=numberOfVariations,
        lengthOfVariation=lengthOfVariation,
        levelOfVariation=levelOfVariation,
        rolePersona=rolePersona,
        targetAudience=targetAudience,
        responsePurpose=responsePurpose,
        domainTopic=domainTopic,
        energyLevel=energyLevel,
        responseTone=responseTone,
        responseLength=responseLength,
        responseFormat=responseFormat,
        maxTokens=maxTokens,
        promptContentDict=promptContentDict,
    )

    # Store the updated instance back in the session
    sesh["personaStyleConf"] = personaConf

    sesh["copyThatObj"].appName = appName
    sesh["copyThatObj"].clientName = clientName
    sesh["copyThatObj"].mediaLibraryRoot = mediaLibraryRoot

    sesh = setStorageVariables(sesh)

    fullGeneratedContentText = ""
    generatedContentReport = ""
    completePrompt = ""
    genContentInfo = {}

    totalNumberOfVariations = numberOfVariations
    verCount = 0
    genMaxTokens = 0
    generatedContentReport += (
        f"\n\n====Variation Report for {totalNumberOfVariations} versions.=====\n\n"
    )

    while numberOfVariations > 0:
        verCount += 1
        numberOfVariations -= 1

        variantGeneratedContentTextCollection = (
            f"Version {verCount} of {totalNumberOfVariations}:\n"
        )

        if personaToggle == True:
            genMaxTokens, modelTemp, completePrompt = (
                buildVariantGenerationPersonaPrompt(sesh)
            )

        else:
            (
                genMaxTokens,
                targetCharCount,
                targetWordCount,
                clnCharCount,
                modelTemp,
                topP,
                fPen,
                pPen,
                completePrompt,
            ) = buildVariantGenerationPrompt(sesh)

        textGenCompletions, genContentInfo = genContentVariationsOpenai(
            genMaxTokens, modelTemp, topP, fPen, pPen, modelChoice, completePrompt
        )

        # sesh["copyThatObj"].aiDojoContentList.append(
        #    (sesh["personaStyleConf"], genContentInfo)
        # )

        # aiDojoContentList = sesh["copyThatObj"].aiDojoContentList

        # aiSenseiObservations = sendAiDojo(aiDojoContentList)
        # pass
        if textGenCompletions == "" or "Error" in textGenCompletions:
            gr.Error(
                "There was an issue with our generation of Text. Can you let someone know? "
                + textGenCompletions
            )

        else:
            if lengthOfVariation == 0:
                pass

            else:
                len(textGenCompletions) >= targetCharCount
                trimTextGenCompletions, sesh = trimGenContentVariation(
                    modelChoice, textGenCompletions, sesh
                )
                trimLen = len(trimTextGenCompletions)
                textGenCompletions = trimTextGenCompletions

            genHistory = []
            srcText = sourceContentTextInput
            genText = textGenCompletions
            variantGeneratedContentTextCollection += f"{genText}\n\n"
            genHistory.append(((sourceContentTextInput, genText)))
            generatedContentReport += f"\n\nVersion {verCount}:\n"

            generatedContentReport += f"Character Count: Source : {len(sourceContentTextInput)} Variant : {len(genText)}\n"
            generatedContentReport += f"Word Count: Source : {count_words(sourceContentTextInput)} Variant : {count_words(genText)}\n"

            generatedContentReport += reportContentDiffs(modelChoice, srcText, genText)

        fullGeneratedContentText += variantGeneratedContentTextCollection

    dbContentPayload = {}
    dbContentPayload["timeStamp"] = getNowDateTime()
    dbContentPayload["completePrompt"] = completePrompt
    dbContentPayload["fullGeneratedContentText"] = fullGeneratedContentText
    dbContentPayload["generatedContentReport"] = generatedContentReport
    # funcStatus, funcMsg, sesh = logActivity(dbContentPayload, sesh)

    # aiSenseiWisdoms = sesh["copyThatObj"].aiDojoContentList
    # aiSenseiWisdomsDict = list2dict(aiSenseiWisdoms)
    # funcStatus, funcMsg, sesh = logActivity(aiSenseiWisdomsDict, sesh)

    return (
        "aiSenseiWisdoms",
        fullGeneratedContentText,
        generatedContentReport,
        gr.Textbox(
            value="", placeholder=f"{userEmailAddress} Share Your Findings and Opinions"
        ),
        "messageBox",
        dbContentPayload,
        sesh,
    )


def trimGenContentVariation(modelChoice, longGenText, sesh):

    promptTextDict = sesh["personaStyleConf"].promptContentDict

    promptTextDict["sourceContentTextInput"] = longGenText
    sesh["personaStyleConf"].promptContentDict = promptTextDict

    (
        genMaxTokens,
        targetCharCount,
        targetWordCount,
        clnWordCount,
        modelTemp,
        topP,
        fPen,
        pPen,
        completePrompt,
    ) = buildVariantGenerationPrompt(sesh)
    trimTextGenCompletions, genContentInfo = genContentVariationsOpenai(
        genMaxTokens, modelTemp, topP, fPen, pPen, modelChoice, completePrompt
    )

    sesh["copyThatObj"].aiDojoContentList.append(
        (sesh["personaStyleConf"], genContentInfo)
    )

    return trimTextGenCompletions, sesh
