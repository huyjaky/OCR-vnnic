import uuid
from datetime import datetime

columns = [
    # "LoaiChuTheID", done
    # "LoaiChuTheName", done
    # "BenGiaoTempId", done
    # "HoSoTempId", done
    # "QuocGia", done
    # "Tinh", done
    # "DiaChi", done
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
        quoc_gia = str(item["ThongTinChuThe"]["DiaChi"]).split(",")[-1].strip()
        tinh = str(item["ThongTinChuThe"]["DiaChi"]).split(",")[-2].strip()

        print(quoc_gia, tinh)

        cache = {
            "LoaiChuTheID": item["LoaiChuTheID"],
            "LoaiChuTheName": loai_chu_the[int(item["LoaiChuTheID"])],
            "BenGiaoTempId": uuid.uuid4(),
            "HoSoTempId": ho_so_id,
            "QuocGia": quoc_gia,
            "Tinh": tinh,
            "DiaChi": str(item["ThongTinChuThe"]["DiaChi"])
            .replace(f"{quoc_gia}", "")
            .replace(f"{tinh},", "")
            .replace("tỉnh", "")
            .replace("thành phố", "")
            .replace("quốc gia", "")
            .strip(),
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
            "DiaChi": str(item.get("DiaChi"))
            .replace(f"{item.get('QuocGia')}", "")
            .replace(f"{item.get('Tinh')},", "")
            .replace("tỉnh", "")
            .replace("thành phố", "")
            .replace("quốc gia", "")
            .strip(),
            "HoSoTempId": ho_so_id,
        }
        list_ben_nhan.append(cache)

    return list_ben_nhan


loai_don_dict = {
    1: "Đăng ký lần đầu (LĐ)",
    2: "Đăng ký thay đổi (TĐ)",
    3: "Sửa chữa sai sót (SC)",
    4: "Xoá đơn đăng ký (XOA)",
    6: "Xoá đăng ký bởi cơ quan có thẩm quyền (XCQ)",
    8: "Cung cấp bản sao (BS)",
    9: "Yêu cầu cấp bản sao kèm thông báo CA (TBCA)",
    10: "Cung cấp thông tin (CCTT)",
}

loai_don_code = {
    1: "LD",
    2: "TD",
    3: "SC",
    4: "XOA",
    6: "XCQ",
    8: "BS",
    9: "TBCA",
    10: "CCTT",
}


def preprocessing_ho_so(ho_so: dict, ho_so_id, file_name: str) -> dict:
    """
    Preprocess the 'HoSo' data to extract necessary fields.
    :param ho_so: Dictionary containing 'HoSo' data.
    :param ho_so_id: Unique identifier for the 'HoSo'.
    :return: Dictionary with preprocessed data.
    """
    if ho_so.get("LoaiDonID") != None:
        LoaiDonID = int(ho_so.get("LoaiDonID"))  # pyright:ignore

        if "/TB-TT3" in str(ho_so.get("MaHoSo", None)):
            LoaiDonID = 9  # CCTT
        elif "CCTT" in str(ho_so.get("SoDon", None)) or "CCTT" in file_name:
            LoaiDonID = 10
        else:
            LoaiDonID = int(list(str(ho_so.get("SoDon", None)))[0])

        LoaiDonName = loai_don_dict[LoaiDonID]
        LoaiDonCode = loai_don_code[LoaiDonID]  # CCTT
    else:
        LoaiDonID = None
        LoaiDonName = None
        LoaiDonCode = None

    return {
        "MaHoSo": ho_so.get("MaHoSo", None),
        "SoDon": ho_so.get("SoDon", None),
        "SoDangKyLanDau": ho_so.get("SoDangKyLanDau", None),
        "LoaiDonID": LoaiDonID,
        "LoaiDonName": LoaiDonName,
        "LoaiDonCode": LoaiDonCode,
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
        "TenFile": file_name,
        "isCheck": False,
        "HoSoTempId": ho_so_id,
        # WARNING: Not clarified fields
        "NgayTao": datetime.now(),
        "NgayUpdate": datetime.now(),
    }
