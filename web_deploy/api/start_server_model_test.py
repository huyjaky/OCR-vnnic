import requests
import threading
import multiprocessing
import os
import time
import queue
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
from utils.load_models.marker_model import load_marker_model, get_text_from_pdf
from utils.sftp_serve.push_file_to_remote_when_error import (
    push_file_to_remote_when_error,
)
from utils.load_env import (
    account,
    folder_remote_path_when_error,
    folder_local_path_when_error,
    folder_local_path,
    md_cached_path,
    model_api,
)


print("[PDF Worker] Loading Marker model...")
converter = load_marker_model()
print("[PDF Worker] Model loaded successfully")


class OptimizedPDFProcessor:
    def __init__(self, max_queue_size=50, model_workers=2):
        # Multiprocessing queues for PDF worker
        self.pdf_queue = multiprocessing.Queue(maxsize=max_queue_size)
        self.result_queue = multiprocessing.Queue()

        # Thread-safe queue for model processing
        self.txt_queue = queue.Queue(maxsize=100)
        self.processed_files = set()
        self.processing_lock = threading.Lock()

        # Configuration
        self.max_queue_size = max_queue_size
        self.model_workers = model_workers
        self.shutdown_event = threading.Event()

        # Performance monitoring
        self.stats = {
            "pdf_processed": 0,
            "txt_processed": 0,
            "errors": 0,
            "start_time": time.time(),
        }

    def pdf_worker(self):
        """Enhanced PDF worker with better error handling"""
        try:
            while True:
                try:
                    file_info = self.pdf_queue.get(timeout=2)
                    if file_info is None:  # Shutdown signal
                        break

                    file_name, local_path, save_path = file_info
                    print(f"[PDF Worker] Processing: {file_name}")

                    start_time = time.time()
                    get_text_from_pdf(
                        converter=converter,
                        file_local_get_path=local_path,
                        file_local_save_path=save_path,
                        file_name=file_name,
                    )

                    process_time = time.time() - start_time
                    self.result_queue.put(
                        {
                            "status": "success",
                            "file": file_name,
                            "process_time": process_time,
                        }
                    )
                    self.stats["pdf_processed"] += 1

                except queue.Empty:
                    continue

                except RuntimeError as e:
                    if "CUDA out of memory" in str(e):
                        push_file_to_remote_when_error(
                            local_save_path=folder_local_path,
                            file_name=file_name,
                            account=account.sftp_account,
                            error_remote_path=folder_remote_path_when_error,
                            error_local_path=folder_local_path_when_error,
                            error_message=str(e),
                            model_index=0,
                            generated_output={"error": "oom"},
                        )
                        # Add delay for OOM recovery
                        time.sleep(5)

                    self.result_queue.put(
                        {"status": "error", "file": file_name, "error": str(e)}
                    )
                    self.stats["errors"] += 1

                except Exception as e:
                    self.result_queue.put(
                        {"status": "error", "file": file_name, "error": str(e)}
                    )
                    self.stats["errors"] += 1

        except Exception as e:
            print(f"[PDF Worker] Fatal error: {e}")
        finally:
            print("[PDF Worker] Shutting down")

    def model_worker(self, worker_id, model_endpoint):
        """Worker thread for model processing"""
        while not self.shutdown_event.is_set():
            try:
                file_name = self.txt_queue.get(timeout=1)
                if file_name is None:  # Shutdown signal
                    break

                start_time = time.time()
                response = requests.post(
                    f"{model_api}/{model_endpoint}",
                    json={"file_name": file_name},
                    timeout=30,
                )

                process_time = time.time() - start_time
                print(
                    f"[Model {worker_id}] Processed: {file_name} ({process_time:.2f}s)"
                )

                with self.processing_lock:
                    self.processed_files.add(file_name)
                    self.stats["txt_processed"] += 1

                self.txt_queue.task_done()

            except queue.Empty:
                continue
            except requests.exceptions.RequestException as e:
                print(f"[Model {worker_id}] Request error for {file_name}: {e}")
                self.stats["errors"] += 1
                self.txt_queue.task_done()
            except Exception as e:
                print(f"[Model {worker_id}] Error processing {file_name}: {e}")
                self.stats["errors"] += 1
                self.txt_queue.task_done()

    def result_monitor(self):
        """Monitor PDF processing results and feed to model workers"""
        completed_pdfs = []

        while not self.shutdown_event.is_set():
            try:
                # Non-blocking check for results
                try:
                    result = self.result_queue.get_nowait()
                    print(f"[PDF Result] {result['status']}: {result['file']}")

                    if result["status"] == "success":
                        completed_pdfs.append(result["file"])
                        # Convert PDF name to TXT name
                        txt_file = result["file"].replace(".pdf", ".txt")

                        # Add to model processing queue
                        try:
                            self.txt_queue.put(txt_file, timeout=1)
                        except queue.Full:
                            print(f"[Warning] Model queue full, dropping {txt_file}")

                except queue.Empty:
                    pass

                time.sleep(0.1)  # Small delay to prevent busy waiting

            except Exception as e:
                print(f"[Result Monitor] Error: {e}")

    def scan_and_queue_pdfs(self):
        """Continuously scan for new PDFs and queue them"""
        processed_pdfs = set()

        while not self.shutdown_event.is_set():
            try:
                if not os.path.exists(folder_local_path):
                    time.sleep(5)
                    continue

                current_pdfs = set(
                    f for f in os.listdir(folder_local_path) if f.endswith(".pdf")
                )

                # Find new PDFs
                new_pdfs = current_pdfs - processed_pdfs

                for pdf_file in new_pdfs:
                    try:
                        self.pdf_queue.put(
                            (pdf_file, folder_local_path, md_cached_path), timeout=1
                        )
                        processed_pdfs.add(pdf_file)
                        print(f"[Scanner] Queued: {pdf_file}")

                    except queue.Full:
                        print(f"[Scanner] PDF queue full, will retry {pdf_file}")
                        break  # Try again next cycle

                time.sleep(2)  # Scan interval

            except Exception as e:
                print(f"[Scanner] Error: {e}")
                time.sleep(5)

    def process_existing_txt_files(self):
        """Process existing TXT files that may have been left over"""
        try:
            if not os.path.exists(md_cached_path):
                os.makedirs(md_cached_path, exist_ok=True)
                return

            existing_txt_files = [
                f for f in os.listdir(md_cached_path) if f.endswith(".txt")
            ]

            for txt_file in existing_txt_files:
                if txt_file not in self.processed_files:
                    try:
                        self.txt_queue.put(txt_file, timeout=1)
                    except queue.Full:
                        break

            print(f"[Startup] Queued {len(existing_txt_files)} existing TXT files")

        except Exception as e:
            print(f"[Startup] Error processing existing files: {e}")

    def print_stats(self):
        """Print performance statistics"""
        while not self.shutdown_event.is_set():
            runtime = time.time() - self.stats["start_time"]
            pdf_rate = self.stats["pdf_processed"] / max(runtime, 1)
            txt_rate = self.stats["txt_processed"] / max(runtime, 1)

            print(
                f"\n[Stats] Runtime: {runtime:.1f}s | "
                f"PDFs: {self.stats['pdf_processed']} ({pdf_rate:.2f}/s) | "
                f"TXTs: {self.stats['txt_processed']} ({txt_rate:.2f}/s) | "
                f"Errors: {self.stats['errors']} | "
                f"PDF Queue: {self.pdf_queue.qsize()} | "
                f"TXT Queue: {self.txt_queue.qsize()}"
            )

            time.sleep(10)

    def run(self):
        """Main execution loop"""
        # Start PDF worker process
        pdf_process = multiprocessing.Process(target=self.pdf_worker)
        pdf_process.start()

        # Process existing TXT files
        self.process_existing_txt_files()

        # Start background threads
        threads = []

        # Result monitor thread
        result_thread = threading.Thread(target=self.result_monitor)
        result_thread.start()
        threads.append(result_thread)

        # PDF scanner thread
        scanner_thread = threading.Thread(target=self.scan_and_queue_pdfs)
        scanner_thread.start()
        threads.append(scanner_thread)

        # Stats thread
        stats_thread = threading.Thread(target=self.print_stats)
        stats_thread.start()
        threads.append(stats_thread)

        # Model worker threads
        with ThreadPoolExecutor(max_workers=self.model_workers) as executor:
            # Start model workers
            model_futures = []
            for i in range(self.model_workers):
                # Alternate between model endpoints
                endpoint = (
                    "convert-json-from-local-model-1"
                    if i % 2 == 0
                    else "convert-json-from-local-model-2"
                )

                # endpoint = (
                #     "convert-json-from-local-model-1"
                #     if i % 4 == 0
                #     else "convert-json-from-local-model-4"
                #     if i % 3 == 0
                #     else "convert-json-from-local-model-3"
                #     if i % 2 == 0
                #     else "convert-json-from-local-model-2"
                # )
                future = executor.submit(self.model_worker, i, endpoint)
                model_futures.append(future)

            try:
                print("[Main] All workers started, processing files...")

                # Main loop - just monitor and handle shutdown
                while True:
                    time.sleep(1)

                    # Check if PDF process is alive
                    if not pdf_process.is_alive():
                        print("[Main] PDF process died, restarting...")
                        pdf_process = multiprocessing.Process(target=self.pdf_worker)
                        pdf_process.start()

            except KeyboardInterrupt:
                print("[Main] Shutdown requested...")

        # Cleanup
        self.shutdown()

        # Wait for PDF process
        self.pdf_queue.put(None)  # Shutdown signal
        pdf_process.join(timeout=10)
        if pdf_process.is_alive():
            pdf_process.terminate()
            pdf_process.join()

        # Wait for threads
        for thread in threads:
            thread.join(timeout=5)

        print("[Main] Shutdown complete")

    def shutdown(self):
        """Graceful shutdown"""
        print("[Shutdown] Initiating graceful shutdown...")
        self.shutdown_event.set()

        # Signal model workers to stop
        for _ in range(self.model_workers):
            try:
                self.txt_queue.put(None, timeout=1)
            except queue.Full:
                pass


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("Graceful shutdown initiated...")
    if "processor" in globals():
        processor.shutdown()
    sys.exit(0)


def main():
    global processor

    # Configuration
    MAX_QUEUE_SIZE = int(os.getenv("PDF_QUEUE_SIZE", 30))
    MODEL_WORKERS = int(os.getenv("MODEL_WORKERS", 2))

    print(f"[Config] PDF Queue Size: {MAX_QUEUE_SIZE}, Model Workers: {MODEL_WORKERS}")

    processor = OptimizedPDFProcessor(
        max_queue_size=MAX_QUEUE_SIZE, model_workers=MODEL_WORKERS
    )

    try:
        processor.run()
    except Exception as e:
        print(f"[Main] Fatal error: {e}")
        processor.shutdown()


if __name__ == "__main__":
    # Set spawn method for CUDA compatibility
    multiprocessing.set_start_method("spawn", force=True)

    # Handle signals gracefully
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        print("Program terminated")
