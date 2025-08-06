import torch
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from types_ocr.sftp_account import sftp_account

# NOTE: Load environment variables from .env file
load_dotenv()
account = sftp_account(
    hostname=str(os.getenv("HOSTNAME_SSH")),
    port=int(os.getenv("PORT_SSH", "22")),
    username=str(os.getenv("USERNAME_SSH")),
    password=str(os.getenv("PASSWORD_SSH")),
)
timeout = int(os.getenv("TIMEOUT_SFTP", "5"))
folder_remote_path = str(os.getenv("REMOTE_CACHE_PATH"))
folder_local_path = str(os.getenv("LOCAL_CACHE_PATH"))
folder_remote_save_path = str(os.getenv("REMOTE_SAVE_PATH"))

model_path = str(os.getenv("MODEL_PATH", "llama-3.1"))
max_seq_length = int(os.getenv("MAX_SEQ_LENGTH", "2048"))

# FIXED: Unsloth and PyTorch Dynamo conflict
# WARNING: Must configure OS before importing Unsloth
os.environ["PYTORCH_DISABLE_DYNAMO"] = "1"
os.environ["TORCH_COMPILE_DISABLE"] = "1"
# Turn off dynamo config
torch._dynamo.config.disable = True
torch._dynamo.config.suppress_errors = True

from fastapi import FastAPI, HTTPException, UploadFile, File
from utils.load_models.major_model import load_model_and_tokenizer, gen_json
from utils.load_models.marker_model import load_marker_model, get_text_from_pdf
from utils.sftp_serve.push_file import push_file_to_remote
from querys.insert_2_dtb import insert_records_from_json


class Item(BaseModel):
    file_name: str


app = FastAPI()

model, tokenizer = load_model_and_tokenizer(
    model_path=model_path, max_seq_length=max_seq_length
)  # Llama 3.1 model for generating JSON from Markdown

converter = load_marker_model()  # Marker model for converting PDF to Markdown


def convert_to_json(file_name: str):
    # NOTE: Convert PDF to JSON
    print("Generating JSON from Markdown...")
    if get_text_from_pdf(
        converter, folder_local_path=folder_local_path, file_name=file_name
    )["response"]:  # Convert PDF to Markdown
        print("-" * 50, file_name, "-" * 50)
        generated_output = gen_json(
            model,
            tokenizer,
            folder_local_path=folder_local_path,
            max_seq_length=max_seq_length,
        )  # Generate JSON from Markdown

        # ThoiDiemDangKy
        push_file_to_remote(
            account=account,
            file_path=str(os.path.join(folder_local_path, file_name)),
            remote_path=folder_remote_save_path,
            file_name=file_name,
            datetime_folder=str(generated_output["ThoiDiemDangKy"]),
        )

        # NOTE: remove file from cache after processing
        os.remove(str(os.path.join(folder_local_path, file_name)))

        print("-" * 50, "END", "-" * 50)
        insert_records_from_json(json_input=generated_output)
        print("JSON generated and inserted into the database successfully.")

        return generated_output
    else:
        print("Failed to convert PDF to Markdown.")
        return {"response": False}


@app.post("/convert-json-from-local", response_model=dict)
def convert_json(file: Item):
    """
    Endpoint to convert a PDF file to JSON format.
    :param file: PDF file name to be converted.
    """
    if file.file_name.endswith(".pdf") is False:
        return {"response": "File must be a PDF."}

    return convert_to_json(file.file_name)


@app.post("/convert-to-json-from-upload", response_model=dict)
async def testing_function(file: UploadFile = File(...)):
    # NOTE: process the uploaded file
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    try:
        # WARNING: This endpoint is for testing purposes only.
        # NOTE: Save the uploaded PDF file to a temporary location
        contents = await file.read()

        file_name_cache = "pdf_cached.pdf"
        file_path = os.path.join(folder_local_path, file_name_cache)

        with open(file_path, "wb") as f:
            f.write(contents)

        return convert_to_json(file_name=str(file.filename))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
