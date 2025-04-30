# Last modified: 2025-03-01 04:23:06
# Version: 0.0.65
from textwrap import wrap
import uuid
import base64
import hashlib
import os
import re
import json
from typing import Any, Union, List
from collections import defaultdict


def filterListItems(listFilterText, dirtyList):
    cleanList = [item for item in dirtyList if item and listFilterText not in item]
    return cleanList


def validateItemsFilterListItems(validItemTypesList, listFilterText, dirtyList):
    cleanValidList = [
        item
        for item in dirtyList
        if item  # non-empty/falsy check
        and any(
            validtype in item for validtype in validItemTypesList
        )  # partial match in valid list
        and (listFilterText not in item)  # exclude partial matches of filter text
    ]
    return cleanValidList


def dict_to_json(data, indent=4):
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        return f"Error converting to JSON: {e}"


def dict_to_markdown_json(d: dict) -> str:
    json_string = json.dumps(d, indent=2)
    markdown_block = f"```json\n{json_string}\n```"
    return markdown_block


def encodeTextForId(textString):
    # Encode the URL using URL-safe Base64 encoding
    textId = base64.urlsafe_b64encode(textString.encode()).decode()
    return textId


def encode_url_to_contentID(url):
    # Encode the URL using URL-safe Base64 encoding
    contentID = base64.urlsafe_b64encode(url.encode()).decode()
    return contentID


def encodeFileName(pathString):
    # Encode the URL using URL-safe Base64 encoding
    contentID = base64.urlsafe_b64encode(pathString.encode()).decode()
    return contentID


def decode_contentID_to_url(contentID):
    # Decode the URL-safe Base64 encoded contentID back to the original URL
    url = base64.urlsafe_b64decode(contentID.encode()).decode()
    return url


def makeGuid():
    unique_guid = uuid.uuid4()
    return str(unique_guid)


def listToString(myList: list) -> str:
    def flatten(item):
        """Recursively flatten lists and dictionaries into strings."""
        if isinstance(item, dict):
            return " ".join(f"{k}: {flatten(v)}" for k, v in item.items())
        elif isinstance(item, list):
            return " ".join(flatten(i) for i in item)
        else:
            return str(item).strip()

    return " ".join(flatten(item) for item in myList if item)


def stringToList(stringText: str) -> list:
    split_pattern = r"[;\n]+"

    newList = re.split(split_pattern, stringText)
    newList = [item.strip() for item in newList if item.strip()]
    return newList


def list2dict(data: List[Union[tuple, Any]]) -> dict:
    d = defaultdict(list)
    if all(isinstance(i, tuple) and len(i) == 2 for i in data):
        for k, v in data:
            d[k].append(v)
    else:
        for k, v in zip(data[::2], data[1::2]):
            d[k].append(v)

    return {k: v[0] if len(v) == 1 else v for k, v in d.items()}


def convertDictToMd(data):
    if not data:
        return "No data available."

    # Dynamically get the field names from the first dictionary
    fields = list(data[0].keys())

    markdown_text = "Retrieved Assets Based On Engagement Metrics\n\n"

    for item in data:
        for field_name in fields:
            field_value = item.get(field_name, "N/A")
            markdown_text += f"{field_name}: {field_value}\n"

        markdown_text += "\n"  # Add extra newline for spacing between items

    return markdown_text


def extractFilename(file_path):
    fileName = os.path.basename(file_path)
    parentFolder = os.path.dirname(file_path)
    return parentFolder, fileName


def parse_vimeo_url(url):
    match = re.search(r"vimeo\.com/(?:showcase/)?(\d+)(?:/video/(\d+))?", url)
    if match:
        return match.group(2) if match.group(2) else match.group(1)
    else:
        return None


def only_unique_items(combined_list: list):
    # combined_list = list1 + list2 + list3
    return list(set(combined_list))


def makeStringList(url_string):
    delimiters = [" ", "\n", ",", ";"]
    for delimiter in delimiters:
        url_string = url_string.replace(delimiter, " ")
    url_list = url_string.split(" ")
    cleanListURLs = [url.strip() for url in url_list if url.strip()]
    return cleanListURLs


