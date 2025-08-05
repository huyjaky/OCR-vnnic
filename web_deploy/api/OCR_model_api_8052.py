import torch
import os
from dotenv import load_dotenv

load_dotenv()
local_path = str(os.getenv("LOCAL_CACHE_PATH"))

# FIXED: Unsloth and PyTorch Dynamo conflict
# WARNING: Must configure OS before importing Unsloth
os.environ["PYTORCH_DISABLE_DYNAMO"] = "1"
os.environ["TORCH_COMPILE_DISABLE"] = "1"
# Turn off dynamo config
torch._dynamo.config.disable = True
torch._dynamo.config.suppress_errors = True

from fastapi import FastAPI
from utils.load_models.major_model import load_model_and_tokenizer, gen_json
from utils.load_models.marker_model import load_marker_model, get_text_from_pdf

app = FastAPI()

model, tokenizer = (
    load_model_and_tokenizer()
)  # Llama 3.1 model for generating JSON from Markdown

converter = load_marker_model()  # Marker model for converting PDF to Markdown


@app.post("/convert-json", response_model=dict)
async def testing_function(file: str):
    # NOTE: process the uploaded file
    file_path = os.path.join(local_path, file)

    # NOTE: Convert PDF to JSON
    print("Generating JSON from Markdown...")
    if get_text_from_pdf(converter, file_path)["response"]:  # Convert PDF to Markdown
        generated_output = gen_json(model, tokenizer)  # Generate JSON from Markdown
        print("-" * 60)
        return {"response": generated_output}
    else:
        print("Failed to convert PDF to Markdown.")
        return {"response": False}
