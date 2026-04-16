import streamlit as st
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from io import BytesIO

st.set_page_config(layout="wide")

# ===== CSS =====
st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
}

.card {
    border: 1px solid #eee;
    padding: 15px;
    border-radius: 12px;
    background: #fafafa;
    margin-bottom: 10px;
}

.stButton > button {
    border-radius: 10px;
    height: 45px;
    font-weight: 600;
}

div[data-testid="stForm"] {
    border: 1px solid #eee;
    padding: 20px;
    border-radius: 12px;
    background: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# ===== TITLE =====
st.markdown("""
# 🚐 HỆ THỐNG QUẢN LÝ VÉ XE  
### Phúc Hải Đà Lạt
""")

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
    xe = st.selectbox("🚌 Số xe", ["--- Không chọn ---"] + all_cars,
                      index=all_cars.index(xe_mac_dinh)+1)

# ================== NGÀY ==================
ngay = st.date_input("📅 Ngày chạy")
ngay_file = ngay.strftime("%d.%m.%Y")
ngay_show = ngay.strftime("%d/%m/%Y")
gio_clean = gio.replace(":", "H")

# ================== FORM ==================
st.divider()

gia_1ve = gia_tuyen[tuyen]

st.markdown(f"""
<div class="card">
💰 <b>Giá vé tuyến {tuyen}</b><br>
<h3>{gia_1ve:,} đ / vé</h3>
</div>
""", unsafe_allow_html=True)

with st.form("form"):
    colA, colB = st.columns(2)

    with colA:
        ten = st.text_area("Họ tên khách / Đơn vị", height=120)
        sdt = st.text_input("Số điện thoại")
        so_ve = st.number_input("Số vé", 1, 50, 1)

    with colB:
        st.text_input("Giá vé", f"{gia_1ve:,} đ", disabled=True)
        thanh_tien = so_ve * gia_1ve
        st.text_input("Thành tiền", f"{thanh_tien:,} đ", disabled=True)

    submit = st.form_submit_button("➕ Thêm vé", use_container_width=True)

# ================== DATA ==================
if "ds" not in st.session_state:
    st.session_state.ds = []

if submit:
    if xe == "--- Không chọn ---":
        st.warning("⚠️ Chọn xe")
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

# ================== DANH SÁCH ==================
st.divider()
st.markdown("### 📋 Danh sách vé")

if st.session_state.ds:

    for i, row in enumerate(st.session_state.ds):
        col1, col2 = st.columns([10,1])

        with col1:
            st.markdown(f"""
            <div class="card">
            👤 <b>{row['ten']}</b><br>
            📞 {row['sdt']} | 🚐 {row['tuyen']} | ⏰ {row['gio']}<br>
            🚌 {row['xe']} | 🎫 {row['so_ve']} vé | 💰 <b>{row['gia']:,} đ</b>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button("❌", key=i):
                st.session_state.ds.pop(i)
                st.rerun()

    if st.button("🗑️ Xóa tất cả"):
        st.session_state.ds = []
        st.rerun()

# ================== XUẤT FILE ==================
def tao_file():
    wb = Workbook()
    ws = wb.active

    center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    right = Alignment(horizontal="right", vertical="center")

    thin = Border(left=Side(style='thin'), right=Side(style='thin'),
                  top=Side(style='thin'), bottom=Side(style='thin'))

    ws.merge_cells("A1:H1")
    ws["A1"] = "CÔNG TY PHÚC HẢI ĐÀ LẠT"
    ws["A1"].alignment = center

    ws.merge_cells("A2:H2")
    ws["A2"] = f"{tuyen} - {gio} - {ngay_show}"
    ws["A2"].alignment = center

    headers = ["Tên","SĐT","Giờ","Tuyến","Xe","Số vé","","Tiền"]

    for col,h in enumerate(headers,1):
        c = ws.cell(row=4,column=col,value=h)
        c.alignment = center
        c.border = thin

    for i,row in enumerate(st.session_state.ds,start=5):
        ws.cell(i,1,row["ten"])
        ws.cell(i,2,row["sdt"])
        ws.cell(i,3,row["gio"])
        ws.cell(i,4,row["tuyen"])
        ws.cell(i,5,row["xe"])
        ws.cell(i,6,row["so_ve"])
        ws.cell(i,8,row["gia"])

        for col in range(1,9):
            c = ws.cell(i,col)
            c.border = thin
            if col == 1:
                c.alignment = left
            elif col == 8:
                c.alignment = right
            else:
                c.alignment = center

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

# ================== DOWNLOAD ==================
if st.session_state.ds:
    st.download_button(
        "📥 Xuất Excel",
        data=tao_file(),
        file_name=f"{tuyen}_{gio_clean}_{ngay_file}.xlsx",
        use_container_width=True
    )
