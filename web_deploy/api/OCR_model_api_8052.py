import torch
import os
from dotenv import load_dotenv

load_dotenv()

# FIXED: Unsloth and PyTorch Dynamo conflict
# WARNING: Must configure OS before importing Unsloth
os.environ["PYTORCH_DISABLE_DYNAMO"] = "1"
os.environ["TORCH_COMPILE_DISABLE"] = "1"
# Turn off dynamo config
torch._dynamo.config.disable = True
torch._dynamo.config.suppress_errors = True

from fastapi import FastAPI, HTTPException, UploadFile, File
from load_models.major_model import load_model_and_tokenizer, gen_json
from load_models.marker_model import load_marker_model, get_text_from_pdf
from input_types.file_type import FileType

app = FastAPI()

model, tokenizer = (
    load_model_and_tokenizer()
)  # Llama 3.1 model for generating JSON from Markdown

converter = load_marker_model()  # Marker model for converting PDF to Markdown


@app.post("/convert-json", response_model=dict)
async def testing_function(file: UploadFile = File(...)):
    # NOTE: process the uploaded file
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    try:
        # WARNING: This endpoint is for testing purposes only.
        # NOTE: Save the uploaded PDF file to a temporary location
        contents = await file.read()
        CACHE_PATH = str(os.getenv("CACHE_PATH"))
        file_path = os.path.join(CACHE_PATH, "pdf_cached.pdf")
        with open(file_path, "wb") as f:
            f.write(contents)

        # NOTE: Convert PDF to JSON
        print("Generating JSON from Markdown...")
        if get_text_from_pdf(converter)["response"]:
            generated_output = gen_json(model, tokenizer)
            print("-" * 60)

            # TODO: Remove the file after processing if is_remove is True
            # IS COMING SOON
            # if input.is_remove:
            #     print("Removing the file after processing...")
            #     return {"response": "File removed after processing."}
            # else:
            #     print("File will not be removed after processing.")
            #     return {"response": "File will not be removed after processing."}


            return {"response": generated_output}
        else:
            print("Failed to convert PDF to Markdown.")
            return {"response": "Failed to convert PDF to Markdown."}
        # generated_output = gen_json(model, tokenizer)
        print("-" * 60)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
