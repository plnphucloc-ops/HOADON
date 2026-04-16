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

    # ===== STYLE =====
    font_title = Font(name="Times New Roman", size=16, bold=True)
    font_header = Font(name="Times New Roman", size=12, bold=True)
    font_normal = Font(name="Times New Roman", size=12)

    center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    right = Alignment(horizontal="right", vertical="center")

    thin = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    fill_header = PatternFill(start_color="EEEEEE", fill_type="solid")

    # ===== TITLE =====
    ws.merge_cells("A1:H1")
    ws["A1"] = "CÔNG TY PHÚC HẢI ĐÀ LẠT"
    ws["A1"].font = font_title
    ws["A1"].alignment = center

    ws.merge_cells("A2:H2")
    ws["A2"] = f"TUYẾN {tuyen} | GIỜ {gio} | XE {xe} | NGÀY {ngay_show}"
    ws["A2"].font = font_normal
    ws["A2"].alignment = center

    # ===== HEADER =====
    headers = [
        "Họ tên khách",
        "SĐT",
        "Giờ",
        "Tuyến",
        "Xe",
        "Số vé",
        "",
        "Thành tiền"
    ]

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=h)
        cell.font = font_header
        cell.alignment = center
        cell.fill = fill_header
        cell.border = thin

    ws.row_dimensions[4].height = 30

    # ===== WIDTH =====
    widths = [40, 18, 12, 12, 15, 10, 5, 18]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[chr(64+i)].width = w

    # ===== DATA =====
    start = 5

    for i, row in enumerate(st.session_state.ds, start=start):

        ws.cell(i,1,row["ten"])
        ws.cell(i,2,row["sdt"])
        ws.cell(i,3,row["gio"])
        ws.cell(i,4,row["tuyen"])
        ws.cell(i,5,row["xe"])
        ws.cell(i,6,row["so_ve"])

        money = ws.cell(i,8,row["gia"])
        money.number_format = '#,##0 "đ"'

        for col in range(1,9):
            c = ws.cell(i,col)
            c.font = font_normal
            c.border = thin

            if col == 1:
                c.alignment = left
            elif col == 8:
                c.alignment = right
            else:
                c.alignment = center

        # ===== AUTO HEIGHT =====
        lines = str(row["ten"]).count("\n") + 1
        ws.row_dimensions[i].height = max(28, lines * 18)

    # ===== TỔNG =====
    last = len(st.session_state.ds) + start

    ws.cell(last,6,"Tổng").font = font_header
    ws.cell(last,6).alignment = center

    total = ws.cell(last,8,sum([x["gia"] for x in st.session_state.ds]))
    total.number_format = '#,##0 "đ"'
    total.font = font_header

    for col in range(1,9):
        ws.cell(last,col).border = thin

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
