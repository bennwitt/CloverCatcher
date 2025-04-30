# Last modified: 2025-02-26 00:17:03
# Version: 0.0.87
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import hashlib
import hmac
import os
import sys
import html
from appVault.keyVault import *


def sendFeedback(feedbackEmailList, feedbackText):
    for feedbackEmailAddress in feedbackEmailList:

        messageContent = Mail(
            from_email=authorityEmailAddress.strip().lower(),
            to_emails=feedbackEmailAddress.strip().lower(),
            subject="CopyThat Feedback",
            html_content=f"<pre>{html.escape(feedbackText)}</pre>",
        )
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(messageContent)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)
            return


def sendUserAuthToken(registeredEmailAddress, authTokenEncoded):
    messageContent = Mail(
        from_email=authorityEmailAddress.strip().lower(),
        to_emails=registeredEmailAddress.strip().lower(),
        subject="CopyThat Registration Token",
        html_content=f"""<pre>
        <strong>Your Authorization Token For: {registeredEmailAddress} 
        Use This Token: {authTokenEncoded}</strong>
        </pre>""",
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(messageContent)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
        return


def authTokenRequested(registeredEmailAddress):
    registeredEmailAddress = registeredEmailAddress.strip().lower()

    authTokenEncoded = generateAuthToken(registeredEmailAddress)
    sendUserAuthToken(registeredEmailAddress, authTokenEncoded)
    return


def authorizeUserRequest(emailAddress, userAuthToken):
    emailAddress = emailAddress.strip().lower()
    userAuthToken = userAuthToken.strip().lower()

    authStatus = verifyAuthToken(emailAddress, userAuthToken)
    return authStatus


def verifyAuthToken(emailAddress, userAuthToken):
    emailAddress = emailAddress.strip().lower()
    userAuthToken = userAuthToken.strip().lower()

    verificationToken = generateAuthToken(emailAddress)
    verificationStatus = hmac.compare_digest(verificationToken, userAuthToken)
    return verificationStatus


def generateAuthToken(emailAddress):
    emailAddress = emailAddress.strip().lower()

    generatedAuthToken = hmac.new(
        secretKey.encode(), emailAddress.encode(), hashlib.sha256
    ).hexdigest()[
        :6
    ]  # First 6 characters
    return generatedAuthToken
