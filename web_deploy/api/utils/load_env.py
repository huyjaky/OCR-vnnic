import os
from types_ocr.account import Account
from types_ocr.sftp_account import SftpAccount
from types_ocr.dtb_account import DtbAccount
from dotenv import load_dotenv

load_dotenv()

max_seq_length = int(os.getenv("MAX_SEQ_LENGTH", "2048"))
timeout = int(os.getenv("TIMEOUT_GET_FILE", "5"))
model_path = str(os.getenv("MODEL_PATH", "llama-3.1"))

folder_remote_path = str(os.getenv("REMOTE_CACHE_PATH"))
folder_remote_save_path = str(os.getenv("REMOTE_SAVE_PATH"))
folder_remote_path_when_error = str(os.getenv("REMOTE_SAVE_PATH_WHEN_ERROR"))

md_cached_path = str(os.getenv("MD_CACHED_PATH"))
folder_local_path = str(os.getenv("PDF_CACHE_PATH"))
folder_local_path_when_error = str(os.getenv("ERROR_CACHE_PATH"))


model_api = str(os.getenv("MODEL_API"))
get_file_api = str(os.getenv("GET_FILE_API"))

account = Account(
    sftp_account=SftpAccount(
        hostname=str(os.getenv("HOSTNAME_SSH")),
        port=int(os.getenv("PORT_SSH", "22")),
        username=str(os.getenv("USERNAME_SSH")),
        password=str(os.getenv("PASSWORD_SSH")),
        timeout=int(os.getenv("TIMEOUT_SFTP", "5")),
        banner_timeout=int(os.getenv("BANNER_TIMEOUT_SFTP", "5")),
    ),
    dtb_account=DtbAccount(
        server=str(os.getenv("DTB_SERVER")),
        database=str(os.getenv("DTB_NAME")),
        uid=str(os.getenv("DTB_UID")),
        password=str(os.getenv("DTB_PWD")),
    ),
)
