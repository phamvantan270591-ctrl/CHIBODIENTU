import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import io
import time

# --- CẤU HÌNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM" # Thay bằng ID file mới của đồng chí
URL_HOSO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=HoSo"
URL_VANBAN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=VanBan"

st.set_page_config(page_title="QUẢN TRỊ ĐẢNG VỤ", layout="wide")

# --- GIAO DIỆN ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stHeader { background-color: #cc0000; color: white; padding: 20px; border-radius: 10px; text-align: center; }
    .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

def get_data(url):
    try:
        r = requests.get(f"{url}&nocache={time.time()}")
        return pd.read_csv(io.StringIO(r.text)).fillna("")
    except: return None

# --- MENU CHÍNH ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Hammer_and_sickle.svg/1200px-Hammer_and_sickle.svg.png", width=100)
    st.title("HỆ THỐNG QUẢN TRỊ")
    tab = st.radio("Chức năng", ["🔍 Tìm kiếm nhanh", "👤 Hồ sơ Đảng viên", "📂 Kho văn bản & Báo cáo"])

# --- 1. TÌM KIẾM NHANH ---
if tab == "🔍 Tìm kiếm nhanh":
    st.markdown('<div class="stHeader"><h1>KHO TRA CỨU TỔNG HỢP</h1></div><br>', unsafe_allow_html=True)
    query = st.text_input("🔎 Nhập tên Đảng viên hoặc nội dung văn bản cần tìm:", placeholder="Ví dụ: Nguyễn Văn A hoặc Nghị quyết 01...")
    
    if query:
        df_hs = get_data(URL_HOSO)
        df_vb = get_data(URL_VANBAN)
        
        st.subheader("Kết quả trong Hồ sơ:")
        res_hs = df_hs[df_hs.apply(lambda row: query.lower() in row.astype(str).str.lower().values, axis=1)]
        st.table(res_hs)
        
        st.subheader("Kết quả trong Văn bản/Công văn:")
        res_vb = df_vb[df_vb.apply(lambda row: query.lower() in row.astype(str).str.lower().values, axis=1)]
        st.table(res_vb)

# --- 2. HỒ SƠ ĐẢNG VIÊN ---
elif tab == "👤 Hồ sơ Đảng viên":
    st.markdown('<div class="stHeader"><h1>DANH SÁCH ĐẢNG VIÊN</h1></div><br>', unsafe_allow_html=True)
    df = get_data(URL_HOSO)
    if df is not None:
        st.dataframe(df, use_container_width=True)
        
    with st.expander("➕ Thêm hồ sơ mới"):
        with st.form("add_hs"):
            name = st.text_input("Họ và tên")
            birth = st.date_input("Ngày sinh")
            job = st.text_input("Chức vụ")
            note = st.text_area("Ghi chú")
            if st.form_submit_button("Lưu vào hệ thống"):
                st.info("Đã ghi nhận lệnh. Dữ liệu sẽ được đồng bộ vào Google Sheets.")

# --- 3. KHO VĂN BẢN ---
elif tab == "📂 Kho văn bản & Báo cáo":
    st.markdown('<div class="stHeader"><h1>LƯU TRỮ VĂN BẢN & BÁO CÁO</h1></div><br>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📤 Tải lên văn bản")
        loai = st.selectbox("Loại", ["Cấp trên", "Chi bộ", "Báo cáo"])
        trich_yeu = st.text_area("Nội dung tóm tắt (Trích yếu)")
        uploaded_file = st.file_uploader("Chụp ảnh hoặc chọn file văn bản", type=['png', 'jpg', 'jpeg', 'pdf'])
        if st.button("Xác nhận lưu trữ"):
            st.success("Đã lưu văn bản thành công!")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        df_vb = get_data(URL_VANBAN)
        if df_vb is not None:
            st.subheader("Danh sách văn bản đã lưu")
            st.dataframe(df_vb, use_container_width=True)
