import requests
import os
import time
import threading
from utils.load_env import model_api, md_cached_path


def server_model(txt_file: str, model_index: int):
    try:
        print(txt_file)
        response = requests.post(
            url=f"{model_api}/convert-json-from-local-model-{model_index}",
            json={"file_name": txt_file},
            timeout=20,
        )
        response_messages = response.json()
        print(response_messages)

    except Exception as e:
        print(f"Error in server_model({txt_file}, {model_index}): {e}")

    return True


while True:
    file_list = os.listdir(md_cached_path)
    txt_files = [f for f in file_list if f.endswith(".txt")]

    if not txt_files:
        print("No .txt files found. Waiting...")
        time.sleep(10)
        continue

    while txt_files:
        try:
            t1 = threading.Thread(target=server_model, args=(txt_files.pop(), 1))
            t2 = threading.Thread(target=server_model, args=(txt_files.pop(), 2))
            t1.start()
            t2.start()
            # Đợi thread xong trước khi tạo mới
            t1.join()
            t2.join()
        except IndexError:
            if len(txt_files) == 1:
                server_model(txt_files.pop(), 1)
            break
    if os.listdir(md_cached_path) == []:
        print("All files processed. Waiting for new files...")
        time.sleep(10)
