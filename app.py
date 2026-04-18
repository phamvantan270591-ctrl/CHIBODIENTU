import streamlit as st
import pandas as pd
import requests
import io
import time

# ==========================================
# 1. CẤU HÌNH & CSS (TẠO KHỐI GIỐNG HÌNH ĐỒNG CHÍ GỬI)
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM" 
URL_HOSO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=HoSo"
URL_VANBAN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=VanBan"

# Bắt buộc đặt bố cục 'centered' để các khối nút nằm giữa màn hình điện thoại
st.set_page_config(page_title="CHI BỘ ẤP 4 - QUẢN TRỊ", layout="centered")

st.markdown("""
    <style>
    /* Nền ứng dụng sạch sẽ */
    .stApp { background-color: #fdfdfd; }

    /* CSS CHO KHỐI ĐĂNG NHẬP (GỌN MẢNH) */
    .login-header-mini {
        background-color: #cc0000; padding: 15px;
        border-radius: 10px 10px 0px 0px; text-align: center;
        border-bottom: 2px solid #ffcc00; max-width: 400px; margin: 0 auto;
    }
    .login-header-mini h2 { color: #ffcc00; font-weight: 700; font-size: 1.1rem; margin: 0; text-transform: uppercase; }
    .login-box-mini {
        background: white; padding: 25px; max-width: 400px; margin: 0 auto;
        border-radius: 0px 0px 10px 10px; border: 1px solid #e0e6ed; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .login-btn>button { background: #cc0000; color: white; border-radius: 6px; width: 100%; height: 3em; border: none; font-weight:bold;}

    /* CSS CHO MENU CHÍNH (KHỐI TO MÀU ĐỎ/XANH) */
    .red-banner {
        background-color: #c0392b; color: white; padding: 40px 20px;
        border-radius: 20px; text-align: center; font-weight: bold;
        font-size: 28px; text-transform: uppercase; letter-spacing: 1px;
        box-shadow: 0 8px 15px rgba(0,0,0,0.1); margin-bottom: 30px;
    }
    .stButton > button {
        background-color: #448344; color: white; border-radius: 20px;
        border: none; padding: 25px 30px; font-size: 18px; font-weight: 500;
        width: 100%; display: flex; align-items: center; justify-content: flex-start;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); transition: 0.3s; margin-bottom: 20px;
    }
    .stButton > button:hover { background-color: #366a36; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.15); }
    .stButton > button div p { color: white !important; font-size: 18px !important; }

    /* CSS CHO KHỐI CHI TIẾT ĐẢNG VIÊN */
    .detail-card {
        border: 2px solid #448344; border-radius: 15px; padding: 20px;
        background-color: #f1f8e9; margin-bottom: 25px;
    }
    .back-btn>button { background: #95a5a6; color: white; border-radius: 10px;}
    </style>
    """, unsafe_allow_html=True)

# Hàm tải dữ liệu
def load_data(url):
    try:
        r = requests.get(f"{url}&nocache={time.time()}", timeout=10)
        return pd.read_csv(io.StringIO(r.text)).fillna("")
    except: return pd.DataFrame()

# ==========================================
# 2. LOGIC ĐĂNG NHẬP (GIỮ NGUYÊN)
# ==========================================
if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False
if 'current_view' not in st.session_state: st.session_state.current_view = "MENU" # Quản lý màn hình

