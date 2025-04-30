# Last modified: 2025-02-26 06:39:34
# Version: 0.0.29
from textwrap import wrap
import uuid
import base64
import hashlib
import json
import time
from functools import wraps
import sys
import os
import re
from datetime import datetime

from dataclasses import dataclass, field, asdict, is_dataclass

from typing import List, Optional, Dict, Tuple, Any, Union

import string
import pandas as pd


def textCharWordAnalysis(text):
    words = text.translate(str.maketrans("", "", string.punctuation)).split()
    word_length_counts = {}

    for word in words:
        length = len(word)
        word_length_counts[length] = word_length_counts.get(length, 0) + 1

    total_words = len(words)
    word_length_pct = {
        length: (count / total_words) * 100
        for length, count in word_length_counts.items()
    }

    total_chars = sum(len(word) for word in words)
    avg_word_length = total_chars / total_words if total_words > 0 else 0

    deviation_threshold = (
        avg_word_length * 1.5
    )  # Consider a word a curve breaker if 1.5x the average
    curve_breakers = [
        length for length in word_length_counts if length > deviation_threshold
    ]

    space_count = text.count(" ")
    punctuation_count = sum(1 for char in text if char in string.punctuation)

    df_word_length_pct = pd.DataFrame(
        list(word_length_pct.items()), columns=["Word Length", "Percentage"]
    )
    df_word_length_pct = df_word_length_pct.sort_values(by="Word Length")

    return {
        "AverageWordLength": avg_word_length,
        "CurveBreakerWordLengths": curve_breakers,
        "SpaceCount": space_count,
        "PunctuationCount": punctuation_count,
    }


def objectConverter(sourceData, sourceDataType):
    if sourceDataType == "dataclass":
        newData = asdict(sourceData)

    elif sourceDataType in ["set", "tuple"]:
        newData = list(sourceData)

    else:
        newData = str(sourceData)

    newDataType = evaluateObjectType(newData)

    return newDataType, newData


def evaluateObjectType(thang):
    if thang is None or (
        isinstance(thang, (str, list, tuple, dict, set)) and len(thang) == 0
    ):
        return "empty"
    elif isinstance(thang, str):
        return "string"
    elif isinstance(thang, list):
        if all(isinstance(i, list) for i in thang):
            return "list of lists"
        else:
            return "list"
    elif isinstance(thang, tuple):
        return "tuple"
    elif isinstance(thang, dict):
        return "dict"
    elif isinstance(thang, set):
        return "set"
    elif is_dataclass(thang):
        return "dataclass"
    elif isinstance(thang, (bytes, bytearray)):
        return "bytes"
    elif hasattr(thang, "__iter__") and not isinstance(
        thang, (str, list, dict, tuple, set)
    ):
        return "generator/iterator"
    elif isinstance(thang, complex):
        return "complex number"
    else:
        return "unknown type"


def convertDataClassToDict(obj):
    """Convert the object to a dictionary if it's a dataclass."""
    if is_dataclass(obj):
        return asdict(obj)  # Convert to dictionary
    return obj


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
