# Last modified: 2024-09-12 08:54:08
# Version: 0.0.3
import sys
import os
from arango import ArangoClient
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def connectToArangoDB(arangoHost, arangoDB, arangoUser, arangoPwd):
    dbClient = ArangoClient(hosts=arangoHost)
    sysDB = dbClient.db("_system", username=arangoUser, password=arangoPwd)
    if not sysDB.has_database(arangoDB):
        sysDB.create_database(arangoDB)

    arangoDataBaseConnection = dbClient.db(
        arangoDB, username=arangoUser, password=arangoPwd
    )
    return arangoDataBaseConnection


def findDocWithField(db, collection_name, field_name, field_value):
    query = f"FOR doc IN {collection_name} FILTER doc.{field_name} == @value LIMIT 1 RETURN 1"
    cursor = db.aql.execute(query, bind_vars={"value": field_value})
    return any(cursor)


def findLengthOfFieldValue(db, collection_name, searchField):
    query = f"FOR doc IN {collection_name} FILTER HAS(doc, '{searchField}') RETURN LENGTH(doc.{searchField})"
    cursor = db.aql.execute(query)
    results = list(cursor)
    if results:
        return results
    else:
        return "No documents found with the specified field."


def findValueInField(db, collection_name, searchField, fieldText):
    query = (
        f"FOR doc IN {collection_name} FILTER doc.{searchField} == @value RETURN doc"
    )
    cursor = db.aql.execute(query, bind_vars={"value": fieldText})
    return any(cursor)


def listAllFieldValues(arangoDbConnection, collection_name, fieldName):
    db = arangoDbConnection
    collection = db.collection(collection_name)
    cursor = collection.find({})
    listOfFieldValues = [doc["sourcePage"] for doc in cursor if "sourcePage" in doc]
    return listOfFieldValues


def getFieldValue(arangoDbConnection, collection_name, field, values):
    db = arangoDbConnection
    collection = db.collection(collection_name)
    query = f"""
    FOR doc IN {collection_name}
        FILTER doc.{field} IN @values
        RETURN doc
    """

    cursor = db.aql.execute(query, bind_vars={"values": values})
    matched_documents = [doc for doc in cursor]
    return matched_documents


def getFieldsValues(arangoDbConnection, collection_name, fields: list, values: list):
    db = arangoDbConnection
    collection = db.collection(collection_name)
    conditions = " OR ".join(f"doc.{field} IN @values" for field in fields)
    query = f"""
    FOR doc IN {collection_name}
        FILTER {conditions}
        RETURN doc
    """
    cursor = db.aql.execute(query, bind_vars={"values": values})
    matched_documents = [doc for doc in cursor]
    return matched_documents


def arangoCollectionConnection(arangoDbConnection: str, collection_name: str):
    arangoDB = arangoDbConnection
    try:

        def ensure_collection(collection_name):
            if not arangoDB.has_collection(collection_name):
                arangoDB.create_collection(collection_name)
            return arangoDB.collection(collection_name)

        target_collection = ensure_collection(collection_name)

        return target_collection
    except Exception as e:
        chatResponse = f"Error {e}"
        return chatResponse


def saveToArangoDB(
    arangoDbConnection, collection_name, contentData, contentType, metaData
):
    contentType = str(contentType).lower()
    try:
        target_collection = arangoCollectionConnection(
            arangoDbConnection, collection_name
        )
        target_collection.insert(contentData, contentType, metaData)

    except Exception as e:
        ouch = f"Error On DBsrv {e}"
        return ouch
