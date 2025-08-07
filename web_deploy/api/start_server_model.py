from dotenv import load_dotenv
import requests
import threading
import multiprocessing
import os
import time
import queue
import signal
import sys
from utils.load_models.marker_model import load_marker_model, get_text_from_pdf
load_dotenv()
folder_local_path = str(os.getenv("LOCAL_CACHE_PATH"))
md_cached_path = str(os.getenv("MD_CACHED_PATH"))

def process_model_1(file_list):
    for file_name in file_list:
        if file_name.endswith(".txt"):
            try:
                x = requests.post(
                    "http://localhost:8052/convert-json-from-local-model-1",
                    json={"file_name": file_name},
                    timeout=30,
                )
                print(f"[Model 1] Processed: {file_name}")
            except Exception as e:
                print(f"[Model 1] Error: {e}")


def process_model_2(file_list):
    for file_name in file_list:
        if file_name.endswith(".txt"):
            try:
                x = requests.post(
                    "http://localhost:8052/convert-json-from-local-model-2",
                    json={"file_name": file_name},
                    timeout=30,
                )
                print(f"[Model 2] Processed: {file_name}")
            except Exception as e:
                print(f"[Model 2] Error: {e}")


converter = load_marker_model()


def pdf_worker(pdf_queue, result_queue):
    """Worker process for PDF conversion - load model inside process"""
    try:
        print("[PDF Worker] Loading Marker model...")
        # Import và load model TRONG process này

        print("[PDF Worker] Model loaded successfully")

        while True:
            try:
                # Get PDF file from queue with timeout
                file_info = pdf_queue.get(timeout=5)

                if file_info is None:  # Poison pill to stop worker
                    break

                file_name, local_path, save_path = file_info

                print(f"[PDF Worker] Processing: {file_name}")
                get_text_from_pdf(
                    converter=converter,
                    file_local_get_path=local_path,
                    file_local_save_path=save_path,
                    file_name=file_name,
                )

                result_queue.put(f"Completed: {file_name}")
                pdf_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                result_queue.put(f"Error processing {file_name}: {e}")
                print(f"[PDF Worker] Error: {e}")

    except Exception as e:
        print(f"[PDF Worker] Fatal error: {e}")
    finally:
        print("[PDF Worker] Shutting down")


def main():
    # Create queues for communication with PDF worker
    pdf_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    # Start PDF worker process
    pdf_process = multiprocessing.Process(
        target=pdf_worker, args=(pdf_queue, result_queue)
    )

    pdf_process.start()

    try:
        while True:
            try:
                if len(os.listdir(folder_local_path)) == 1:
                    print("Waiting for new files to be added to the cache server...")
                    time.sleep(5)
                    continue

                # Get file lists
                md_files = []
                try:
                    md_files = [
                        f for f in os.listdir(md_cached_path) if f.endswith(".txt")
                    ]
                except FileNotFoundError:
                    os.makedirs(md_cached_path, exist_ok=True)

                pdf_files = [
                    f for f in os.listdir(folder_local_path) if f.endswith(".pdf")
                ]

                # Start HTTP processing threads
                threads = []

                if md_files:
                    if len(md_files) % 2 == 0:
                        file_list_model_1 = md_files[: len(md_files) // 2]
                        file_list_model_2 = md_files[len(md_files) // 2 :]
                    else:
                        file_list_model_1 = md_files[: len(md_files) // 2 + 1]
                        file_list_model_2 = md_files[len(md_files) // 2 + 1 :]

                    t1 = threading.Thread(
                        target=process_model_1, args=(file_list_model_1,)
                    )
                    t2 = threading.Thread(
                        target=process_model_2, args=(file_list_model_2,)
                    )

                    threads.extend([t1, t2])

                # Send PDF files to worker process
                if pdf_files:
                    for pdf_file in pdf_files:
                        pdf_queue.put((pdf_file, folder_local_path, md_cached_path))

                # Start HTTP threads
                for thread in threads:
                    thread.start()

                # Wait for threads to complete
                for thread in threads:
                    thread.join()

                # Check PDF results (non-blocking)
                pdf_results = []
                try:
                    while True:
                        result = result_queue.get_nowait()
                        pdf_results.append(result)
                        print(f"[PDF Result] {result}")
                except queue.Empty:
                    pass

                print("Cycle completed")
                time.sleep(10)

            except KeyboardInterrupt:
                print("Stopping main loop...")
                break
            except Exception as e:
                print(f"Main loop error: {e}")
                time.sleep(5)

    finally:
        print("Shutting down...")
        # Stop PDF worker
        pdf_queue.put(None)  # Poison pill
        pdf_process.join(timeout=10)

        if pdf_process.is_alive():
            print("Force terminating PDF process...")
            pdf_process.terminate()
            pdf_process.join()


# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("Graceful shutdown initiated...")
    sys.exit(0)

if __name__ == "__main__":
    # Set spawn method for CUDA compatibility
    multiprocessing.set_start_method("spawn", force=True)

    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal_handler)

    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        print("Program terminated")
