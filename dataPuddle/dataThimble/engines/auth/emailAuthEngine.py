# Last modified: 2025-02-26 01:46:38
# Version: 0.0.26
import sys
import os
import gradio as gr
from appVault.keyVault import *
from engines.enviros.envInfo import appName, clientName
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Any, Union
from engines.enviros.personaVars import *
from engines.enviros.gradioVars import *
from engines.models.appDataModel import CopyThatData as copyThatObj
from engines.auth.authTokenEngine import *
from engines.arango.arangoBaseEngine import arangoAction
from engines.enviros.arangoVars import setArangoVariables


def requestAuthToken(
    authorizationStatus,
    authToken,
    userEmailAddress,
    sesh,
):

    authDomain = "@wearemoore.com"
    userEmailAddress = userEmailAddress.strip().lower()

    if authorizationStatus == True:
        messageBox = "You Are Already Authorized"
        authorizationStatus = authStatusTrue
        generateButtonStatus = genBtnStatusTrue
        return (
            authorizationStatus,
            generateButtonStatus,
            messageBox,
            sesh,
        )

    if not userEmailAddress or authDomain not in userEmailAddress:
        sesh["copyThatObj"].authStatus = False
        messageBox = "Please Provide an Authorized Email Address"
        authorizationStatus = authStatusFalseEmail
        generateButtonStatus = genBtnStatusFalse

    elif authDomain in userEmailAddress:
        authTokenRequested(userEmailAddress)
        sesh["copyThatObj"].authStatus = False
        messageBox = "AuthToken Request Successful. Please check your Email."
        authorizationStatus = authStatusFalseToken
        generateButtonStatus = genBtnStatusFalse

    else:
        messageBox = "Unknown Condition"
        authorizationStatus = authStatusFalse
        generateButtonStatus = genBtnStatusFalse

    return (
        authorizationStatus,
        generateButtonStatus,
        messageBox,
        sesh,
    )


def userLogin(authorizationStatus, authToken, userEmailAddress, sesh):
    authDomain = "@wearemoore.com"
    userEmailAddress = userEmailAddress.strip().lower()

    if authorizationStatus == True:
        appStatusMsg = "Email Authorized"
        messageBox = appStatusMsg
        authorizationStatus = authStatusTrue
        generateButtonStatus = genBtnStatusTrue

    elif not userEmailAddress or authDomain not in userEmailAddress or not authToken:
        sesh["copyThatObj"].authStatus = False
        messageBox = "Please Provide an Authorized Email Address"
        authorizationStatus = authStatusFalseEmail
        generateButtonStatus = genBtnStatusFalse

    else:
        validationStatus = verifyAuthToken(userEmailAddress, authToken)
        if not validationStatus:
            messageBox = "Failed AuthToken."
            authorizationStatus = authStatusFalseToken
            generateButtonStatus = genBtnStatusFalse
        else:
            messageBox = "User Authorized"
            authorizationStatus = authStatusTrue
            generateButtonStatus = genBtnStatusTrue
        (
            sesh["copyThatObj"].appDb,
            sesh["copyThatObj"].clientDb,
            sesh["copyThatObj"].userDirectory,
            sesh["copyThatObj"].accessLogs,
            sesh["copyThatObj"].activityLogs,
            sesh["copyThatObj"].contentCollection,
        ) = setArangoVariables(clientName, appName)

        sesh["copyThatObj"].userEmailAddress = userEmailAddress
        sesh["copyThatObj"].authStatus = validationStatus
        sesh["copyThatObj"].authToken = authToken

    return (
        authorizationStatus,
        generateButtonStatus,
        messageBox,
        sesh,
    )
