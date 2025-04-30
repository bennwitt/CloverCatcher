# Last modified: 2024-12-31 23:35:22
# Version: 0.0.93
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
from engines.arango.arangoBaseEngine import arangoAction


def collapse_doc_to_field_save_new_collection(srcCollection, dstCollection):
    try:
        # Step 1: Connect to the source ArangoDB database
        db_status, log_msg, arg_dbc = connectToArangoDB(
            arangoHost, arangoDB, arangoUser, arangoPwd
        )
        if not db_status:
            print(f"Connection error: {log_msg}")
            return False, log_msg

        # Step 2: Get all documents from source collection
        source_col = arg_dbc.collection(srcCollection)
        all_docs = source_col.all()

        # Step 3: Iterate over each document and collapse its fields into a single text field
        for doc in all_docs:
            # Join all fields into a single string, excluding '_key' and '_id'
            mega_meta_email_data = " ".join(
                str(value) for key, value in doc.items() if key not in ["_key", "_id"]
            )

            # Create a new document for target collection
            new_doc = {"megaMetaEmailData": mega_meta_email_data}

            # Step 4: Save the collapsed document to the target collection
            db_status, log_msg, _ = arangoAction(arangoDB, dstCollection, new_doc, None)
            if not db_status:
                print(f"Failed to save document: {log_msg}")
                continue  # Continue processing other documents

        return True, "All documents processed successfully."

    except Exception as e:
        errMsg = f"Error in collapse_documents_and_save: {e}"
        print(errMsg)
        return False, errMsg


def connectToArangoDB(arangoHost, arangoDB, arangoUser, arangoPwd):
    try:
        dbClient = ArangoClient(hosts=arangoHost)
        sysDB = dbClient.db("_system", username=arangoUser, password=arangoPwd)
        if not sysDB.has_database(arangoDB):
            sysDB.create_database(arangoDB)

        argDBC = dbClient.db(arangoDB, username=arangoUser, password=arangoPwd)
        return True, "argDBC success", argDBC
    except Exception as e:
        errMsg = f"Error On connectToArangoDB {e}"
        print(errMsg)
        return False, errMsg, argDBC


def findMakeInsertRemove(argDBC, collectionName):
    try:
        # && !HAS(doc, "workStatus")
        aql_query = f"""
        FOR doc IN {collectionName}
            FILTER HAS(doc, "theEmailTextEmbeddings") 
            LIMIT 1
            UPDATE doc WITH {{ workStatus: "remove theemailtextembeddings field" }} IN {collectionName}
            RETURN NEW
        """
        cursor = argDBC.aql.execute(aql_query)
        result = list(cursor)

        if not result:
            return "No items to process"

        doc = result[0]
        workItemKey = doc["_key"]

        emailText = doc.get("emailText", "")

        cleanEmailText = sanitext(emailText)

        emailTextEmbeddings = genEmbeddings(cleanEmailText, embeddingModel)

        dModTime = getNowDateTime()

        update_query = f"""
        FOR doc IN {collectionName}
            FILTER doc._key == "{workItemKey}"
            UPDATE UNSET(doc, "theEmailTextEmbeddings") WITH {{
                docModTime: @dModTime,
                emailText: {json.dumps(cleanEmailText)}, 
                emailTextEmbeddings: {json.dumps(emailTextEmbeddings)},
                theEmailTextEmbeddings: null,
                workStatus: "removedBadField" 
            }} IN {collectionName}
        """

        bind_vars = {
            "dModTime": dModTime,
        }

        argDBC.aql.execute(update_query, bind_vars=bind_vars)
    except Exception as e:
        errMsg = f"Error in findMakeInsert: {e}"
        print(errMsg)
        return False, errMsg

    return True, f"all good {workItemKey}"


