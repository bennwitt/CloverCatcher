import os
import sys
import tiktoken
import gradio as gr
from urllib.parse import urlparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def aiConvoEngineVAXs(
    sourceContentCollection,
    generatedImageInsightText,
    aiConvoInput,
    aiResponseScope,
    domainTopic,
    responseLength,
    responseTone,
    responseFormat,
    energyLevel,
    modelTemp,
    modelChoice,
    convoHistory=[],
):
    if aiConvoInput == "":
        aiConvoInput = "Determine the people, places, dates, facts, locations, subject and topics that are available in the content. Generate an interesting response that is engaing and exploring new ways to interact and converse with you"

    aiConvoInput = aiConvoInput.strip()
    # Database writes

    if not generatedImageInsightText:
        convoHistory = convoHistory or []
        convoOutputText = "noContentConvo"
        convoHistory.append(((aiConvoInput, convoOutputText)))
        aiConvoSpace = convoHistory
        return (noSimilarContent, convoHistory, aiConvoSpace)

    textGenCompletions, textGenCompletionInfo = primeThePromptAndGenText(
        aiConvoInput,
        generatedImageInsightText,
        aiResponseScope,
        domainTopic,
        responseLength,
        responseTone,
        responseFormat,
        energyLevel,
        modelTemp,
        modelChoice,
    )
    if textGenCompletions == "" or "Error" in textGenCompletions:
        raise gr.Error(
            "There was an issue with our chat. Can you let someone know? "
            + textGenCompletions
        )
    else:
        convoHistory = convoHistory or []
        convoOutputText = textGenCompletions
        convoHistory.append(((aiConvoInput, convoOutputText)))

    aiConvoSpace = convoHistory

    return (convoHistory, aiConvoSpace)
