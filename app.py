# Last modified: 2025-04-29 18:58:48
# Version: 0.0.46
import gradio as gr
from pathlib import Path
import sys
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Union
from models.appDataModel import UserData
from models.appDataModel import PersonaData
from engines.agent.agentStudio import agentDirector

app_root = os.path.abspath(os.path.dirname(__file__))
if app_root not in sys.path:
    sys.path.insert(0, os.path.abspath(app_root))
APP_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_ROOT / "app"))


def init_app_model() -> Dict[str, Any]:
    """Return a fresh session dict with the two core dataclasses."""
    return {"seshObj": UserData(), "personaObj": PersonaData()}


theme = gr.themes.Base(
    primary_hue="red",
    secondary_hue="stone",
    neutral_hue="stone",
    text_size="md",
    font=[
        gr.themes.GoogleFont("Montserrat"),
        gr.themes.GoogleFont("Zilla Slab"),
        "system-ui",
        "sans-serif",
    ],
    font_mono=[
        gr.themes.GoogleFont("Roboto Mono"),
        "ui-monospace",
        "Consolas",
        "monospace",
    ],
)


with gr.Blocks(
    title="CloverCatcher",
    theme=theme,
    fill_height=True,
    fill_width=True,
) as cloverCatcher:

    omniObj = gr.State(init_app_model)

    cloverCatcherChat = gr.ChatInterface(
        fn=agentDirector,
        autofocus=True,
        autoscroll=True,
        flagging_mode="manual",
        flagging_options=["👍🏼 Like", "😑 Meh", "👎🏼 DisLike"],
        flagging_dir="./dataPuddle/usrFlags",
        save_history=True,
        multimodal=True,
        fill_height=False,
        fill_width=False,
        stop_btn=True,
        show_progress="full",
        type="messages",
        title="🍀 CloverCatcher",
        description="Upload a photo — Get it detected and annotated!",
        additional_inputs=[omniObj],
        additional_outputs=[omniObj],
    )

if __name__ == "__main__":

    cloverCatcher.launch(
        server_port=8001,
        show_error=True,
        show_api=False,
        share=False,
        server_name="0.0.0.0",
    )
