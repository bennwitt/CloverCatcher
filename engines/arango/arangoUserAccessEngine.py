# Last modified: 2025-01-03 08:29:54
# Version: 0.0.89
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


def getAllRepoDatabases(sesh):
    try:
        # Connect to the ArangoDB server
        client = ArangoClient(hosts=arangoHost)

        sys_db = client.db("_system", username=arangoUser, password=arangoPwd)

        # Fetch all database names
        databaseNames = sys_db.databases()
        databaseList = [db for db in databaseNames if db.endswith("Repo")]

        sesh["acd"].serverRepoList = databaseList

        return True, "Success", sesh

    except Exception as e:
        funcMsg = f"Error on getting all RepoDBs: {e}"
        print(funcMsg)
        return False, funcMsg, sesh


def getClientRepoCollections(dataBaseName, sesh):
    try:
        client = ArangoClient(hosts=arangoHost)
        db = client.db(dataBaseName, username=arangoUser, password=arangoPwd)

        collections = db.collections()
        databaseCollectionList = [
            collection["name"]
            for collection in collections
            if not collection["name"].startswith("_")
        ]
        return True, "Success", databaseCollectionList, sesh

    except Exception as e:
        funcMsg = f"Error on getting all RepoDB Collections: {e}"
        print(funcMsg)
        return False, funcMsg, databaseCollectionList, sesh


def getUserClientAppList(sesh):
    try:
        client = ArangoClient(hosts=arangoHost)
        db = client.db(accessControlDB, username=arangoUser, password=arangoPwd)

        # Fetch the document with matching EmailName
        query = f"""
        FOR doc IN {userPermissionsCollection}
            FILTER doc.userEmail == @userEmail
            LIMIT 1
            RETURN doc
        """
        bind_vars = {"userEmail": sesh["aud"].userEmail}

        cursor = db.aql.execute(query, bind_vars=bind_vars)
        result = list(cursor)
        if not result:
            return False, "None", sesh

        doc = result[0]

        sesh["aud"].userAppList = doc.get("userAppList")
        sesh["aud"].userClientList = doc.get("userClientList")
        sesh["aud"].userId = doc.get("userId")
        sesh["aud"].userEmail = doc.get("userEmail")
        sesh["aud"].userTrustedVoicesList = doc["userTrustedVoicesList"]
        sesh["aud"].userSessionsHistoryList = doc["userSessionsHistoryList"]

        return True, "got user client list", sesh

    except Exception as e:
        funcMsg = f"Error on getting UserClientAppList: {e}"
        print(funcMsg)
        return False, funcMsg, sesh


def getAllChannelCollections(dataBaseName, channelString, sesh):
    try:
        client = ArangoClient(hosts=arangoHost)
        db = client.db(dataBaseName, username=arangoUser, password=arangoPwd)
        matchedChannelStringCollectionsList = []
        databaseCollectionsList = []
        collections = db.collections()
        databaseCollectionsList = [
            collection["name"]
            for collection in collections
            if not collection["name"].startswith("_")
        ]
        matchedChannelStringCollectionsList = [
            item for item in databaseCollectionsList if channelString in item
        ]

        return (
            True,
            "Success",
            databaseCollectionsList,
            matchedChannelStringCollectionsList,
            sesh,
        )

    except Exception as e:
        funcMsg = f"Error on getting all channel Collections: {e}"
        print(funcMsg)
        return False, funcMsg, [], [], sesh
