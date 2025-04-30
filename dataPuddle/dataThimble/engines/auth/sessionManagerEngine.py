# Last modified: 2025-03-29 23:36:24
# Version: 0.0.77
from arango import ArangoClient
from typing import Dict, Any, Tuple
from appVault.keyVault import *
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Any, Union
from engines.models.museDataModel import UserSeshState
from engines.db.arangoBaseEngine import arangoAction
from engines.util.zTimeEngine import getNowDateTime
from engines.models.museDataModel import AppUserData
from engines.models.museDataModel import AppContentData
from fastapi.encoders import jsonable_encoder

from arango import ArangoClient
from arango.exceptions import ArangoServerError
from fastapi.encoders import jsonable_encoder


def updateUserSesh(userEmailAddress, userSeshStateUpdate):
    try:
        client = ArangoClient(hosts=arangoHost)
        db = client.db(accessControlDB, username=arangoUser, password=arangoPwd)
        # Fetch the document with matching userEmailAddress
        query = """
        FOR doc IN @@sessionCollection
            FILTER doc.userEmailAddress == @userEmailAddress
            LIMIT 1
            RETURN doc
        """
        bind_vars = {
            "@sessionCollection": sessionCollection,  # Correct way to pass collection names
            "userEmailAddress": userEmailAddress,
        }

        cursor = db.aql.execute(query, bind_vars=bind_vars)
        result = list(cursor)

        if not result:
            return False, "UserNotFound", None

        doc = result[0]
        docKey = doc["_key"]

        # If new session data is provided, update the document
        if userSeshStateUpdate:
            userSessionData = userSeshStateUpdate.get("userSessionData", {})
            userConvoData = userSeshStateUpdate.get("userConvoData", {})

            # Convert data to JSON-compatible format
            userSessionDataJson = jsonable_encoder(userSessionData)
            userConvoDataJson = jsonable_encoder(userConvoData)

            # Update Query
            update_query = """
            UPDATE @docKey 
            WITH { 
                userConvoData: @userConvoData, 
                userSessionData: @userSessionData, 
                lastUpdated: @lastUpdated, 
                userEmailAddress: @userEmailAddress 
            } 
            IN @@sessionCollection 
            RETURN NEW
            """

            update_bind_vars = {
                "@sessionCollection": sessionCollection,
                "docKey": docKey,
                "userEmailAddress": userEmailAddress,
                "userSessionData": userSessionDataJson,
                "userConvoData": userConvoDataJson,
                "lastUpdated": getNowDateTime(),
            }

            cursor = db.aql.execute(update_query, bind_vars=update_bind_vars)
            result = list(cursor)
            doc = result[0]

            return True, "UserUpdated", doc

        return False, "NoUpdateProvided", None

    except ArangoServerError as e:
        error_msg = f"ArangoDB Error: {str(e)}"
        print(error_msg)
        return False, error_msg, None

    except Exception as e:
        error_msg = f"Unexpected Error: {str(e)}"
        print(error_msg)
        return False, error_msg, None


def initState():
    return AppUserData(), AppContentData()


def initChat(userEmailAddress):
    convoHistory = []
    userConvoInputText = f"Hello MUSE I am {userEmailAddress}!"
    assistantConvoOutputText = f"### Hello! {userEmailAddress}\n### What creative content and performance metrics are we developing a strategy to execute?"
    convoHistory.append({"role": "user", "content": userConvoInputText})
    convoHistory.append({"role": "assistant", "content": assistantConvoOutputText})
    return convoHistory


def initUserSeshState(userEmailAddress):
    aud, acd = initState()
    convoQueue = initChat()
    userSeshState = UserSeshState(
        userSessionData={
            "aud": aud,
            "acd": acd,
            "lastUpdated": getNowDateTime(),
        },
        userConvoData={"convoHistory": []},
        convoQueue=convoQueue,
        userProfile={},
    )
    return userSeshState


def getUserSesh(userEmailAddress):
    try:
        client = ArangoClient(hosts=arangoHost)
        db = client.db(accessControlDB, username=arangoUser, password=arangoPwd)

        # Fetch the document with matching EmailName
        query = f"""
        FOR doc IN {sessionCollection}
            FILTER doc.userEmailAddress == @userEmailAddress
            LIMIT 1
            RETURN doc
        """
        bind_vars = {"userEmailAddress": userEmailAddress}

        cursor = db.aql.execute(query, bind_vars=bind_vars)
        result = list(cursor)
        if not result:
            return False, "UserNotFound", "None"

        doc = result[0]
        userSeshState = {}
        userSeshState["userSessionData"] = doc.get("userSessionData")
        userSeshState["userEmailAddress"] = doc.get("userEmailAddress")
        userSeshState["authResponseStatus"] = doc.get("authResponseStatus")
        userSeshState["clientDataRepoInfo"] = doc.get("clientDataRepoInfo")
        userSeshState["userConvoData"] = doc.get("userConvoData")
        userSeshState["convoQueue"] = doc.get("convoQueue")

        return True, "UserFound", userSeshState

    except Exception as e:
        funcMsg = f"Error on getting UserClientAppList: {e}"
        print(funcMsg)
        return False, funcMsg, "None"


def saveUserSession(
    userEmailAddress: str, userSessionData: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Saves or updates the user session in ArangoDB.
    """
    userSessionData["userEmailAddress"] = userEmailAddress
    userSessionData["lastUpdated"] = getNowDateTime()

    funcStatus, funcMsg, _ = arangoAction(
        accessControlDB, sessionCollection, userSessionData, None
    )

    return funcStatus, funcMsg


def validateUserSession(userEmail):
    """
    Checks if a user's session is valid by retrieving it from ArangoDB.
    """
    funcStatus, funcMsg, userSeshState = getUserSesh(userEmail)

    if not funcStatus:
        return False, funcMsg, {}

    return True, funcMsg, userSeshState
