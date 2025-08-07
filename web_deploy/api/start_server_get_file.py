from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
import os
import time
import requests

timeout = int(os.getenv("TIMEOUT_SFTP", "5"))  # Default to 5 minutes if not set
while True:
    get_file = requests.get("http://localhost:8053/get-file-from-remote")
    timeout_bar = tqdm(
        range(timeout * 60), desc="Waiting for new files", unit="seconds"
    )
    for _ in range(timeout * 60):
        timeout_bar.update(1)
        time.sleep(1)  # Sleep for 1 second in each iteration
