```python
import streamlit as st
import pandas as pd
import requests
import io
import time

# ==========================================
# CONFIG
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
URL_HOSO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=HoSo"

PASSWORD = "Tan@753496"

st.set_page_config(
    page_title="QUẢN LÝ ĐẢNG VIÊN",
    layout="centered"
)

# ==========================================
# CSS
# ==========================================
st.markdown("""
<style>

.stApp {
    background-color: #f4f7f9;
}

.red-header {
    background-color: #b30000;
    color: #ffcc00;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
}

.stButton > button {
    background-color: #2e7d32;
    color: white;
    border-radius: 15px;
    padding: 18px;
    font-size: 18px;
    font-weight: bold;
    width: 100%;
    border: none;
    margin-bottom: 15px;
}

.content-box {
    background-color: white;
    border-radius: 12px;
    padding: 20px;
    border: 2px solid #2e7d32;
    margin-top: 10px;
}

.member-card {
    padding: 15px;
    border-radius: 10px;
    background-color: #fafafa;
    border-left: 5px solid #cc0000;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# LOAD DATA
# ==========================================
def load_data(url):
    try:
        r = requests.get(
            f"{url}&nocache={time.time()}",
            timeout=10
        )

        r.raise_for_status()

        df = pd.read_csv(
            io.StringIO(r.text),
            encoding="utf-8"
        )

        return df.fillna("Chưa có")

    except Exception as e:
        st.error(f"Lỗi tải dữ liệu: {e}")
        return pd.DataFrame()

# ==========================================
# SESSION
# ==========================================
if "auth" not in st.session_state:
    st.session_state.auth = False

if "menu" not in st.session_state:
    st.session_state.menu = "HOME"

# ==========================================
# LOGIN
# ==========================================
if not st.session_state.auth:

    st.markdown(
        '<div class="red-header">QUẢN TRỊ CHI BỘ ẤP 4</div>',
        unsafe_allow_html=True
    )

    with st.form("login_form"):

        password = st.text_input(
            "Mật khẩu truy cập",
            type="password"
        )

        submit = st.form_submit_button("ĐĂNG NHẬP")

        if submit:

            if password == PASSWORD:
                st.session_state.auth = True
                st.rerun()

            else:
                st.error("Sai mật khẩu!")

    st.stop()

# ==========================================
# HOME
# ==========================================
if st.session_state.menu == "HOME":

    st.markdown(
        '<div class="red-header">MENU QUẢN LÝ</div>',
        unsafe_allow_html=True
    )

    if st.button("👤 HỒ SƠ ĐẢNG VIÊN"):
        st.session_state.menu = "HOSO"
        st.rerun()

    if st.button("➕ THÊM ĐẢNG VIÊN"):
        st.session_state.menu = "THEM"
        st.rerun()

    st.write("---")

    if st.button("🚪 ĐĂNG XUẤT"):
        st.session_state.auth = False
        st.rerun()

# ==========================================
# HỒ SƠ ĐẢNG VIÊN
# ==========================================
elif st.session_state.menu == "HOSO":

    if st.button("⬅️ QUAY LẠI"):
        st.session_state.menu = "HOME"
        st.rerun()

    st.markdown(
        '<div class="red-header">HỒ SƠ ĐẢNG VIÊN</div>',
        unsafe_allow_html=True
    )

    df = load_data(URL_HOSO)

    if not df.empty:

        st.markdown(
            '<div class="content-box">',
            unsafe_allow_html=True
        )

        # SEARCH
        search = st.text_input(
            "🔍 Tìm kiếm đảng viên"
        )

        if df.shape[1] >= 2:

            name_col = df.columns[1]

            if search:
                df = df[
                    df[name_col]
                    .astype(str)
                    .str.contains(search, case=False)
                ]

            member_names = df[name_col].tolist()

            selected = st.selectbox(
                "Chọn đảng viên",
                member_names
            )

            row = df[
                df[name_col] == selected
            ].iloc[0]

            birth = row.iloc[2] if len(row) > 2 else "N/A"
            position = row.iloc[3] if len(row) > 3 else "N/A"
            note = row.iloc[4] if len(row) > 4 else "N/A"

            st.markdown(f'''
            <div class="member-card">
            <h4>{selected}</h4>
            <p><b>Ngày sinh:</b> {birth}</p>
            <p><b>Chức vụ:</b> {position}</p>
            <p><b>Ghi chú:</b> {note}</p>
            </div>
            ''', unsafe_allow_html=True)

        else:
            st.warning("Dữ liệu Google Sheets không đúng cấu trúc.")

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    else:
        st.warning("Không tải được dữ liệu.")

# ==========================================
# THÊM ĐẢNG VIÊN
# ==========================================
elif st.session_state.menu == "THEM":

    if st.button("⬅️ QUAY LẠI"):
        st.session_state.menu = "HOME"
        st.rerun()

    st.markdown(
        '<div class="red-header">THÊM ĐẢNG VIÊN</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="content-box">',
        unsafe_allow_html=True
    )

    with st.form("add_member_form", clear_on_submit=True):

        name = st.text_input("Họ và tên")
        dob = st.text_input("Ngày sinh")
        position = st.text_input("Chức vụ")
        phone = st.text_input("Số điện thoại")

        photo = st.file_uploader(
            "Ảnh đảng viên",
            type=["jpg", "jpeg", "png"]
        )

        submit = st.form_submit_button(
            "LƯU THÔNG TIN"
        )

        if submit:

            if not name:
                st.error("Vui lòng nhập họ tên.")

            else:

                st.success(f"Đã thêm tạm thời: {name}")

                if photo:
                    st.image(
                        photo,
                        width=180,
                        caption=name
                    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )
```
