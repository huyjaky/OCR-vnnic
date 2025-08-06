from dotenv import load_dotenv
import requests
load_dotenv()
import os 
import time 
from tqdm import tqdm

folder_local_path = str(os.getenv("LOCAL_CACHE_PATH"))

while True:
    if len(os.listdir(folder_local_path)) == 1:
        print("Waiting for new files to be added to the cache server...")
        time.sleep(5)
    else:
        for file_name in os.listdir(folder_local_path):
            x = requests.post("http://localhost:8052/convert-json-from-local", json={"file_name": file_name})
