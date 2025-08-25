from fastapi import FastAPI
from utils.sftp_serve.take_file_from_cache import take_file_from_cache
from utils.load_env import (
    folder_remote_path,
    folder_local_path,
    folder_remote_path_when_error,
    folder_local_path_when_error,
    account,
)

app = FastAPI()

@app.get("/get-file-from-remote", response_model=dict)
async def get_file_from_remote():
    """
    Endpoint to retrieve a file from the remote SFTP server.
    """
    take_file_from_cache(
        account=account.sftp_account,
        folder_local_path=folder_local_path,
        folder_remote_path_when_error=folder_remote_path_when_error,
        folder_local_path_when_error=folder_local_path_when_error,
        folder_remote_save_path=folder_remote_path,
        model_index=0,
    )  # Timeout in minutes
    return {"message": "File retrieval initiated."}