if not st.session_state.admin_auth:
    st.markdown('<div style="height: 15vh;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-header-mini"><h2>Hệ thống quản trị chi bộ Ấp 4</h2></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-box-mini">', unsafe_allow_html=True)
    with st.form("login_form"):
        u = st.text_input("Tài khoản:", value="Admin")
        p = st.text_input("Mật khẩu:", type="password")
        st.markdown('<div class="login-btn">', unsafe_allow_html=True)
        btn = st.form_submit_button("XÁC NHẬN TRUY CẬP")
        st.markdown('</div>', unsafe_allow_html=True)
        if btn:
            if u == "Admin" and p == "Tan@753496": st.session_state.admin_auth = True; st.rerun()
            else: st.error("Sai thông tin đăng nhập!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 3. GIAO DIỆN CHÍNH (BIẾN ĐỔI THÀNH CÁC KHỐI TO)
# ==========================================

# MÀN HÌNH MENU CHÍNH (Y HỆT HÌNH ĐỒNG CHÍ GỬI)
if st.session_state.current_view == "MENU":
    st.markdown('<div class="red-banner">MENU CHÍNH -<br>QUẢN TRỊ ĐẢNG VỤ</div>', unsafe_allow_html=True)
    
    # Tạo các nút bấm to
    btn1 = st.button("👤 HỒ SƠ ĐẢNG VIÊN")
    btn2 = st.button("📤 LƯU VĂN BẢN MỚI")
    btn3 = st.button("🖼️ KHO ẢNH VĂN BẢN")
    st.markdown("---")
    if st.button("🚪 Đăng xuất", key="logout"): st.session_state.admin_auth = False; st.rerun()

    # Xử lý chuyển màn hình
    if btn1: st.session_state.current_view = "HOSO"; st.rerun()
    elif btn2: st.session_state.current_view = "UPVB"; st.rerun()
    elif btn3: st.session_state.current_view = "KHOVB"; st.rerun()

# MÀN HÌNH 1: HỒ SƠ ĐẢNG VIÊN (KẾT HỢP XEM CHI TIẾT)
elif st.session_state.current_view == "HOSO":
    # Nút quay lại mảnh mai hơn
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ Quay lại Menu"): st.session_state.current_view = "MENU"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🗂 DANH SÁCH ĐẢNG VIÊN ẤP 4")
    
    df_hs = load_data(URL_HOSO)
    if not df_hs.empty:
        # Bảng gọn chỉ STT và Tên
        df_display = df_hs.iloc[:, [0, 1]]
        df_display.columns = ["STT", "HỌ VÀ TÊN"]
        
        # Cho phép bấm chọn dòng
        selected = st.dataframe(df_display, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

        # Hiện chi tiết trong khối màu xanh
        if len(selected.selection.rows) > 0:
            idx = selected.selection.rows[0]
            row = df_hs.iloc[idx]
            st.markdown('<div class="detail-card">', unsafe_allow_html=True)
            st.subheader(f"🔍 Chi tiết: {row.iloc[1]}")
            c1, c2 = st.columns(2)
            c1.write(f"**Số thứ tự:** {row.iloc[0]}"); c1.write(f"**Ngày sinh:** {row.iloc[2]}")
            c2.write(f"**Chức vụ:** {row.iloc[3]}"); c2.write(f"**Ghi chú:** {row.iloc[4]}")
            st.markdown('</div>', unsafe_allow_html=True)
    else: st.warning("Chưa có dữ liệu.")

# MÀN HÌNH 2: TẢI VĂN BẢN
elif st.session_state.current_view == "UPVB":
    if st.button("⬅️ Quay lại"): st.session_state.current_view = "MENU"; st.rerun()
    st.markdown("### 📤 TẢI LÊN VĂN BẢN MỚI")
    st.file_uploader("Chọn ảnh văn bản/báo cáo:", type=['jpg','png','pdf'])
    st.button("XÁC NHẬN LƯU", key="btn_save")

# MÀN HÌNH 3: KHO VĂN BẢN
elif st.session_state.current_view == "KHOVB":
    if st.button("⬅️ Quay lại"): st.session_state.current_view = "MENU"; st.rerun()
    st.markdown("### 🖼️ KHO ẢNH VĂN BẢN ĐÃ LƯU")
    # Tạm thời chưa có dữ liệu thật
    st.write("Kho ảnh sẽ hiển thị tại đây.")
