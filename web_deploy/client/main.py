from table import (
    render_vertical_table,
    render_horizontal_table,
    title,
    title_small,
    format_time,
    group_by_type,
)
import pandas as pd



load_json = pd.read_json("../Phúc/2_41_done/2080000207.json")
form_schema = load_json["output"][0]

lable_map_bengiao = {
    "1": "Công dân Việt Nam",
    "2": "Tổ chức có đăng ký kinh doanh trong nước",
    "3": "Người nước ngoài",
    "4": "Nhà đầu tư nước ngoài",
    "5": "Tổ chức khác",
    "6": "Người không quốc tịch cư trú tại Việt Nam",
}


lable_map_taisan = {
    "TaiSan_CoSoKhung": "Tài sản có số khung",
    "TaiSan_KhongCoSoKhung": "Tài sản không có số khung",
    "TaiSan_QuyenTaiSan": "Quyền tài sản",
    "TaiSan_HangHoaLuanChuyen": "Hàng hóa luân chuyển",
}

label_map_value = {
    # TaiSan_CoSoKhung
    "PhuongTien": "Phương tiện",
    "NhanHieuMauSon": "Nhãn hiệu màu sơn",
    "SoKhung": "Số khung",
    "SoMay": "Số máy",
    "BienSo": "Biển số",
    # TaiSan_KhongCoSoKhung
    "TenPhuongTienNhanHieu": "Tên phương tiện, nhãn hiệu",
    "TenChuPhuongTien": "Tên chủ phương tiện",
    "SoDangKyCoQuanCC": "Sô đăng ký cơ quan cc",
    "CapPhuongTien": "Cấp phương tiện",
    # TaiSan_QuyenTaiSan
    "TenQuyen": "Tên quyền",
    "CanCuPhatSinhQuyen": "Căn cứ phát sinh quyền",
    # TaiSan_HangHoaLuanChuyen
    "LoaiKhoHang": "Loại kho hàng",
    "GiaTri_TenLoai_HangHoa": "Giá trị, tên loại hàng hóa",
    "DiaChiKhoHang": "Địa chỉ kho hàng",
    "SoHieuKhoHang": "Số hiệu kho hàng",
    # CongDanVietNam
    "HoTen": "Họ tên",
    "CCCD": "Căng cước công dân",
    "DiaChi": "Địa chỉ",
    # ToChucTrongNuoc
    "TenToChuc": "Tên tổ chức",
    "MaSoThue": "Mã số thuế",
    # NguoiNuocNgoai
    "SoHoChieu": "Số hộ chiếu",
    "QuocGiaCap": "Quốc gia lập",
    "QuocGia": "Quốc gia",
    "Tinh": "Tỉnh",
    # NhaDauTuNuocNgoai
    "MaSoThue": "Mã số thuế",
    "Ten": "Tên",
    # ToChucKhac
    # NguoiKhongQuocTich
    "TheCuTru": "Thẻ cư trú",
}

title("Thông tin trích xuất")

render_horizontal_table(
    ["Mã hồ sơ", "Số đăng ký", "Thời điểm đăng ký"],
    [
        [
            form_schema["MaHoSo"],
            form_schema["SoDon"],
            format_time(form_schema["ThoiDiemDangKy"]),
        ]
    ],
)



render_horizontal_table(
    ["Số đăng ký lần đầu", "Thời điểm đăng ký lần đầu"],
    [
        [
            form_schema["SoDangKyLanDau"],
            format_time(form_schema["ThoiDiemDKLanDau"]),
        ]
    ],
)

render_vertical_table(
    [
        ["Loại đơn", form_schema["LoaiDonName"]],
        ["Loại hình giao dịch", form_schema["LoaiHinhGDName"]],
        ["Loại biện pháp", form_schema["LoaBienPhapName"]],
        ["Loại hợp đồng", form_schema["LoaHopDongName"]],
    ],
)


render_horizontal_table(
    ["Số hợp đồng", "Số phụ lục hợp đồng", "Ngày hiệu lực"],
    [
        [
            form_schema["SoHopDong"],
            form_schema["SoPhuLuc"],
            form_schema["NgayCoHieuLucHopDong"],
        ]
    ],
)

render_horizontal_table(
    ["Nội dung thay đổi đăng ký"], [[form_schema["NoiDungThayDoi"]]]
)

render_horizontal_table(["Mô tả chung về tài sản"], [[form_schema["MoTaChungTaiSan"]]])


title("Bên giao")

bengiao = group_by_type(form_schema["BenGiao"], "LoaiChuTheID")
for loai_id in sorted(bengiao.keys()):
    danh_sach = bengiao[loai_id]
    title_small(lable_map_bengiao[f"{loai_id}"])
    for i, obj in enumerate(danh_sach, 1):
        chu_the = obj["ThongTinChuThe"]
        rows = [[k, v] for k, v in chu_the.items()]
        rows = [[label_map_value.get(k, k), v] for k, v in rows]
        render_vertical_table(rows)


title("Bên nhận")
bennhan = form_schema["BenNhan"][0]
render_vertical_table(
    [
        ["Tên", bennhan["Ten"]],
        ["Quốc gia", bennhan["QuocGia"]],
        ["Tỉnh", bennhan["Tinh"]],
        ["Địa chỉ", bennhan["DiaChi"]],
    ],
)

title("Tài sản")

exclude_taisan_keys = ["LoaiTaiSan", "CanCuThayDoi"]
taisan = group_by_type(form_schema["TaiSan"], "LoaiTaiSan")
for loai_id in sorted(taisan.keys()):
    danh_sach = taisan[loai_id]

    title_small(lable_map_taisan[f"{loai_id}"])

    for i, obj in enumerate(danh_sach, 1):
        rows = [[k, v] for k, v in obj.items() if k not in exclude_taisan_keys]
        rows = [
            [
                k,
                (
                    {0: "Hàng hoá luân chuyển", 1: "Kho hàng"}.get(v, v)
                    if k == "LoaiKhoHang"
                    else v
                ),
            ]
            for k, v in rows
        ]
        rows.append(
            [
                "Căn cứ thay đổi",
                (
                    "Thế chấp/Cầm cố"
                    if obj["CanCuThayDoi"] == 1
                    else "Xóa thế chấp/Cầm cố"
                    if obj["CanCuThayDoi"] == 2
                    else ""
                ),
            ]
        )

        rows = [[label_map_value.get(k, k), v] for k, v in rows]
        render_vertical_table(rows)
