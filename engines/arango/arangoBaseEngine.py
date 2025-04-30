# Last modified: 2025-01-29 23:24:34
# Version: 0.0.77
import sys
import os
import re
from arango import ArangoClient
import gradio as gr

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Any, Union

from engines.util.zTextEngine import *
from engines.util.zDataEngine import *
from engines.util.zFileEngine import *
from engines.util.zTimeEngine import *


# Flow:
# arangoAction ->
# ConnectToArangoDB(make db if none) -> Return to arangoAction
# arangoAction -> saveToArangoDB ->
# arangoCollectionConnection(make collection if none, save one doc in it) -> Return to saveToArangoDB
# saveToArangoDB (inserts content)


def arangoAction(
    arangoDB: str,
    collectionName: str,
    contentToSave: Union[List[Any], str, Dict[str, Any]],
    sesh: any,
) -> Tuple[bool, str, Any]:

    dataType = evaluateObjectType(contentToSave)  # Arango need dict, list, string
    if not dataType in ["list", "dict", "str"]:
        return False, f"contentToSave is {dataType}. Convert to list, dict, str.", sesh

    funcMsg = "arangoAction"
    try:
        funcStatus, funcMsg, argDBC = connectToArangoDB(
            arangoHost, arangoDB, arangoUser, arangoPwd
        )
        if not funcStatus:
            return False, funcMsg, sesh
        funcStatus, funcMsg, sesh = saveToArangoDB(
            argDBC, collectionName, contentToSave, sesh
        )
        return funcStatus, funcMsg, sesh
    except Exception as e:
        funcMsg = f"Error On arangoAction {e}"
        print(funcMsg)
        return False, funcMsg, sesh


def connectToArangoDB(arangoHost, arangoDB, arangoUser, arangoPwd):
    try:
        dbClient = ArangoClient(hosts=arangoHost)
        sysDB = dbClient.db("_system", username=arangoUser, password=arangoPwd)
        if not sysDB.has_database(arangoDB):
            sysDB.create_database(arangoDB)

        argDBC = dbClient.db(arangoDB, username=arangoUser, password=arangoPwd)
        return True, "Success", argDBC

    except Exception as e:
        funcMsg = f"Error On connectToArangoDB {e}"
        print(funcMsg)
        return False, funcMsg, argDBC


def saveToArangoDB(argDBC, collectionName, contentData, sesh):
    try:
        dbStatus, target_collection = arangoCollectionConnection(argDBC, collectionName)
        if (
            isinstance(target_collection, str)
            and target_collection.startswith("Error")
            or dbStatus == False
        ):
            return False, target_collection, sesh

        target_collection.insert(contentData)
        return True, "savedToArangoDB", sesh
    except Exception as e:
        funcMsg = f"Error On saveToArangoDB {e}"
        print(funcMsg)
        return False, funcMsg, sesh


def arangoCollectionConnection(argDBC: str, collectionName: str):
    try:
        if not argDBC.has_collection(collectionName):
            argDBC.create_collection(collectionName)
            # created collection add 1st document
            docModTime = getNowDateTime()
            saveFirstContent = {"docModTime": docModTime}
            new_collection = argDBC.collection(collectionName)
            new_collection.insert(saveFirstContent)

        collection_target = argDBC.collection(collectionName)
        return True, collection_target

    except Exception as e:
        funcMsg = f"Error arangoCollectionConnection {e}"
        print(funcMsg)
        return False, funcMsg


def stopDuplicates(arangoDB, collectionName, field_name, field_value):
    try:
        dbClient = ArangoClient(hosts=arangoHost)
        argDBC = dbClient.db(arangoDB, username=arangoUser, password=arangoPwd)

        query = """
            FOR doc IN @@collection
            FILTER doc.@field == @value
            LIMIT 1
            RETURN doc
        """
        bind_vars = {
            "@collection": collectionName,
            "field": field_name,
            "value": field_value,
        }

        result = argDBC.aql.execute(query, bind_vars=bind_vars)

        return True, any(result)
    except Exception as e:
        funcMsg = f"Error On stopDuplicates {e}"
        print(funcMsg)
        return False, funcMsg


def isCollectionEmpty(arangoDB, collectionName):
    try:
        query = f"FOR doc IN {collectionName} LIMIT 1 RETURN 1"
        cursor = arangoDB.aql.execute(query)
        return True, any(cursor)
    except Exception as e:
        funcMsg = f"Error on checking if collection is empty: {e}"
        print(funcMsg)
        return False, funcMsg


def getAllDatabases(sesh):
    try:
        # Connect to the ArangoDB server
        client = ArangoClient(hosts=arangoHost)

        sys_db = client.db("_system", username=arangoUser, password=arangoPwd)

        # Fetch all database names
        databaseNames = sys_db.databases()
        databaseList = [db for db in databaseNames if not db.startswith("_")]
        return True, "Success", databaseList, sesh
    except Exception as e:
        funcMsg = f"Error on getting all DBs: {e}"
        print(funcMsg)
        return False, funcMsg, databaseList, sesh
