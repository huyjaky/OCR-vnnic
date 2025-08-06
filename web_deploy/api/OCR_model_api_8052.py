import torch
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from types_ocr.sftp_account import sftp_account
from sftp_serve.take_file_from_cache import take_file_from_cache

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

model_path = str(os.getenv("MODEL_PATH", "llama-3.1"))
max_seq_length = int(os.getenv("MAX_SEQ_LENGTH", "2048"))

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
from querys.insert_2_dtb import insert_records_from_json


class Item(BaseModel):
    file_name: str


app = FastAPI()

model, tokenizer = load_model_and_tokenizer(
    model_path=model_path, max_seq_length=max_seq_length
)  # Llama 3.1 model for generating JSON from Markdown

converter = load_marker_model()  # Marker model for converting PDF to Markdown


@app.post("/convert-json", response_model=dict)
def convert_json(file: Item):
    """
    Endpoint to convert a PDF file to JSON format.
    :param file: PDF file name to be converted.
    """
    if file.file_name.endswith(".pdf") is False:
        return {"response": "File must be a PDF."}

    # NOTE: Convert PDF to JSON
    print("Generating JSON from Markdown...")
    if get_text_from_pdf(
        converter, folder_local_path=folder_local_path, file_name=file.file_name
    )["response"]:  # Convert PDF to Markdown
        print("-" * 50, file.file_name, "-" * 50)
        generated_output = gen_json(
            model,
            tokenizer,
            folder_local_path=folder_local_path,
            max_seq_length=max_seq_length,
        )  # Generate JSON from Markdown

        # NOTE: remove file from cache after processing
        os.remove(str(os.path.join(folder_local_path, file.file_name)))

        print("-" * 50, "END", "-" * 50)
        insert_records_from_json(json_data=generated_output)
        print("JSON generated and inserted into the database successfully.")

        return generated_output
    else:
        print("Failed to convert PDF to Markdown.")
        return {"response": False}


@app.get("/get-file-from-remote", response_model=dict)
async def get_file_from_remote():
    """
    Endpoint to retrieve a file from the remote SFTP server.
    """
    take_file_from_cache(
        folder_remote_path=folder_remote_path,
        folder_local_path=folder_local_path,
        account=account,
    )  # Timeout in minutes
    return {"message": "File retrieval initiated."}
