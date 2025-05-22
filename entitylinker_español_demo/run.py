import uvicorn
import gradio as gr
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app_gradio import EntityLinkingUI

CUSTOM_PATH = "/"

app = FastAPI()

# Sirve la carpeta assets/
app.mount("/static", StaticFiles(directory="assets"), name="static")

el_demo = EntityLinkingUI()
app = gr.mount_gradio_app(app, el_demo.get_app(), path=CUSTOM_PATH)

if __name__ == "__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True, workers=2)
