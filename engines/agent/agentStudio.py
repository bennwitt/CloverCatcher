# Last modified: 2025-04-29 22:21:10
# Version: 0.0.40
from engines.cv.detectAnnotateImage import annotateImageObj
import gradio as gr


def agentDirector(message, history, omniObj):
    user_msg = None
    assistant_msg = None
    if not message["text"]:
        return "Looks like you didn't share any thoughts or files.", omniObj

    elif message["files"] and not message["text"]:
        return (
            "I am gonna need you to share some thoughts and/or guidance on your files.",
            omniObj,
        )

    elif message["files"] and message["text"]:
        annotated_image = annotateImageObj(message["files"][0])
        user_msg = {"role": "user", "content": message}
        assistant_msg = {
            "role": "assistant",
            "content": gr.Image(value=annotated_image),
        }

    elif not message["files"] and message["text"]:
        user_msg = {"role": "user", "content": message["text"]}
        assistant_msg = {"role": "assistant", "content": "Got Your Message."}

    else:
        assistant_msg = {
            "role": "assistant",
            "content": "This is odd.. is there an issue?",
        }

    agentResponse = assistant_msg

    omniObj["seshObj"].history = history

    return agentResponse, omniObj
