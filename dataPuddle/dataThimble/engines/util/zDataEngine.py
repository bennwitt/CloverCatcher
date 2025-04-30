# Last modified: 2025-04-02 20:31:38
# Version: 0.0.31

from dataclasses import dataclass, field, asdict, is_dataclass


def groupListItems(sourceList: list, groupItemSize: int):
    return [
        " ".join(sourceList[i : i + groupItemSize])
        for i in range(0, len(sourceList), groupItemSize)
    ]


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


def removeEmptyListItems(data):
    return [item for item in data if item not in (" ", "", None)]


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
