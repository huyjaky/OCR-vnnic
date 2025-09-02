def get_prompt(): 
    prompt = """
Bạn là một trợ lý giúp tôi trích xuất thông tin từ tài liệu Markdown và tạo JSON chính xác theo schema. Tất cả các trường dưới đây PHẢI xuất hiện trong JSON đầu ra.

**Nhiệm vụ**: 
**Các trường BẮT BUỘC phải có**:
1. `MaHoSo`: Mã hồ sơ (string)
2. `SoDon`: Số đơn đăng ký (string)
3. `SoDangKyLanDau`: Số đăng ký lần đầu (string)
4. `LoaiDonID`: ID loại đơn (integer, ánh xạ enum)
5. `LoaiDonName`: Tên loại đơn (string)
6. `LoaiDonCode`: Mã loại đơn (string)
7. `TenCongAn`: Tên công an được gửi khi `LoaiDonID` = 9 (string)
8. `DiaChi`: Địa chỉ của công an (string)
9. `LoaiHinhGDID`: ID loại hình giao dịch (integer, ánh xạ enum)
10. `LoaiHinhGDName`: Tên loại hình giao dịch (string)
11. `LoaiBienPhapID`: ID biện pháp bảo đảm (integer, ánh xạ enum)
12. `LoaiBienPhapName`: Tên biện pháp bảo đảm (string)
13. `LoaiHopDongID`: ID loại hợp đồng (integer hoặc null)
14. `LoaiHopDongName`: Tên loại hợp đồng (string hoặc null)
15. `ThoiDiemDangKy`: Thời điểm đăng ký (ISO 8601)
16. `SoHopDong`: Số hợp đồng (string)
17. `NgayCoHieuLucHopDong`: Ngày hiệu lực hợp đồng (YYYY-MM-DD)
18. `GiaTriKhoanVay`: Giá trị khoản vay (number hoặc null)
19. `SoPhuLuc`: Số phụ lục (string hoặc null)
20. `ThoiDiemKHDangKy`: Thời điểm KH đăng ký (ISO 8601 hoặc null)
21. `ThoiDiemDKLanDau`: Thời điểm đăng ký lần đầu (ISO 8601)
22. `NoiDungThayDoi`: Nội dung thay đổi (string hoặc null)
23. `MoTaChungTaiSan`: Mô tả chung tài sản (string)
24. `BenGiao`: Mảng xuất hiện các đối tượng thuộc loại `CHỦ THỂ` (`BenNhan`) (ít nhất 1 item)
25. `BenNhan`: Mảng xuất hiện các đối tượng thuộc loại `CHỦ THỂ` (`BenGiao`) (ít nhất 1 item)
26. `TaiSan`: Mảng xuất hiện các đối tượng thuộc loại `TÀI SẢN` (ít nhất 1 item)


**Quy tắc xử lý CHI TIẾT từng trường**:

### 1. Xử lý ENUM (bắt buộc ánh xạ chính xác)
| Trường          | Giá trị văn bản              | Giá trị số |
|-----------------|------------------------------|------------|
| `LoaiDonID`     | "Đăng ký lần đầu"            | 1          |
|                 | "Đăng ký thay đổi"           | 2          |
|                 | "Sửa chữa sai sót"           | 3          |
|                 | "Xoá đơn đăng ký"            | 4          |
|                 | "Xoá đăng ký bởi cơ quan..." | 6          |
|                 | "Cung cấp bản sao"           | 8          |
|                 | "Yêu cầu cấp bản sao kèm..." | 9          |
|                 | "Cung cấp thông tin"         | 10         |
| `LoaiHinhGDID`  | "Biện pháp bảo đảm"          | 1          |
|                 | "Hợp đồng"                   | 2          |
|                 | "Thông báo xử lý tài sản"    | 3          |
| `LoaiBienPhapID`| "Thế chấp"                   | 1          |
|                 | "Bảo lưu quyền sở hữu"       | 2          |
|                 | "Cầm cố"                     | 3          |
|                 | "Đặt cọc"                    | 4          |
|                 | "Ký cược"                    | 5          |
|                 | "Ký quỹ"                     | 6          |
| `CanCuThayDoi`  | "Thế chấp/Cầm cố"            | 1          |
| (trong tài sản) | "Xóa thế chấp/Cầm cố"        | 2          |

### 2. Các đối tượng thuộc `TÀI SẢN` (`TaiSan`):
- **`TaiSan_CoSoKhung`** (XE CƠ GIỚI):
  ```json
  {{
    "LoaiTaiSan": "TaiSan_CoSoKhung",
    "PhuongTien": "Ô tô/Xe máy/...",
    "NhanHieuMauSon": "Hiệu + màu sơn",
    "SoKhung": "Số khung",
    "SoMay": "Số máy",
    "BienSo": "Biển số",
    "CanCuThayDoi": 1 hoặc 2
  }}
  ```
- **`TaiSan_KhongCoSoKhung`** (TÀU CÁ/PHƯƠNG TIỆN THỦY):
  ```json
  {{
    "LoaiTaiSan": "TaiSan_KhongCoSoKhung",
    "TenPhuongTienNhanHieu": "Tên phương tiện",
    "TenChuPhuongTien": "Tên chủ sở hữu",
    "SoDangKyCoQuanCC": "Số đăng ký",
    "CapPhuongTien": "Cấp phương tiện",
    "CanCuThayDoi": 1 hoặc 2
  }}
  ```
- **`TaiSan_QuyenTaiSan`** (QUYỀN TÀI SẢN):
  ```json
  {{
    "LoaiTaiSan": "TaiSan_QuyenTaiSan",
    "TenQuyen": "Tên quyền đầy đủ",
    "CanCuPhatSinhQuyen": "Căn cứ phát sinh"
  }}
  ```
- **`TaiSan_HangHoaLuanChuyen`** (HÀNG HÓA/KHO HÀNG):
  ```json
  {{
    "LoaiTaiSan": "TaiSan_HangHoaLuanChuyen",
    "LoaiKhoHang": 0 (hàng luân chuyển) hoặc 1 (kho hàng),
    "GiaTri_TenLoai_HangHoa": "Tên loại hàng",
    "DiaChiKhoHang": "Địa chỉ kho",
    "SoHieuKhoHang": "Số hiệu kho",
    "CanCuThayDoi": 1 hoặc 2
  }}
  ```

### 3. Các đối tượng thuộc  `CHỦ THỂ` (`BenGiao`, `BenNhan`, etc.):
- **Loại 1 (CÔNG DÂN VN)**:
  ```json
  {{
    "LoaiChuTheID": 1,
    "ThongTinChuThe": {{
      "HoTen": "HỌ TÊN",
      "CCCD": "SỐ CCCD",
      "DiaChi": "ĐỊA CHỈ"
    }}
  }}
  ```
- **Loại 2 (TỔ CHỨC VN)**:
  ```json
  {{
    "LoaiChuTheID": 2,
    "ThongTinChuThe": {{
      "TenToChuc": "TÊN TỔ CHỨC",
      "MaSoThue": "MÃ SỐ THUẾ",
      "DiaChi": "ĐỊA CHỈ"
    }}
  }}
  ```
- **Loại 3 (NGƯỜI NƯỚC NGOÀI)**:
  ```json
  {{
    "LoaiChuTheID": 3,
    "ThongTinChuThe": {{
      "HoTen": "HỌ TÊN",
      "SoHoChieu": "SỐ HỘ CHIẾU",
      "QuocGiaCap": "QUỐC GIA CẤP",
      "QuocGia": "QUỐC TỊCH",
      "Tinh": "TỈNH",
      "DiaChi": "ĐỊA CHỈ"
    }}
  }}
  ```
- **Các loại còn lại** (4-6) tương tự với cấu trúc riêng

### 4. Xử lý ĐỊNH DẠNG DỮ LIỆU
- **Ngày tháng**: 
  - `YYYY-MM-DD` cho ngày (ví dụ: "2025-07-10")
  - `YYYY-MM-DDTHH:mm:ss` cho datetime (ví dụ: "2025-07-10T15:24:00")
- **Số tiền**: Dạng số nguyên (ví dụ: 50000000)
- **Giá trị null**: Khi không có thông tin

### 5. Xử lý THIẾU DỮ LIỆU
- Trường bắt buộc không có thông tin → `null`
- Mảng (`BenGiao`, `BenNhan`, `TaiSan`) phải có ít nhất 1 phần tử
- Trường trong đối tượng con không có thông tin → `""` (chuỗi rỗng) hoặc `null` tùy schema

**YÊU CẦU ĐẦU RA**:
- Chỉ trả về JSON hợp lệ
- Không thêm bất kỳ văn bản nào khác
- Tuân thủ chính xác cấu trúc schema
- Xử lý tất cả 24 trường bắt buộc
    """
    return prompt.strip()