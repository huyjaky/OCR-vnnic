from utils.load_models.marker_model import load_marker_model, get_text_from_pdf
import os
import time
from utils.load_env import folder_local_path, md_cached_path

print("[PDF Worker] Loading Marker model...")
converter = load_marker_model()
print("[PDF Worker] Model loaded successfully")

# get_text_from_pdf(
#     converter=converter,
#     file_local_get_path=local_path,
#     file_local_save_path=save_path,
#     file_name=file_name,
# )

while True:
    try:
        all_files = os.listdir(folder_local_path)
        pdf_files = [f for f in all_files if f.endswith(".pdf")]
        if not pdf_files:
            print("[PDF Worker] No .pdf files found. Waiting...")
            time.sleep(10)
            continue

        for pdf in pdf_files:
            get_text_from_pdf(
                converter=converter,
                file_local_get_path=folder_local_path,
                file_local_save_path=md_cached_path,
                file_name=pdf,
            )
    except Exception as e:
        print(f"[PDF Worker] General error: {e}")
        time.sleep(10)