# this one actually works.
def getFieldMakeEmbeddingInsertNewField(argDBC, collectionName):
    try:
        # AQL query to find a document without "embeddings" and "workStatus" fields
        aql_query = f"""
        FOR doc IN {collectionName}
            FILTER !HAS(doc, "visualTextEmbeddings") && !HAS(doc, "workStatus")
            LIMIT 1
            UPDATE doc WITH {{ workStatus: "checkedOutForEmbeddings" }} IN {collectionName}
            RETURN NEW
        """
        cursor = argDBC.aql.execute(aql_query)
        result = list(cursor)

        if not result:
            return "No items to process"

        doc = result[0]
        workItemKey = doc["_key"]
        visualFontText = doc.get("Text", "")
        contentCompositionText = doc.get("Composition", "")
        contentPeopleDetailText = doc.get("PeopleDetail", "")
        contentTargetAudienceText = doc.get("TargetAudience", "")
        contentEmailText = doc.get("emailText", "")

        targetAudienceTextEmbeddings = genEmbeddings(
            contentTargetAudienceText, embeddingModel
        )
        contentCompositionTextEmbeddings = genEmbeddings(
            contentCompositionText, embeddingModel
        )
        contentVisualFontTextEmbeddings = genEmbeddings(visualFontText, embeddingModel)
        contentEmailTextEmbeddings = genEmbeddings(contentEmailText, embeddingModel)
        contentPeopleDetailTextEmbeddings = genEmbeddings(
            contentPeopleDetailText, embeddingModel
        )

        update_query = f"""
        FOR doc IN {collectionName}
            FILTER doc._key == "{workItemKey}"
            UPDATE doc WITH {{ targetAudienceTextEmbeddings: {targetAudienceTextEmbeddings}, workStatus: "embeddingsComplete", peopleDetailTextEmbeddings: {contentPeopleDetailTextEmbeddings}, fontTextEmbeddings: {contentVisualFontTextEmbeddings}, emailTextEmbeddings: {contentEmailTextEmbeddings}, compositionTextEmbeddings: {contentCompositionTextEmbeddings},}} IN {collectionName}
        """
        argDBC.aql.execute(update_query)
    except Exception as e:
        errMsg = f"Error in findMakeInsert: {e}"
        print(errMsg)
        return False, errMsg

    return True, f"all good {workItemKey}"


def makeExternalIdField(argDBC, collectionName):
    try:
        # && !HAS(doc, "workStatus")
        aql_query = f"""
        FOR doc IN {collectionName}
            FILTER !HAS(doc, "externalId") 
            LIMIT 1
            UPDATE doc WITH {{ workStatus: "addingExternalId" }} IN {collectionName}
            RETURN NEW
        """
        cursor = argDBC.aql.execute(aql_query)
        result = list(cursor)

        if not result:
            return "No items to process"

        doc = result[0]
        workItemKey = doc["_key"]

        emailname = doc.get("EmailName", "")

        imgpath = doc.get("artifactsFolder", "")
        emailimgpath = doc.get("emailImagePath", "")

        fixDimgpath = imgpath.replace(
            "/ai/aiApps/aiWinCAP/mediaLibrary/ahaArtifacts/",
            "/ai/mediaLibrary/mooreMUSE/ahaArtifacts/",
        )
        fixDemailimgpath = emailimgpath.replace(
            "/ai/aiApps/aiWinCAP/mediaLibrary/ahaArtifacts/",
            "/ai/mediaLibrary/mooreMUSE/ahaArtifacts/",
        )

        externalId = generateHash(emailname)

        # cleanEmailText = sanitext(emailText)
        # theEmailTextEmbeddings: null,
        # emailTextEmbeddings = genEmbeddings(cleanEmailText, embeddingModel)   artifactsFolder: fixDimgpath

        dModTime = getNowDateTime()

        update_query = f"""
        FOR doc IN {collectionName}
            FILTER doc._key == "{workItemKey}"
            UPDATE doc WITH {{
                docModTime: @dModTime,
                externalId: {json.dumps(externalId)}, 
                artifactsFolder: {json.dumps(fixDimgpath)},
                emailImagePath: {json.dumps(fixDemailimgpath)},
                workStatus: "artifactsPathFixD" 
            }} IN {collectionName}
        """

        bind_vars = {
            "dModTime": dModTime,
        }

        argDBC.aql.execute(update_query, bind_vars=bind_vars)
    except Exception as e:
        errMsg = f"Error in findMakeInsert: {e}"
        print(errMsg)
        return False, errMsg

    return True, f"all good {workItemKey}"


"""
cnt = 47
status, msg, argDBC = connectToArangoDB(arangoHost, "mooreMUSE", arangoUser, arangoPwd)


while status == True:
    cnt -= 1
    status, msg = makeExternalIdField(
        argDBC, "PersuasiveLanguageElementsAndImpactfulMessaging"
    )
    print(str(f"{status} {cnt}"))

"""


