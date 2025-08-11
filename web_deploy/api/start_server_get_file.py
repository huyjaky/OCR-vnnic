from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()
import os
import time
import requests

timeout = int(os.getenv("TIMEOUT_SFTP", "1"))  # Default to 5 minutes if not set
folder_local_path = str(os.getenv("LOCAL_CACHE_PATH"))
get_file_api = str(os.getenv("GET_FILE_API"))

while True:
    # NOTE: prevent fetching new files when file was processed
    if len(os.listdir(folder_local_path)) != 0:
        print("Waiting for new files to be added to the cache server...")
        time.sleep(5)
        continue

    get_file = requests.get(f"{get_file_api}/get-file-from-remote")
    timeout_bar = tqdm(
        range(timeout * 60), desc="Waiting for new files", unit="seconds"
    )
    for _ in range(timeout * 60):
        timeout_bar.update(1)
        time.sleep(1)  # Sleep for 1 second in each iteration
