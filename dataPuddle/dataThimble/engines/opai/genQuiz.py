# Last modified: 2025-04-02 21:05:38
# Version: 0.0.54
import sys
import os
import json
from dataclasses import dataclass
from typing import Dict, Any
from openai import OpenAI
import gradio as gr
import json
from typing import Dict, Any


def genMCQ(envVars: dict, contentChunk: str) -> str:

    oaClient = OpenAI(api_key=envVars["api_key"])

    structured_output_prompt = """
    You are provided Text from a training class. Analyze the Text, determine its topic, subject, context and its key point and intent, and generate a Multiple choice question with 4 relevant and tricky distractors as the choices and the answer.
    Generate a Title for the question from the topic, subject, context and intent you extracted.
    Generate Multiple choice question as a structured output in the following JSON format:
    
    {
        "Topic": "<Generated Topic Of Question Here>",
        "Question": "<Generated Question Here>",
        "A:": "<Generated Answer Choice Text Here>",
        "B:": "<Generated Answer Choice Text Here>",
        "C:": "<Generated Answer Choice Text Here>",
        "D:": "<Generated Answer Choice Text Here>",
        "Answer": "<Correct Answer Choice Here>: <Correct Answer Choice Text Here>"
    }
    """

    full_prompt = (
        f"{structured_output_prompt}\n"
        f"Here is the text to analyze and generate the Multiple choice question and answers: {contentChunk}"
    )

    try:
        # Call the OpenAI API
        oaCompletionResponse = oaClient.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educator and assessment designer across all domains of knowledge. You analyze provided content—regardless of subject matter—and generate challenging, contextually relevant multiple-choice questions that test deep understanding and critical thinking. Each question must include four answer choices (A-D), one correct answer, and be crafted to reflect the complexity and nuance of the source material. Follow the structure provided.",
                },
                {"role": "user", "content": full_prompt},
            ],
            temperature=0.77,
            frequency_penalty=0.7,
            presence_penalty=0.5,
            top_p=0.9,
        )

        structured_response = oaCompletionResponse.choices[0].message.content

        # Preprocess the response to remove Markdown code block if present
        if structured_response.startswith("```") and structured_response.endswith(
            "```"
        ):
            structured_response = structured_response.strip("```").strip()
            if structured_response.startswith("json"):
                structured_response = structured_response[len("json") :].strip()

        # Try parsing the response as JSON
        question_data: Dict[str, Any] = json.loads(structured_response)

        return question_data

    except json.JSONDecodeError as e:
        return structured_response.strip()

    except Exception as e:
        print(f"Error generating Question: {e}")
        return f"Error generating Question: {e}"
