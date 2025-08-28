from fastapi import FastAPI
import os
from load_models.marker_model import converter, text_from_rendered
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
path = str(os.getenv("CACHE_PATH"))

@app.get("/convertPDF2MD", response_model=dict)
def insert_tieu_chi():
    rendered = converter(os.path.join(path, "pdf_cached.pdf"))
    text, _, images = text_from_rendered(rendered)
    with open(
        os.path.join(path, "md_cached.txt"),
        "w",
        encoding="utf-8",
    ) as f:
        f.write(text)
    return {"response": True}
