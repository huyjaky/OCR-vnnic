import uuid
from datetime import datetime

columns = [
    # "LoaiChuTheID", done
    # "LoaiChuTheName", done
    # "BenGiaoTempId", done
    # "HoSoTempId", done
    # "QuocGia", done "Tinh", done "DiaChi", done
    "HoTen",
    "CCCD",
    "TenToChuc",
    "MaSoThue",
    "SoHoChieu",
    "TheCuTru",
    "QuocGiaCap",
]

loai_chu_the = {
    1: "Công dân Việt Nam",
    2: "Tổ chức có đăng ký kinh doanh trong nước",
    3: "Người nước ngoài",
    4: "Nhà đầu tư nước ngoài",
    5: "Tổ chức khác",
    6: "Người không quốc tịch cư trú tại Việt Nam",
}


def preprocessing_ben_giao(ben_giao: list[dict], ho_so_id: str) -> list[dict]:
    """
    Preprocess the 'BenGiao' data to extract necessary fields.
    :param ben_giao: List of dictionaries containing 'BenGiao' data.
    :param columns: List of column names to extract from 'ThongTinChuThe'.
    :param ho_so_id: Unique identifier for the 'HoSo'.
    :return: List of dictionaries with preprocessed data.
    """
    list_ben_giao = []
    for item in ben_giao:
        try:
            quoc_gia = str(item["ThongTinChuThe"]["DiaChi"]).split(",")[-1].strip()
        except IndexError:
            quoc_gia = "Không xác định"

        try:
            tinh = str(item["ThongTinChuThe"]["DiaChi"]).split(",")[-2].strip()
        except IndexError:
            tinh = "Không xác định"
        cache = {
            "LoaiChuTheID": item["LoaiChuTheID"],
            "LoaiChuTheName": loai_chu_the[int(item["LoaiChuTheID"])],
            "BenGiaoTempId": uuid.uuid4(),
            "HoSoTempId": ho_so_id,
            "QuocGia": quoc_gia,
            "Tinh": tinh,
            "DiaChi": str(item["ThongTinChuThe"]["DiaChi"]),
            # WARNING: Not clarified fields
            "isCheck": False,
            "NgayTao": datetime.now(),
            "NgayUpdate": datetime.now(),
        }
        for key in columns:  # Skip the first column which is 'LoaiChuTheID'
            if key in list(item["ThongTinChuThe"].keys()):
                cache[key] = item["ThongTinChuThe"][key]
            else:
                cache[key] = None
        list_ben_giao.append(cache)

    return list_ben_giao


def preprocessing_ben_nhan(ben_nhan: list[dict], ho_so_id: str) -> list[dict]:
    """
    Preprocess the 'BenNhan' data to extract necessary fields.
    :param ben_nhan: List of dictionaries containing 'BenNhan' data.
    :param ho_so_id: Unique identifier for the 'HoSo'.
    :return: List of dictionaries with preprocessed data.
    """
    list_ben_nhan = []
    for item in ben_nhan:
        cache = {
            "BenNhanTempId": uuid.uuid4(),
            "Ten": item["Ten"],
            "QuocGia": item.get("QuocGia", None),
            "Tinh": item.get("Tinh", None),
            "DiaChi": str(item.get("DiaChi")),
            "HoSoTempId": ho_so_id,
            # WARNING: Not clarified fields
            "isCheck": False,
            "NgayTao": datetime.now(),
            "NgayUpdate": datetime.now(),
        }
        list_ben_nhan.append(cache)

    return list_ben_nhan


loai_don_dict = {
    1: "Đăng ký lần đầu (LĐ)",
    2: "Đăng ký thay đổi (TĐ)",
    3: "Sửa chữa sai sót (SC)",
    4: "Xoá đơn đăng ký (XOA)",
    5: "Xóa đăng ký bởi cơ quan có thẩm quyền (XCQ)",
    6: "Cung cấp bản sao (BS)",
    7: "Yêu cầu cấp bản sao kèm thông báo (TBCA)",
    8: "Cung cấp thông tin (CCTT)",
    9: "Thông báo xử lý tài sản (XLTS)",
}

loai_don_code = {
    1: "LĐ",
    2: "TĐ",
    3: "SC",
    4: "XOA",
    5: "XCQ",
    6: "BS",
    7: "TBCA",
    8: "CCTT",
    9: "XLTS",
}


def preprocessing_ho_so(ho_so: dict, ho_so_id, file_name: str) -> dict:
    """
    Preprocess the 'HoSo' data to extract necessary fields.
    :param ho_so: Dictionary containing 'HoSo' data.
    :param ho_so_id: Unique identifier for the 'HoSo'.
    :return: Dictionary with preprocessed data.
    """
    if ho_so.get("LoaiDonID") != None:
        LoaiDonID = int(list(str(ho_so.get("SoDon", None)))[0])  # pyright:ignore
        if "TBD" in file_name:
            LoaiDonID = 9
        elif "CCTT8" in file_name:
            LoaiDonID = 8

        LoaiDonName = loai_don_dict[LoaiDonID]
        LoaiDonCode = loai_don_code[LoaiDonID]  # CCTT
    else:
        LoaiDonID = None
        LoaiDonName = None
        LoaiDonCode = None

    if ho_so.get("SoDangKyLanDau", None) != None:
        so_dang_ky_lan_dau = str(ho_so.get("SoDangKyLanDau", None)).replace("/HDTC", "")
    else:
        so_dang_ky_lan_dau = None

    return {
        "MaHoSo": ho_so.get("MaHoSo", None),
        "SoDon": ho_so.get("SoDon", None),
        "SoDangKyLanDau": so_dang_ky_lan_dau,
        "LoaiDonID": LoaiDonID,
        "LoaiDonName": LoaiDonName,
        "LoaiDonCode": LoaiDonCode,
        "TenCongAn": ho_so.get("TenCongAn", None),
        "DiaChiCongAn": ho_so.get("DiaChi", None),
        "LoaiHinhGDID": ho_so.get("LoaiHinhGDID", None),
        "LoaiHinhGDName": ho_so.get("LoaiHinhGDName", None),
        "LoaiBienPhapID": ho_so.get("LoaiBienPhapID", None),
        "LoaiBienPhapName": ho_so.get("LoaiBienPhapName", None),
        "LoaiHopDongID": ho_so.get("LoaiHopDongID", None),
        "LoaiHopDongName": ho_so.get("LoaiHopDongName", None),
        "ThoiDiemDangKy": ho_so.get("ThoiDiemDangKy", None),
        "SoHopDong": ho_so.get("SoHopDong", None),
        "NgayCoHieuLucHopDong": ho_so.get("NgayCoHieuLucHopDong", None),
        "GiaTriKhoanVay": ho_so.get("GiaTriKhoanVay", None),
        "SoPhuLuc": ho_so.get("SoPhuLuc", None),
        "ThoiDiemKHDangKy": ho_so.get("ThoiDiemKHDangKy", None),
        "ThoiDiemDKLanDau": ho_so.get("ThoiDiemDKLanDau", None),
        "TenFile": file_name + ".pdf",
        "HoSoTempId": ho_so_id,
        # WARNING: Not clarified fields
        "isCheck": False,
        "NgayTao": datetime.now(),
        "NgayUpdate": datetime.now(),
    }
