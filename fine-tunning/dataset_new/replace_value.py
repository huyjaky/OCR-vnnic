import os
import json

dir_path = "./extra_data_1/"

def get_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)[0]["output"]

def replace_loai_don(data):
    # NOTE: Insert key:value u want change
    data["LoaiDonID"] = 2
    data["LoaiDonName"] = "Đăng ký thay đổi"
    data["LoaiDonCode"] = "TĐ"
    return data

def save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        # ensure_ascii=False để hiển thị tiếng Việt chuẩn
        json.dump([{"output": data}], file, ensure_ascii=False, indent=4)

for file_name in os.listdir(dir_path):
    if file_name.endswith(".json") and file_name.startswith("2"):
        file_path = os.path.join(dir_path, file_name)
        try:
            data = get_json(file_path)
            save_json(replace_loai_don(data), file_path)
            print(f"✅ Đã xử lý {file_name}")
        except Exception as e:
            print(f"⚠ Lỗi file {file_name}: {e}")
