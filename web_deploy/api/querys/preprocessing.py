import uuid
from datetime import datetime

columns = [
    # "LoaiChuTheID", done
    # "LoaiChuTheName", done
    # "BenGiaoTempId", done
    # "HoSoTempId", done
    "HoTen",
    "CCCD",
    "TenToChuc",
    "MaSoThue",
    "SoHoChieu",
    "TheCuTru",
    "QuocGia",
    "QuocGiaCap",
    "Tinh",
    "DiaChi",
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
        cache = {
            "LoaiChuTheID": item["LoaiChuTheID"],
            "LoaiChuTheName": loai_chu_the[int(item["LoaiChuTheID"])],
            "BenGiaoTempId": uuid.uuid4(),
            "HoSoTempId": ho_so_id,
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
            "DiaChi": str(item.get("DiaChi", None))
            .replace(f"{item.get('QuocGia', None)}", "")
            .replace(f"{item.get('Tinh', None)},", "")
            .strip(),
            "HoSoTempId": ho_so_id,
        }
        list_ben_nhan.append(cache)

    return list_ben_nhan


def preprocessing_ho_so(ho_so: dict, ho_so_id: str) -> dict:
    """
    Preprocess the 'HoSo' data to extract necessary fields.
    :param ho_so: Dictionary containing 'HoSo' data.
    :param ho_so_id: Unique identifier for the 'HoSo'.
    :return: Dictionary with preprocessed data.
    """
    return {
        "MaHoSo": ho_so.get("MaHoSo", None),
        "SoDon": ho_so.get("SoDon", None),
        "SoDangKyLanDau": ho_so.get("SoDangKyLanDau", None),
        "LoaiDonID": ho_so.get("LoaiDonID", None),
        "LoaiDonName": ho_so.get("LoaiDonName", None),
        "LoaiDonCode": ho_so.get("LoaiDonCode", None),
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
        # "NoiDungThayDoi": ho_so.get("NoiDungThayDoi", None),
        # "MoTaChungTaiSan": ho_so.get("MoTaChungTaiSan", None),
        "isCheck": False,
        "HoSoTempId": ho_so_id,
        # WARNING: Not clarified fields
        "NgayTao": datetime.now(),
        "NgayUpdate": datetime.now(),
    }
