import streamlit as st
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from io import BytesIO

st.set_page_config(layout="wide")
st.title("🚐 PHẦN MỀM TẠO FILE HÓA ĐƠN ĐIỆN TỬ")

# ================== DATA ==================
routes = {
    "DL-GL": {"07:00": "49H-046.85", "10:00": "49G-000.71", "17:00": "49B-019.00"},
    "GL-DL": {"07:00": "49H-046.85", "13:00": "49G-000.71", "17:00": "49B-019.00"},
    "BMT-DL": {"07:00": "49B-013.18"},
    "DL-BMT": {"13:00": "49B-013.18"}
}

gia_tuyen = {
    "DL-GL": 420000,
    "GL-DL": 420000,
    "BMT-DL": 300000,
    "DL-BMT": 300000
}

all_cars = [
    "49B-016.93","49B-017.39","49B-019.00",
    "49G-000.71","49B-013.18","49H-046.85"
]

# ================== CHỌN ==================
col1, col2, col3 = st.columns(3)

with col1:
    tuyen = st.selectbox("🚐 Tuyến", list(routes.keys()))

with col2:
    gio = st.selectbox("⏰ Giờ", list(routes[tuyen].keys()))

with col3:
    xe_mac_dinh = routes[tuyen][gio]
    options = ["--- Không chọn ---"] + all_cars
    xe = st.selectbox("🚌 Xe", options, index=options.index(xe_mac_dinh))

ngay = st.date_input("📅 Ngày")
ngay_show = ngay.strftime("%d/%m/%Y")
ngay_file = ngay.strftime("%d.%m.%Y")
gio_clean = gio.replace(":", "H")

# ================== FORM ==================
st.divider()
gia_1ve = gia_tuyen[tuyen]
st.info(f"💰 Giá: {gia_1ve:,} đ")

with st.form("form"):
    ten = st.text_area("Họ tên khách", height=120)
    sdt = st.text_input("SĐT")
    so_ve = st.number_input("Số vé", 1, 100, 1)

    thanh_tien = so_ve * gia_1ve
    st.text_input("Thành tiền", f"{thanh_tien:,} đ", disabled=True)

    submit = st.form_submit_button("➕ Thêm")

# ================== DATA ==================
if "ds" not in st.session_state:
    st.session_state.ds = []

if submit:
    if xe == "--- Không chọn ---":
        st.warning("Chọn xe")
    else:
        st.session_state.ds.append({
            "ten": ten,
            "sdt": sdt,
            "gio": gio,
            "tuyen": tuyen,
            "xe": xe,
            "so_ve": so_ve,
            "gia": thanh_tien
        })

# ================== HIỂN THỊ ==================
st.divider()
if st.session_state.ds:

    for i, row in enumerate(st.session_state.ds):
        c1, c2 = st.columns([10,1])
        with c1:
            st.write(f"{row['ten']} | {row['sdt']} | {row['so_ve']} vé | {row['gia']:,} đ")
        with c2:
            if st.button("❌", key=i):
                st.session_state.ds.pop(i)
                st.rerun()

    if st.button("🗑️ Xóa tất cả"):
        st.session_state.ds = []
        st.rerun()

# ================== XUẤT EXCEL ==================
def tao_file():
    wb = Workbook()
    ws = wb.active

    font = Font(name="Times New Roman", size=12)
    center = Alignment(horizontal="center", vertical="center")
    left = Alignment(horizontal="left", vertical="top", wrap_text=True)
    right = Alignment(horizontal="right")

    thin = Border(left=Side(style='thin'), right=Side(style='thin'),
                  top=Side(style='thin'), bottom=Side(style='thin'))

    ws.merge_cells("A1:H1")
    ws["A1"] = "CÔNG TY PHÚC HẢI ĐÀ LẠT"
    ws["A1"].alignment = center

    ws.merge_cells("A2:H2")
    ws["A2"] = f"{tuyen} - {gio} - {ngay_show}"
    ws["A2"].alignment = center

    headers = ["Tên", "SĐT", "Giờ", "Tuyến", "Xe", "Số vé", "", "Tiền"]

    for col, h in enumerate(headers,1):
        c = ws.cell(row=4, column=col, value=h)
        c.alignment = center
        c.border = thin

    for i, row in enumerate(st.session_state.ds, start=5):
        ws.cell(i,1,row["ten"])
        ws.cell(i,2,row["sdt"])
        ws.cell(i,3,row["gio"])
        ws.cell(i,4,row["tuyen"])
        ws.cell(i,5,row["xe"])
        ws.cell(i,6,row["so_ve"])
        ws.cell(i,8,row["gia"])

        for col in range(1,9):
            cell = ws.cell(i,col)
            cell.border = thin
            cell.font = font
            if col == 1:
                cell.alignment = left
            elif col == 8:
                cell.alignment = right
            else:
                cell.alignment = center

        # auto cao dòng
        lines = str(row["ten"]).count("\n") + 1
        ws.row_dimensions[i].height = max(20, lines*15)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

# ================== DOWNLOAD ==================
if st.session_state.ds:
    st.download_button(
        "📥 Xuất Excel",
        data=tao_file(),
        file_name=f"{tuyen}_{gio_clean}_{ngay_file}.xlsx"
    )
