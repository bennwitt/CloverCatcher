# Last modified: 2025-02-27 15:40:03
# Version: 0.0.103
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dataclasses import dataclass, field, asdict
from datetime import datetime
import html
import json


def sendFeedbackEmail(
    feedbackEmailList,
    userEmailAddress,
    feedbackOpinion,
    feedbackText,
    sourceContentTextInput,
    generatedContentOutput,
    generatedContentReport,
    sessionData,
):

    json_sessionData, html_sessionData = makeSessionDataPretty(sessionData)
    html_session_content = (
        f"<pre>{userEmailAddress} : Opinion:{html.escape(feedbackOpinion)}</pre>"
    )
    html_session_content += f"<pre>FeedbackText: {html.escape(feedbackText)}</pre>"
    html_session_content += (
        f"<pre>sourceContentTextInput: {html.escape(sourceContentTextInput)}</pre>"
    )
    html_session_content += (
        f"<pre>generatedContentReport: {html.escape(generatedContentReport)}</pre>"
    )
    html_session_content += (
        f"<pre>generatedContentOutput: {html.escape(generatedContentOutput)}</pre>"
    )
    html_session_content += html_sessionData

    try:
        feedbackStatus = True
        feedbackReceiptMessageList = []
        for feedbackEmailAddress in feedbackEmailList:

            messageContent = Mail(
                from_email=authorityEmailAddress.strip().lower(),
                to_emails=feedbackEmailAddress.strip().lower(),
                subject=f"CopyThat{appVer} Feedback : {feedbackOpinion}",
                html_content=html_session_content,
            )

            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(messageContent)
            feedbackStatus = response.status_code <= 299
            feedbackReceiptMessageList.append(
                f"{str({response.status_code})}: str({response.headers})"
            )

        return feedbackStatus, feedbackReceiptMessageList

    except Exception as e:
        print(e.message)
        return False, [e]


def makeSessionDataPretty(sessionData):
    formatted_sessiondata = {key: asdict(value) for key, value in sessionData.items()}

    # Convert to JSON
    json_sessionData = json.dumps(formatted_sessiondata, indent=4, default=str)

    # Convert JSON to HTML-friendly format
    html_sessionData = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <pre style="background: #f4f4f4; padding: 10px; border-radius: 5px; white-space: pre-wrap;">
        {json_sessionData}
        </pre>
    </body>
    </html>
    """

    return json_sessionData, html_sessionData
