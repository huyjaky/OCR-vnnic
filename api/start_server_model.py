import requests
import os
import time
import threading
from utils.load_env import model_api, md_cached_path, folder_local_path_when_error


def server_model(txt_file: str, model_index: int):
    try:
        print("-" * 80)
        print(txt_file)
        response = requests.post(
            url=f"{model_api}/convert-json-from-local-model-{model_index}",
            json={"file_name": txt_file},
            timeout=60,
        )
        response_messages = response.json()
        print(f"{response_messages} | {len(os.listdir(folder_local_path_when_error))} | Model {model_index}")

    except Exception as e:
        print(f"Error in server_model({txt_file}, {model_index}): {e}")

    print("-" * 80)
    return True


def looping_pull(txt_files: list, model_index: int):
    for _ in range(len(txt_files)):
        server_model(txt_files.pop(), model_index)


while True:
    file_list = os.listdir(md_cached_path)
    txt_files = [f for f in file_list if f.endswith(".txt")]

    if not txt_files:
        print("No .txt files found. Waiting...")
        time.sleep(10)
        continue

    t1 = threading.Thread(target=looping_pull, args=(txt_files, 1))
    t2 = threading.Thread(target=looping_pull, args=(txt_files, 2))

    while txt_files != []:
        try:
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        except IndexError:
            break

    if os.listdir(md_cached_path) == []:
        print("All files processed. Waiting for new files...")
        time.sleep(10)
