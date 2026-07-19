# OCR-vnnic

Hệ thống OCR + AI trích xuất thông tin hồ sơ từ PDF tiếng Việt sang JSON có cấu trúc, phục vụ quy trình xử lý nghiệp vụ tự động.

## 1) Mục tiêu dự án

Repo này tập trung vào 3 mục tiêu chính:

- Tự động đọc tài liệu PDF (hợp đồng/hồ sơ) và chuyển về dạng text/markdown.
- Dùng mô hình LLM để trích xuất các trường nghiệp vụ quan trọng sang JSON chuẩn.
- Đưa dữ liệu sau trích xuất vào luồng xử lý backend (lưu trữ, đồng bộ, kiểm tra lỗi).

## 2) Ý tưởng cốt lõi

Pipeline được thiết kế theo hướng **end-to-end**:

1. Nhận file PDF từ vùng cache (SFTP).
2. OCR/PDF parsing để tạo text markdown.
3. Dùng LLM sinh JSON theo schema nghiệp vụ.
4. Tiền xử lý JSON để chuẩn hóa trường dữ liệu.
5. Ghi kết quả vào database và đẩy file về vùng lưu trữ phù hợp.
6. Tách luồng lỗi riêng để dễ theo dõi và xử lý lại.

## 3) Cấu trúc thư mục chính

```text
OCR-vnnic/
├── analyze_dataset.py                 # Script rà soát/chỉnh dữ liệu dataset JSON
├── fine-tunning/                      # Khu vực chuẩn bị dữ liệu + fine-tune mô hình
│   ├── fine-tunning.py                # Script huấn luyện chính (Unsloth/TRL)
│   ├── preprocessing-data.ipynb       # Notebook tiền xử lý dữ liệu
│   ├── dataset_new/                   # Dữ liệu huấn luyện và script chuẩn hóa
│   └── ...                            # checkpoint/model artifacts
├── web_deploy/
│   ├── api/
│   │   ├── ocr_model_api_8052.py      # API suy luận JSON từ markdown
│   │   ├── get_file_from_remote_api_8053.py  # API lấy file từ cache SFTP
│   │   ├── start_server_model.py      # Orchestrator xử lý PDF -> markdown -> model
│   │   ├── querys/                    # Tiền xử lý + insert dữ liệu DB
│   │   └── utils/                     # load model, SFTP helpers, prompt
│   └── client/                        # Streamlit UI demo hiển thị kết quả
└── Progress.md / Plan.md              # Ghi chú tiến trình và ý tưởng
```

## 4) Các thành phần kỹ thuật

### OCR / PDF parsing
- `marker-pdf`: chuyển PDF sang markdown/text.

### AI extraction
- Mô hình LLM fine-tune bằng Unsloth/TRL.
- Tối ưu theo bài toán trích xuất thông tin tiếng Việt theo schema JSON.

### Backend/API
- `FastAPI` cho các endpoint xử lý.
- Luồng xử lý có tách worker và chia tải model.

### Data & storage integration
- Kết nối SFTP để nhận/trả file.
- Tiền xử lý dữ liệu trước khi insert SQL Server (`pyodbc`).

### Demo UI
- `Streamlit` để upload file và hiển thị JSON/trường đã trích xuất.

## 5) Luồng chạy tổng quát

1. Service lấy file PDF mới từ remote cache.
2. Service chuyển PDF sang `.txt` (markdown text).
3. API model đọc `.txt` và sinh JSON nghiệp vụ.
4. JSON được chuẩn hóa field (Loại đơn, thông tin bên giao/bên nhận, địa chỉ...).
5. Dữ liệu được ghi vào database.
6. File thành công/lỗi được chuyển về thư mục remote tương ứng.

## 6) Điểm nổi bật khi trình bày với HR

- Dự án thể hiện năng lực **ML + Backend + Data Pipeline** trong một hệ thống thực tế.
- Có tư duy **production workflow**: queue/worker, xử lý lỗi, đồng bộ file, tích hợp DB.
- Chủ động làm cả phần:
  - xây dựng dataset,
  - fine-tune mô hình,
  - triển khai API,
  - dựng giao diện demo.

## 7) Công nghệ chính

- Python
- FastAPI
- Streamlit
- marker-pdf
- Unsloth, TRL, Transformers
- Paramiko (SFTP), pyodbc (SQL Server)

## 8) Chạy nhanh (mức tham khảo)

> Lưu ý: repo chứa nhiều artifact huấn luyện và cấu hình nội bộ. Khi public, nên tách thông tin nhạy cảm và chuẩn hóa biến môi trường trước khi chạy.

```bash
# 1) Cài dependencies (ví dụ cho deploy)
pip install -r /home/runner/work/OCR-vnnic/OCR-vnnic/web_deploy/api/requirements.txt
pip install -r /home/runner/work/OCR-vnnic/OCR-vnnic/web_deploy/requirements.txt

# 2) Chạy API lấy file từ remote cache
python /home/runner/work/OCR-vnnic/OCR-vnnic/web_deploy/api/get_file_from_remote_api_8053.py

# 3) Chạy orchestrator xử lý model
python /home/runner/work/OCR-vnnic/OCR-vnnic/web_deploy/api/start_server_model.py

# 4) (Tùy chọn) chạy client demo
streamlit run /home/runner/work/OCR-vnnic/OCR-vnnic/web_deploy/client/main.py
```

## 9) Gợi ý trước khi public repo

- Loại bỏ token/API key/credential nếu còn sót trong code hoặc notebook.
- Thêm `.env.example` để mô tả biến môi trường.
- Tách bớt checkpoint/dataset lớn sang storage ngoài (Drive/HF/S3) để repo gọn hơn.
- Bổ sung sơ đồ kiến trúc và sample input/output trong README.

---

Nếu bạn là HR/reviewer: chỉ cần xem 3 thư mục `fine-tunning`, `web_deploy/api`, `web_deploy/client` là sẽ nắm được đầy đủ hành trình từ dữ liệu đầu vào đến kết quả đầu ra của hệ thống.
