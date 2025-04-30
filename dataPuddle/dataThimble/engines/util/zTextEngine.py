# Last modified: 2025-03-31 22:52:03
# Version: 0.0.62
from textwrap import wrap
import uuid
import base64
import hashlib
import json
import os
import re
import random
import string


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


def generate_guid8():
    chars = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return "".join(random.choices(chars, k=8))


def listToString(myList: list) -> str:
    # Join the list elements into a single string, separated by spaces
    return " ".join(item.strip() for item in myList if item.strip())


def stringToList(stringText: str) -> list:
    split_pattern = r"[;\n]+"

    newList = re.split(split_pattern, stringText)
    newList = [item.strip() for item in newList if item.strip()]
    return newList


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
    pattern = "[^0-9a-zA-Z\s_,.$!%&@*+><:#='()-?]+"
    cleantext = re.sub(pattern, " ", dirtytext)
    cleanertext = cleantext.replace("\n", " ")
    cleanesttext = " ".join(cleanertext.split())
    steriletext = cleanesttext.strip()
    return steriletext


def cleanTxtForLLM(dirtytext: str):
    pattern = "[^0-9a-zA-Z\s_,.$!%&@+><:='()-?]+"
    cleantext = re.sub(pattern, " ", dirtytext)
    cleanertext = cleantext.replace("\n", " ")
    cleanesttext = " ".join(cleanertext.split())
    steriletext = cleanesttext.strip()
    return steriletext


def prepFolderName(inputString):
    pattern = "[^0-9a-zA-Z\s_.-]+"
    cleanString = re.sub(pattern, "", inputString)
    cleanerString = cleanString.replace(" ", "")
    sterileFolderName = cleanerString.strip()
    return sterileFolderName.lower()


def prepCollectionName(inputString):
    pattern = "[^0-9a-zA-Z\s_.-]+"
    cleanString = re.sub(pattern, "", inputString)
    cleanerString = cleanString.replace(" ", "")
    sterileCollectionName = cleanerString.strip()
    return sterileCollectionName


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