def sanitext(dirtytext: str):
    pattern = r"[^0-9a-zA-Z\s_,.$!%&@*+><:#='()-?]+"
    cleantext = re.sub(pattern, " ", dirtytext)
    cleanertext = cleantext.replace("\n", " ")
    cleanesttext = " ".join(cleanertext.split())
    steriletext = cleanesttext.strip()
    return steriletext


def saniCountAndClean(dirtytext: str):
    # Count words and characters before cleaning
    orgWordCount = len(dirtytext.split())
    orgCharCount = len(dirtytext)

    # Cleaning process
    pattern = r"[^0-9a-zA-Z\s_,.$!%&@*+><:#='()-?]+"
    cleantext = re.sub(pattern, " ", dirtytext)
    cleanertext = cleantext.replace("\n", " ")
    cleanesttext = " ".join(cleanertext.split())
    steriletext = cleanesttext.strip()

    # Count words and characters after cleaning
    clnWordCount = len(steriletext.split())
    clnCharCount = len(steriletext)

    return steriletext, orgWordCount, orgCharCount, clnWordCount, clnCharCount


def cleanTxtForLLM(dirtytext: str):
    pattern = r"[^0-9a-zA-Z\s_,.$!%&@+><:='()-?]+"
    cleantext = re.sub(pattern, " ", dirtytext)
    cleanertext = cleantext.replace("\n", " ")
    cleanesttext = " ".join(cleanertext.split())
    steriletext = cleanesttext.strip()
    return steriletext


def prepFolderName(inputString):
    pattern = r"[^0-9a-zA-Z\s_.-]+"
    cleanString = re.sub(pattern, "", inputString)
    cleanerString = cleanString.replace(" ", "")
    sterileFolderName = cleanerString.strip()
    return sterileFolderName


def cleanRobotMarkUp(text: str) -> str:
    cleaned_text = re.sub(r"\*\*|###|:", "", text)
    return cleaned_text.strip()


def generateHash(filename):
    # Create a SHA-256 hash of the filename
    sha256_hash = hashlib.sha256(filename.encode()).digest()
    # Encode the hash in URL-safe Base64 and decode to a string
    base64_hash = base64.urlsafe_b64encode(sha256_hash).decode("utf-8").rstrip("=")
    # Take the first 12 characters
    short_hash = base64_hash[:12]
    return short_hash


def replacePathParts(input_string):
    # Replace '/img/' with '/vid/'
    step1 = input_string.replace("/img/", "/vid/")

    # Replace '.x.*.png' with '.mp4'
    step2 = re.sub(r"\.x\..*?\.png", ".mp4", step1)

    return step2


def cleanUpPdfTextNoise(pdfText):
    cleaned = re.sub(r"\.{2,}", ".", pdfText)

    cleaned = re.sub(r"\s{2,}", " ", cleaned)

    cleaned = cleaned.replace("\n", "")

    cleanedPdfText = cleaned.strip()

    return cleanedPdfText


def contentTextSplitter(contentText, chunkSize, overlap):
    contentTextSplits = []
    initialSplits = wrap(
        contentText,
        chunkSize,
        expand_tabs=False,
        break_on_hyphens=False,
        placeholder=" ",
        break_long_words=False,
        drop_whitespace=True,
    )
    for i in range(len(initialSplits)):
        if i > 0:
            overlap_text = initialSplits[i - 1][-overlap:]
            combined_text = overlap_text + initialSplits[i]
            contentTextSplits.append(combined_text)
        else:
            contentTextSplits.append(initialSplits[i])
    return contentTextSplits


def clean_json(data):
    if isinstance(data, dict):
        return {k: clean_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_json(i) for i in data]
    elif isinstance(data, str):
        return " ".join(data.split())
    else:
        return data


def removeFieldValuesNone(data):
    if isinstance(data, dict):
        return {
            k: removeFieldValuesNone(v)
            for k, v in data.items()
            if v != "NONE" and v is not None
        }
    elif isinstance(data, list):
        return [removeFieldValuesNone(item) for item in data]
    else:
        return data


def concatenateDictText(data):
    if isinstance(data, dict):
        # Recursively concatenate all text from dictionary values
        return " ".join(concatenateDictText(v) for v in data.values())
    elif isinstance(data, list):
        # Concatenate list items if any
        return " ".join(concatenateDictText(item) for item in data)
    else:
        # Assume the value is a string if it's not a dict or list
        return str(data)


def count_words(text):
    return len(text.split())
