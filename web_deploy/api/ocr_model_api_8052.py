import os

import torch
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
md_cached_path = str(os.getenv("MD_CACHED_PATH"))
folder_remote_path_when_error = str(os.getenv("REMOTE_SAVE_PATH_WHEN_ERROR"))
folder_local_path_when_error = str(os.getenv("ERROR_CACHE_PATH"))

model_path = str(os.getenv("MODEL_PATH", "llama-3.1"))
max_seq_length = int(os.getenv("MAX_SEQ_LENGTH", "2048"))

# FIXED: Unsloth and PyTorch Dynamo conflict
# WARNING: Must configure OS before importing Unsloth
os.environ["PYTORCH_DISABLE_DYNAMO"] = "1"
os.environ["TORCH_COMPILE_DISABLE"] = "1"
# Turn off dynamo config
torch._dynamo.config.disable = True
torch._dynamo.config.suppress_errors = True

from fastapi import FastAPI, File, HTTPException, UploadFile
from querys.insert_2_dtb import insert_records_from_json
from utils.load_models.major_model import gen_json, load_model_and_tokenizer
from utils.sftp_serve.push_file_to_remote_save_path import push_file_to_remote_save_path
from utils.sftp_serve.push_file_to_remote_when_error import (
    push_file_to_remote_when_error,
)


class Item(BaseModel):
    file_name: str


app = FastAPI()

model_1, tokenizer = load_model_and_tokenizer(
    model_path=model_path, max_seq_length=max_seq_length, cuda_index=0
)  # Llama 3.1 model for generating JSON from Markdown


model_2, tokenizer = load_model_and_tokenizer(
    model_path=model_path, max_seq_length=max_seq_length, cuda_index=1
)  # Llama 3.1 model for generating JSON from Markdown


def convert_to_json(file_name: str, model, index: int) -> dict:
    # NOTE: Convert PDF to JSON
    print("Generating JSON from Markdown...")
    print("-" * 50, file_name, "-" * 50)

    try:
        generated_output = gen_json(
            model,
            tokenizer,
            file_local_path=str(os.path.join(md_cached_path, file_name)),
            max_seq_length=max_seq_length,
            cuda_index=index,  # Use the first GPU for model_1
        )  # Generate JSON from Markdown

        push_file_to_remote_save_path(
            account=account,
            file_name=file_name,
            # folder_remote_get_path=folder_remote_path,
            folder_remote_save_path=folder_remote_save_path,
            local_save_path=folder_local_path,
            datetime_folder=str(
                generated_output["ThoiDiemDangKy"]
            ),  # Assuming the file name is in the
        )

        print("-" * 50, "END", "-" * 50)
        insert_records_from_json(json_input=generated_output, file_name=file_name)
        print("JSON generated and inserted into the database successfully.")

    except Exception as e:
        print(f"Error generating JSON: {e}")
        push_file_to_remote_when_error(
            local_save_path=folder_local_path,
            file_name=file_name,
            account=account,
            error_remote_path=folder_remote_path_when_error,
            error_local_path=folder_local_path_when_error,
            error_message=str(e),
            model_index=index,
        )

    # NOTE: remove file from cache after processing
    # file_name = <file_name>.txt
    os.remove(str(os.path.join(md_cached_path, file_name)))
    os.remove(str(os.path.join(folder_local_path, file_name.replace(".txt", ".pdf"))))

    return {"response": True}


@app.post("/convert-json-from-local-model-1", response_model=dict)
def convert_json_model_1(file: Item):
    """
    Endpoint to convert a PDF file to JSON format.
    :param file: PDF file name to be converted.
    """
    if file.file_name.endswith(".txt") is False:
        return {"response": "File must be a txt."}
    return convert_to_json(file_name=file.file_name, model=model_1, index=0)


@app.post("/convert-json-from-local-model-2", response_model=dict)
def convert_json_model_2(file: Item):
    """
    Endpoint to convert a PDF file to JSON format.
    :param file: PDF file name to be converted.
    """
    if file.file_name.endswith(".txt") is False:
        return {"response": "File must be a txt."}
    return convert_to_json(file_name=file.file_name, model=model_2, index=1)


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

        return convert_to_json(file_name=str(file.filename), model=model_1, index=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e!s}")
