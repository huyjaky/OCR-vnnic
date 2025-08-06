from datetime import datetime

time_thoidiemdk = "2025-05-05T08:23:00"

# Parse chuỗi thành đối tượng datetime
dt = datetime.fromisoformat(time_thoidiemdk)

# Lấy năm
nam = dt.year
thang = dt.month
ngay = dt.day

print(f"Năm: {nam}, ngay: {ngay}, tháng: {thang}")
