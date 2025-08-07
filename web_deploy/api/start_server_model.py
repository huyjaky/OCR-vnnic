from dotenv import load_dotenv
import requests
import threading

load_dotenv()
import os
import time

folder_local_path = str(os.getenv("LOCAL_CACHE_PATH"))


def process_model_1(file_list):
    for file_name in file_list:
        x = requests.post(
            "http://localhost:8052/convert-json-from-local-model-1",
            json={"file_name": file_name},
        )
        print(f"[Model 1] Processed: {file_name}")


def process_model_2(file_list):
    for file_name in file_list:
        x = requests.post(
            "http://localhost:8052/convert-json-from-local-model-2",
            json={"file_name": file_name},
        )
        print(f"[Model 2] Processed: {file_name}")


while True:
    if len(os.listdir(folder_local_path)) == 1:
        print("Waiting for new files to be added to the cache server...")
        time.sleep(5)
    else:
        file_list = os.listdir(folder_local_path)
        file_list_model_1 = []
        file_list_model_2 = []
        if len(file_list) % 2 == 0:
            file_list_model_1 = file_list[: len(file_list) // 2]
            file_list_model_2 = file_list[len(file_list) // 2 :]
        else:
            file_list_model_1 = file_list[: len(file_list) // 2 + 1]
            file_list_model_2 = file_list[len(file_list) // 2 + 1 :]

        t1 = threading.Thread(target=process_model_1, args=(file_list_model_1,))
        t2 = threading.Thread(target=process_model_2, args=(file_list_model_2,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
