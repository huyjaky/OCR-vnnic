import requests
import multiprocessing
import os
import time
from utils.load_env import (
    md_cached_path,
    model_api,
)


# folder_remote_save_path = str(os.getenv("REMOTE_SAVE_PATH"))
# folder_remote_path_when_error = str(os.getenv("REMOTE_SAVE_PATH_WHEN_ERROR"))
# folder_local_path_when_error = str(os.getenv("ERROR_CACHE_PATH"))

# load_dotenv()
# folder_local_path = str(os.getenv("LOCAL_CACHE_PATH"))
# md_cached_path = str(os.getenv("MD_CACHED_PATH"))
# model_api = str(os.getenv("MODEL_API"))


def process_model_1(file_list):
    for file_name in file_list:
        if file_name.endswith(".txt"):
            try:
                x = requests.post(
                    f"{model_api}/convert-json-from-local-model-1",
                    json={"file_name": file_name},
                    timeout=3600,
                )
                print(f"[Model 1] Processed: {file_name}")
            except Exception as e:
                print(f"[Model 1] Error: {e}")


def process_model_2(file_list):
    for file_name in file_list:
        if file_name.endswith(".txt"):
            try:
                x = requests.post(
                    f"{model_api}/convert-json-from-local-model-2",
                    json={"file_name": file_name},
                    timeout=3600,
                )
                print(f"[Model 2] Processed: {file_name}")
            except Exception as e:
                print(f"[Model 2] Error: {e}")


while True:
    try:
        all_files = os.listdir(md_cached_path)
        txt_files = [f for f in all_files if f.endswith(".txt")]
        if not txt_files:
            print("No .txt files found. Waiting...")
            time.sleep(10)
            continue

        mid_index = len(txt_files) // 2
        model_1_files = txt_files[:mid_index]
        model_2_files = txt_files[mid_index:]

        p1 = multiprocessing.Process(target=process_model_1, args=(model_1_files,))
        p2 = multiprocessing.Process(target=process_model_2, args=(model_2_files,))

        p1.start()
        p2.start()

        p1.join()
        p2.join()

    except Exception as e:
        print(f"Error in main loop: {e}")

    print("Cycle complete. Waiting before next check...")
    time.sleep(10)
