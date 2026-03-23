import streamlit as st
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from io import BytesIO

st.set_page_config(layout="wide")
st.title("🚐 PHẦN MỀM TẠO DANH SÁCH VÉ")

# ================== DATA TUYẾN ==================
routes = {
    "DL-GL": {
        "07:00": "49H-046.85",
        "10:00": "49G-000.71",
        "17:00": "49B-019.00"
    },
    "GL-DL": {
        "07:00": "49H-046.85",
        "13:00": "49G-000.71",
        "17:00": "49B-019.00"
    },
    "BMT-DL": {
        "07:00": "49B-013.18"
    },
    "DL-BMT": {
        "13:00": "49B-013.18"
    }
}

# ================== DANH SÁCH XE CỐ ĐỊNH ==================
all_cars = [
    "49B-016.93",
    "49B-017.39",
    "49B-019.00",
    "49G-000.71",
    "49B-013.18",
    "49H-046.85"
]

# ================== LẤY ALL GIỜ ==================
all_times = sorted(list(set(
    time for route in routes.values() for time in route.keys()
)))

# ================== CHẾ ĐỘ ==================
mode = st.radio("⚙️ Chế độ", ["Chuẩn (auto)", "Linh hoạt (tự chọn)"])

colA, colB, colC = st.columns(3)

# ================== CHUẨN ==================
if mode == "Chuẩn (auto)":
    with colA:
        tuyen = st.selectbox("🚐 Tuyến", list(routes.keys()))

    with colB:
        gio = st.selectbox("⏰ Giờ", list(routes[tuyen].keys()))

    with colC:
        xe_mac_dinh = routes[tuyen][gio]
        options = ["--- Không chọn ---"] + all_cars
        index = options.index(xe_mac_dinh) if xe_mac_dinh in options else 0

        xe = st.selectbox("🚌 Số xe", options, index=index)

# ================== LINH HOẠT ==================
else:
    with colA:
        tuyen = st.selectbox("🚐 Tuyến", list(routes.keys()))

    with colB:
        gio = st.selectbox("⏰ Giờ", all_times)

    with colC:
        xe = st.selectbox("🚌 Số xe", ["--- Không chọn ---"] + all_cars)

# ================== NGÀY ==================
ngay = st.date_input("📅 Ngày chạy")
ngay_file = ngay.strftime("%d.%m.%Y")
ngay_show = ngay.strftime("%d/%m/%Y")
gio_clean = gio.replace(":", "H")

# ================== FORM ==================
st.divider()
st.subheader("🧾 Nhập thông tin vé")

with st.form("form_ve"):
    col1, col2 = st.columns(2)

    with col1:
        ten = st.text_input("Họ tên khách / Đơn vị")
        cccd = st.text_input("CCCD / MST")
        sdt = st.text_input("Số điện thoại")
        so_ve = st.number_input("Số vé", min_value=1, value=1)

    with col2:
        gia_1ve = st.number_input("Giá 1 vé", value=100000)
        thanh_tien = so_ve * gia_1ve
        st.text_input("Thành tiền", value=f"{thanh_tien:,} đ", disabled=True)

    submit = st.form_submit_button("➕ Thêm vé")

# ================== DATA ==================
if "ds_ve" not in st.session_state:
    st.session_state.ds_ve = []

if submit:
    if xe == "--- Không chọn ---":
        st.warning("⚠️ Vui lòng chọn xe trước khi thêm vé")
    else:
        st.session_state.ds_ve.append({
            "ten": ten,
            "cccd": cccd,
            "sdt": sdt,
            "gio": gio,
            "tuyen": tuyen,
            "xe": xe,
            "so_ve": so_ve,
            "gia": thanh_tien
        })

# ================== HIỂN THỊ ==================
st.divider()
st.subheader("📋 Danh sách vé")

if st.session_state.ds_ve:
    df = pd.DataFrame(st.session_state.ds_ve)

    df_show = df.copy()
    df_show.columns = [
        "Họ tên khách/Tên đơn vị",
        "CCCD/MST",
        "Số điện thoại",
        "Giờ xuất bến",
        "Tuyến xe",
        "Số xe",
        "Số vé",
        "Thành tiền"
    ]

    st.dataframe(df_show, use_container_width=True)

    tong_tien = df["gia"].sum()
    st.success(f"💰 Tổng tiền: {tong_tien:,} đ")

# ================== XUẤT FILE ==================
def tao_file():
    wb = Workbook()
    ws = wb.active

    ws.merge_cells("A1:H1")
    ws["A1"] = "CÔNG TY PHÚC HẢI ĐÀ LẠT"
    ws["A1"].font = Font(size=14, bold=True)
    ws["A1"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A2:H2")
    ws["A2"] = f"TUYẾN {tuyen} | GIỜ {gio} | XE {xe} | NGÀY {ngay_show}"
    ws["A2"].alignment = Alignment(horizontal="center")

    headers = [
        "Họ tên khách/Tên đơn vị",
        "CCCD/MST",
        "Số điện thoại",
        "Giờ xuất bến",
        "Tuyến xe",
        "Số xe",
        "Số vé",
        "Thành tiền"
    ]

    fill = PatternFill(start_color="DDDDDD", fill_type="solid")
    thin = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=3, column=col, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")
        cell.fill = fill

    for i, row in enumerate(st.session_state.ds_ve, start=4):
        ws.cell(row=i, column=1, value=row["ten"])
        ws.cell(row=i, column=2, value=row["cccd"])
        ws.cell(row=i, column=3, value=row["sdt"])
        ws.cell(row=i, column=4, value=row["gio"])
        ws.cell(row=i, column=5, value=row["tuyen"])
        ws.cell(row=i, column=6, value=row["xe"])
        ws.cell(row=i, column=7, value=row["so_ve"])

        money = ws.cell(row=i, column=8, value=row["gia"])
        money.number_format = '#,##0 "đ"'

        for c in range(1, 9):
            ws.cell(row=i, column=c).border = thin

    last_row = len(st.session_state.ds_ve) + 4
    ws.cell(row=last_row, column=7, value="Tổng")
    total = ws.cell(row=last_row, column=8, value=sum([x["gia"] for x in st.session_state.ds_ve]))
    total.number_format = '#,##0 "đ"'

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

# ================== DOWNLOAD ==================
if st.session_state.ds_ve:
    file_name = f"TTHD_{tuyen}_{gio_clean}_{xe}_{ngay_file}.xlsx"

    st.download_button(
        "📥 Xuất Excel",
        data=tao_file(),
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
