from fastapi import FastAPI
from utils.sftp_serve.take_file_from_cache import take_file_from_cache
from dotenv import load_dotenv
import os
from types_ocr.sftp_account import sftp_account

load_dotenv()

timeout = int(os.getenv("TIMEOUT_SFTP", "5"))
folder_remote_save_path = str(os.getenv("REMOTE_CACHE_PATH"))
folder_local_path = str(os.getenv("LOCAL_CACHE_PATH"))
folder_remote_save_path_when_error = str(os.getenv("REMOTE_SAVE_PATH_WHEN_ERROR"))

account = sftp_account(
    hostname=str(os.getenv("HOSTNAME_SSH")),
    port=int(os.getenv("PORT_SSH", "22")),
    username=str(os.getenv("USERNAME_SSH")),
    password=str(os.getenv("PASSWORD_SSH")),
)

app = FastAPI()


@app.get("/get-file-from-remote", response_model=dict)
async def get_file_from_remote():
    """
    Endpoint to retrieve a file from the remote SFTP server.
    """
    take_file_from_cache(
        folder_remote_save_path=folder_remote_save_path,
        folder_local_path=folder_local_path,
        account=account,
        folder_remote_save_path_when_error=folder_remote_save_path_when_error,
    )  # Timeout in minutes
    return {"message": "File retrieval initiated."}
