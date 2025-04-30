# Last modified: 2025-04-02 21:05:02
# Version: 0.0.64
import sys
import os
import json
from dataclasses import dataclass
from typing import Dict, Any
from openai import OpenAI

import json
from typing import Dict, Any


def genTitleSummaryKeyPoints(envVars: dict, contentChunk: str) -> str:

    oaClient = OpenAI(api_key=envVars["api_key"])

    system_content_prompt = """You are an expert educator and assessment designer across all domains of knowledge. You analyze provided content—regardless of subject matter—and generate challenging, contextually relevant insights and observations that demonstrate understanding and critical thinking craft your conclusions and findings in the following structure provided."""

    structured_output_prompt = """
    You are a highly capable, natural-sounding AI tasked with analyzing educational or training content.

    Given the provided text from a training class, perform the following:

    1. Analyze the text thoroughly to determine its **main topic**, **subject**, **context**, **intent**, and **core message**.
    2. Generate a **Title** that clearly reflects the essence of the content.
    3. Create a **Trailer-Type Summary** a compelling, high-level overview written like a short teaser for engaging or presenting the content.
    4. Extract **Key Points**: concise, important concepts or ideas covered in the text (as bullet points).
    5. Extract **Named Entities** (NER): people, organizations, technologies, locations, and key terminology mentioned.
    6. Return the structured data as a JSON object with the following format:

    ```json
    {
    "Title": "<Generated Title>",
    "TrailerSummary": "<Trailer-Type Summary>",
    "Topic": "<Detected Core Topic>",
    "KeyWords": ["<Keyword1>", "<Keyword2>", "..."],
    "KeyPoints": [
        "<Key Point 1>",
        "<Key Point 2>"
    ],
    "NamedEntities": [
        "<Entity 1>",
        "<Entity 2>"
    ]
    }
    """

    full_prompt = (
        f"{structured_output_prompt}\n"
        f"Here is the text to analyze and generate the Title, TrailerSummary, Topic, KeyWords, KeyPoints and Named Entities: {contentChunk}"
    )

    try:
        # Call the OpenAI API
        oaCompletionResponse = oaClient.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": system_content_prompt,
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
        summary_data: Dict[str, Any] = json.loads(structured_response)

        return summary_data

    except json.JSONDecodeError as e:
        return structured_response.strip()

    except Exception as e:
        return f"Error generating Question: {e}"
