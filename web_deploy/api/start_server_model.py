import requests
import multiprocessing
import os
import time
from utils.load_env import (
    md_cached_path,
    model_api,
)


def worker_model_1(task_queue):
    """Worker cho model 1 - lấy task từ queue"""
    while True:
        try:
            # Lấy file từ queue (timeout sau 5 giây nếu không có task)
            try:
                file_name = task_queue.get(timeout=5)
                if file_name is None:  # Poison pill để dừng worker
                    break
            except:
                continue  # Timeout, tiếp tục loop

            try:
                x = requests.post(
                    f"{model_api}/convert-json-from-local-model-1",
                    json={"file_name": file_name},
                    timeout=3600,
                )
                print(f"[Model 1] Processed: {file_name}")
            except Exception as e:
                print(f"[Model 1] Error processing {file_name}: {e}")
            finally:
                print("[Model 1] Task done")

        except Exception as e:
            print(f"[Model 1] Worker error: {e}")


def worker_model_2(task_queue):
    """Worker cho model 2 - lấy task từ queue"""
    while True:
        try:
            # Lấy file từ queue (timeout sau 5 giây nếu không có task)
            try:
                file_name = task_queue.get(timeout=5)
                if file_name is None:  # Poison pill để dừng worker
                    break
            except:
                continue  # Timeout, tiếp tục loop

            try:
                x = requests.post(
                    f"{model_api}/convert-json-from-local-model-2",
                    json={"file_name": file_name},
                    timeout=3600,
                )
                print(f"[Model 2] Processed: {file_name}")
            except Exception as e:
                print(f"[Model 2] Error processing {file_name}: {e}")
            finally:
                print("[Model 2] Task done")

        except Exception as e:
            print(f"[Model 2] Worker error: {e}")


def file_monitor(queue1, queue2):
    """Monitor files và phân phối vào 2 queue"""
    processed_files = set()

    while True:
        try:
            all_files = os.listdir(md_cached_path)
            txt_files = [f for f in all_files if f.endswith(".txt")]

            if not txt_files:
                print("No .txt files found. Waiting...")
                time.sleep(10)
                continue

            # Chỉ xử lý các file mới
            new_files = [f for f in txt_files if f not in processed_files]

            if not new_files:
                time.sleep(5)
                continue

            print(f"Found {len(new_files)} new files to process")

            # Phân phối files vào 2 queue theo round-robin
            for i, file_name in enumerate(new_files):
                if i % 2 == 0:
                    queue1.put(file_name)
                    print(f"Assigned {file_name} to Model 1")
                else:
                    queue2.put(file_name)
                    print(f"Assigned {file_name} to Model 2")

                processed_files.add(file_name)

        except Exception as e:
            print(f"File monitor error: {e}")

        time.sleep(5)  # Kiểm tra files mới mỗi 5 giây


if __name__ == "__main__":
    # Tạo 2 queue riêng biệt cho mỗi model
    queue1 = multiprocessing.Queue()
    queue2 = multiprocessing.Queue()

    # Tạo các process
    p1 = multiprocessing.Process(target=worker_model_1, args=(queue1,))
    p2 = multiprocessing.Process(target=worker_model_2, args=(queue2,))
    monitor = multiprocessing.Process(target=file_monitor, args=(queue1, queue2))

    # Đặt daemon=True
    p1.daemon = True
    p2.daemon = True
    monitor.daemon = True

    # Khởi động các process
    p1.start()
    p2.start()
    monitor.start()

    try:
        # Giữ main process chạy và monitor health
        while True:
            if not p1.is_alive():
                print("Worker 1 died, restarting...")
                p1 = multiprocessing.Process(target=worker_model_1, args=(queue1,))
                p1.daemon = True
                p1.start()

            if not p2.is_alive():
                print("Worker 2 died, restarting...")
                p2 = multiprocessing.Process(target=worker_model_2, args=(queue2,))
                p2.daemon = True
                p2.start()

            if not monitor.is_alive():
                print("Monitor died, restarting...")
                monitor = multiprocessing.Process(
                    target=file_monitor, args=(queue1, queue2)
                )
                monitor.daemon = True
                monitor.start()

            time.sleep(10)

    except KeyboardInterrupt:
        print("Shutting down...")
        # Gửi poison pills để dừng workers gracefully
        queue1.put(None)
        queue2.put(None)

        p1.terminate()
        p2.terminate()
        monitor.terminate()

        p1.join()
        p2.join()
        monitor.join()
