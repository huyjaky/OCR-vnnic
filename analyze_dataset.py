import os
import json

list_cache = []
for foldername in os.listdir("./dataset/"):
    for filename in os.listdir(os.path.join("./dataset/", foldername)):
        if filename.endswith(".json"):
            filepath = os.path.join("./dataset/", foldername, filename)
            try:
                with open(filepath, "r") as file:
                    data = json.load(file)
                    # list_cache.append(len(data[0]["output"]["TaiSan"]))
                    list_cache.append(data[0]["output"]["LoaiHopDongName"])
            except Exception as e:
                data[0]["output"]["LoaiHopDongName"] = None
                with open(filepath, "w") as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                # print(f"Error processing {filepath}: {e}")
                # print(filename)