def update_documents_with_stats_arango(
    db_name="mooreMUSE", collection_name="mediaAssets"
):
    # Initialize the ArangoDB client and open the database
    client = ArangoClient()
    db = client.db(arangoDB, arangoUser, arangoPwd)
    collection = db.collection(collection_name)

    # Iterate through each document in the collection
    for document in collection.all():
        # Initialize lists to store field-value pairs for contentStats and performanceStats
        content_stats_data = []
        performance_stats_data = []

        # Add fields and their values from content_stats list to the content_stats_data list
        for field_name in content_stats:
            if field_name in document:
                # Append a dictionary with field name and its value
                content_stats_data.append({field_name: document[field_name]})

        # Add fields and their values from performance_stats list to the performance_stats_data list
        for field_name in performance_stats:
            if field_name in document:
                # Append a dictionary with field name and its value
                performance_stats_data.append({field_name: document[field_name]})

        # Update the document with contentStats and performanceStats fields as lists of field-value pairs
        update_data = {
            "contentStats": content_stats_data,
            "performanceStats": performance_stats_data,
        }

        # Update the document in the collection with the new fields
        collection.update_match({"_key": document["_key"]}, update_data)


# Example usage
content_stats = [
    "AdjectiveListCount",
    "AllCAPsTextCount",
    "Amount_count",
    "AskStatementCount",
    "CallToActionCount",
    "ColorsCount",
    "CompositionCount",
    "DeclarativeStatementCount",
    "DirectiveStatementCount",
    "EmbeddedImagesCount",
    "EmotionTextCount",
    "EmpathyTextCount",
    "ExclamatoryStatementCount",
    "FactStatementCount",
    "HelpingCauseTextCount",
    "HelpingPeopleTextCount",
    "HeroTextCount",
    "ImperativeStatementCount",
    "InterrogativeStatementCount",
    "MatchingDetailsCount",
    "PeopleDetailCount",
    "SentenceLengthCounts",
    "SocialProofingCount",
    "TargetAudienceCount",
    "TextCount",
    "TotalEmojiCount",
    "TotalQuestionCount",
    "TotalSentenceCount",
    "TotalShoutCount",
    "TotalWordCount",
    "UrgencyTextCount",
    "VerbListCount",
    "VisualDataCount",
    "VisualSummaryCount",
    "WordLengthCounts",
    "Z_amount_count",
    "VisualIntentCount",
]

performance_stats = [
    "Amount_sum",
    "Amount_count",
    "avg_donation_amount",
    "Z_amount_sum",
    "Z_amount_count",
    "Z_avg_donation_amount",
    "Total_Z",
    "75th_percentile_amount",
    "25th_percentile_amount",
    "ClientID",
    "ClientName",
    "JobID",
    "EmailName",
    "SendStartTime",
    "SendCompleteTime",
    "Sends",
    "ImplicitDeliveries",
    "ImplicitDeliveryRate",
    "OverallBounces",
    "OverallBounceRate",
    "HardBounces",
    "HardBounceRate",
    "SoftBounces",
    "SoftBounceRate",
    "BlockBounces",
    "BlockBounceRate",
    "TechnicalBounces",
    "TechnicalBounceRate",
    "UnknownBounces",
    "UnknownBounceRate",
    "UniqueOpens",
    "CumulativeOpens",
    "OpenRate",
    "UniqueClicks",
    "CumulativeClicks",
    "ClickRate",
    "UniqueSurveyResponses",
    "CumulativeSurveyResponses",
    "SurveyResponseRate",
    "UniqueConversions",
    "CumulativeConversions",
    "ConversionRate",
    "UniqueFTAFs",
    "CumulativeFTAFs",
    "FTAFRate",
    "UniqueFTAFRecipients",
    "CumulativeFTAFRecipients",
    "FTAFRecipientRate",
    "UniqueFTAFSubscribers",
    "CumulativeFTAFSubscribers",
    "FTAFSubscriberRate",
    "ComplaintDeliveries",
    "UniqueComplaints",
    "CumulativeComplaints",
    "ComplaintRate",
    "UniqueUnsubscribes",
    "CumulativeUnsubscribes",
    "UnsubscribeRate",
]


update_documents_with_stats_arango()
