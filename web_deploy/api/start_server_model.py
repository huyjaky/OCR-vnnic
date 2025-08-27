import requests
import multiprocessing
import os
import time
from utils.load_env import md_cached_path, model_api


class WorkerStats:
    def __init__(self):
        self.manager = multiprocessing.Manager()
        self.stats = self.manager.dict(
            {
                "model1": {"busy": False, "processed": 0, "last_active": time.time()},
                "model2": {"busy": False, "processed": 0, "last_active": time.time()},
            }
        )


def worker(model_id, shared_queue, stats):
    """Universal worker for both models"""
    endpoint = f"/convert-json-from-local-model-{model_id}"
    worker_key = f"model{model_id}"

    while True:
        try:
            file_name = shared_queue.get(timeout=5)
            if file_name is None:
                break

            # Mark as busy
            stats[worker_key]["busy"] = True
            start_time = time.time()

            try:
                requests.post(
                    f"{model_api}{endpoint}",
                    json={"file_name": file_name},
                    timeout=3600,
                )
                print(f"[Model {model_id}] ✓ {file_name}")
                stats[worker_key]["processed"] += 1
            except Exception as e:
                print(f"[Model {model_id}] ✗ {file_name}: {e}")

            # Update stats
            stats[worker_key].update({"busy": False, "last_active": time.time()})

        except multiprocessing.TimeoutError:
            continue
        except Exception as e:
            print(f"[Model {model_id}] Worker error: {e}")
            stats[worker_key]["busy"] = False


def get_best_worker(stats):
    """Get least busy worker based on dynamic stats"""
    current_time = time.time()

    # Check if workers are responsive (active within last 60s)
    model1_responsive = current_time - stats["model1"]["last_active"] < 60
    model2_responsive = current_time - stats["model2"]["last_active"] < 60

    # Prefer non-busy and responsive workers
    if not stats["model1"]["busy"] and model1_responsive:
        if not stats["model2"]["busy"] and model2_responsive:
            # Both free, choose less loaded one
            return (
                1 if stats["model1"]["processed"] <= stats["model2"]["processed"] else 2
            )
        return 1
    elif not stats["model2"]["busy"] and model2_responsive:
        return 2

    # Both busy or unresponsive, use round-robin as fallback
    return (
        1
        if (stats["model1"]["processed"] + stats["model2"]["processed"]) % 2 == 0
        else 2
    )


def file_monitor(shared_queue, stats):
    """Monitor files and distribute with dynamic load balancing"""
    processed_files = set()

    while True:
        try:
            txt_files = [f for f in os.listdir(md_cached_path) if f.endswith(".txt")]
            new_files = [f for f in txt_files if f not in processed_files]

            if new_files:
                print(f"Found {len(new_files)} new files")

                for file_name in new_files:
                    shared_queue.put(file_name)
                    processed_files.add(file_name)

                    # Log assignment decision
                    best_worker = get_best_worker(stats)
                    print(f"Queued: {file_name} (next: Model {best_worker})")

            # Print stats every 30 seconds
            if int(time.time()) % 30 == 0:
                print(
                    f"Stats - Model1: {stats['model1']['processed']} files, "
                    f"Model2: {stats['model2']['processed']} files, "
                    f"Queue: ~{shared_queue.qsize()}"
                )

        except Exception as e:
            print(f"Monitor error: {e}")

        time.sleep(5)


def main():
    # Shared resources
    shared_queue = multiprocessing.Queue()
    stats = WorkerStats()

    # Create processes
    processes = [
        multiprocessing.Process(target=worker, args=(1, shared_queue, stats.stats)),
        multiprocessing.Process(target=worker, args=(2, shared_queue, stats.stats)),
        multiprocessing.Process(target=file_monitor, args=(shared_queue, stats.stats)),
    ]

    # Start all processes
    for p in processes:
        p.daemon = True
        p.start()

    try:
        # Simple health monitoring
        while True:
            alive_count = sum(1 for p in processes if p.is_alive())
            if alive_count < len(processes):
                print(f"Only {alive_count}/{len(processes)} processes alive!")
            time.sleep(30)

    except KeyboardInterrupt:
        print("Shutting down...")
        shared_queue.put(None)  # Stop workers
        shared_queue.put(None)

        for p in processes:
            p.terminate()
            p.join(timeout=5)


if __name__ == "__main__":
    main()
