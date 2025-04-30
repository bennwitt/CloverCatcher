# Last modified: 2025-03-31 22:59:47
# Version: 0.0.112

from arango import ArangoClient

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
    arangoHost: str,
    arangoUser: str,
    arangoUserPwd: str,
    arangoDb: str,
    collectionName: str,
    contentToSave: Union[List[Any], str, Dict[str, Any]],
    sesh: any,
) -> Tuple[bool, str, Any]:

    dataType = evaluateObjectType(contentToSave)  # Arango need dict, list, string
    if not dataType in ["list", "dict", "str"]:
        return False, f"contentToSave is {dataType}. Convert to list, dict, str.", sesh

    funcMsg = "arangoAction..."
    try:
        funcStatus, funcMsg, argDBC = connectToArangoDB(
            arangoHost, arangoDb, arangoUser, arangoUserPwd
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


def connectToArangoDB(
    arangoHost: str, arangoUser: str, arangoUserPwd: str, arangoDb: str
):
    try:
        funcMsg = "connectToArangoDB..."
        dbClient = ArangoClient(hosts=arangoHost)
        sysDB = dbClient.db("_system", username=arangoUser, password=arangoUserPwd)
        if not sysDB.has_database(arangoDb):
            sysDB.create_database(arangoDb)

        argDBC = dbClient.db(arangoDb, username=arangoUser, password=arangoUserPwd)
        return True, "Success", argDBC

    except Exception as e:
        funcMsg = f"Error On connectToArangoDB {e}"
        print(funcMsg)
        return False, funcMsg, argDBC


def saveToArangoDB(argDBC, collectionName, contentData, sesh):
    try:
        funcMsg = "saveToArangoDB..."
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


def arangoCollectionConnection(
    argDBC: str, collectionName: str, create_collection: bool
):
    funcMsg = ""
    status = False
    collection_target = None
    try:
        if not argDBC.has_collection(collectionName) and create_collection == False:
            status = False
            funcMsg = f"{collectionName} Not Found. Set create_collection to True"
            collection_target = False

        elif not argDBC.has_collection(collectionName) and create_collection == True:
            argDBC.create_collection(collectionName)
            # created collection add 1st document
            docModTime = getNowDateTime()
            saveFirstContent = {"docModTime": docModTime}
            new_collection = argDBC.collection(collectionName)
            new_collection.insert(saveFirstContent)
            status = True
            funcMsg = f"{collectionName} Created added 1st document"
            collection_target = argDBC.collection(collectionName)
        else:
            status = True
            funcMsg = f"{collectionName} Found"
            collection_target = argDBC.collection(collectionName)

        return status, funcMsg, collection_target

    except Exception as e:
        funcMsg = f"Error arangoCollectionConnection {e}"
        return False, funcMsg, collectionName


def stopDuplicates(
    arangoHost: str,
    arangoUser: str,
    arangoUserPwd: str,
    arangoDb: str,
    collectionName,
    field_name,
    field_value,
):
    try:
        funcMsg = "stopDuplicates..."
        dbClient = ArangoClient(hosts=arangoHost)
        argDBC = dbClient.db(arangoDb, username=arangoUser, password=arangoUserPwd)

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
        return False, funcMsg


def isCollectionEmpty(arangoDb, collectionName):
    try:
        query = f"FOR doc IN {collectionName} LIMIT 1 RETURN 1"
        cursor = arangoDb.aql.execute(query)
        return True, any(cursor)
    except Exception as e:
        funcMsg = f"Error on checking if collection is empty: {e}"

        return False, funcMsg


def getAllDatabases(arangoHost: str, arangoUser: str, arangoUserPwd: str):
    try:
        # Connect to the arangoDb server
        client = ArangoClient(hosts=arangoHost)
        funcMsg = "getAllDatabases..."
        sys_db = client.db("_system", username=arangoUser, password=arangoUserPwd)

        # Fetch all database names
        databaseNames = sys_db.databases()
        databaseList = [db for db in databaseNames if db.startswith("aiPrompt")]
        return True, "Success on getting all DBs", databaseList
    except Exception as e:
        funcMsg = f"Error on getting all DBs: {e}"
        print(funcMsg)
        return False, funcMsg, databaseList


def getAllDatabaseCollections(
    arangoHost: str, arangoUser: str, arangoUserPwd: str, allDatabasesList: list
):
    collectionsByDatabase = {}
    try:
        for dbname in allDatabasesList:
            client = ArangoClient(hosts=arangoHost)
            argDbc = client.db(dbname, username=arangoUser, password=arangoUserPwd)

            collections = argDbc.collections()
            databaseCollections = [
                collection["name"]
                for collection in collections
                if collection["name"].startswith("pmt")
            ]
            collectionsByDatabase[dbname] = databaseCollections

        return True, "Success", collectionsByDatabase

    except Exception as e:
        funcMsg = f"Error on getting all RepoDB Collections: {e}"
        return False, funcMsg, collectionsByDatabase
