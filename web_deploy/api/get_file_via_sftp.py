from types_ocr.sftp_account import sftp_account
from dotenv import load_dotenv
import os
from sftp_serve.take_file_from_cache import take_file_from_cache

load_dotenv()

from dotenv import load_dotenv

load_dotenv()
# Example usage
account = sftp_account(
    hostname=str(os.getenv("HOSTNAME_SSH")),
    port=int(os.getenv("PORT_SSH", "22")),
    username=str(os.getenv("USERNAME_SSH")),
    password=str(os.getenv("PASSWORD_SSH")),
)
timeout = int(os.getenv("TIMEOUT_SFTP", "5"))
folder_remote_path = str(os.getenv("REMOTE_CACHE_PATH"))
folder_local_path = str(os.getenv("LOCAL_CACHE_PATH"))
take_file_from_cache(
    folder_remote_path=folder_remote_path,
    folder_local_path=folder_local_path,
    account=account,
    timeout=timeout,
)  # Timeout in minutes
