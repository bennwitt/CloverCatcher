import os
import sys
import tiktoken
import gradio as gr
from urllib.parse import urlparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from enviros.envInfo import *
from models.vars import *
from enviros.envInfo import *
from datetime import datetime
from convoCosSineSECs import *
from arangoEngine import *


def aiConvoEngineSECs(
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

    similarList, contentTextSimilar, contentLOCsSimilar, contentBodyText = (
        getSimilarEmbeddingsSECs(
            aiConvoInput,
            embeddingModel,
            sourceContentCollection,
            sourceContentTextEmbeddingField,
            contentThreshold,
            top_n=7,
        )
    )

    contentText = contentTextSimilar  # + contentTextDistance
    contentRef = contentRefSimilar  # + contentUrlsDistance
    if not contentText:
        convoHistory = convoHistory or []
        convoOutputText = noSimilarContentConvo
        convoHistory.append(((aiConvoInput, convoOutputText)))
        aiConvoSpace = convoHistory
        return (noSimilarContent, convoHistory, aiConvoSpace)

        textGenCompletions, textGenCompletionInfo = primeThePromptAndGenText(
            agentFunction,
            robotChatInput,
            contentText,
            robotResponseScope,
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
        chatHistory = chatHistory or []
        chatOutputText = textGenCompletions
        chatHistory.append(((robotChatInput, chatOutputText)))

    metaData = {"similarityList": similarList}  # , "distanceList": distanceList}

    writeToArangoDB(
        modelChoice,
        contentText,
        robotResponseScope,
        robotChatInput,
        chatOutputText,
        chatHistory,
        metaData,
    )
    robotChatSpace = chatHistory
    contentLinks = update_clickable_links(contentLOCs)
    return (contentBodyText, contentText, contentLinks, chatHistory, robotChatSpace)


def format_links_as_html(urls):
    header_html = '<h3 style="text-align: center; font-weight: bold;">Response Content Sources</h3>'
    links_html = []
    for url in urls:
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip("/").split("/")
        label = (
            path_parts[-1] if path_parts else parsed_url.netloc
        )  # Use the last part of the path as label, fallback to domain
        link_html = '<a href="{0}" target="_blank">{1}</a>'.format(url, label)
        links_html.append(link_html)

    formatted_html = header_html + "<br><br>".join(links_html)
    return formatted_html


def update_clickable_links(urls):
    if urls:
        formatted_html = format_links_as_html(urls)

    else:
        formatted_html = ""
    return formatted_html
