# app.py
import streamlit as st
import sqlite3
import os
from datetime import datetime, date
import pandas as pd
import plotly.express as px
import io

# -----------------------
DB_PATH = "police_rms.db"
PHOTOS_DIR = "photos"

# -----------------------
def init_db():
    os.makedirs(PHOTOS_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS suspects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        dob TEXT,
        gender TEXT,
        address TEXT,
        phone TEXT,
        occupation TEXT,
        photo_front TEXT,
        photo_left TEXT,
        photo_right TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS crimes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        crime_type TEXT,
        description TEXT,
        occurred_at TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# -----------------------
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

    html, body, .stApp {
      font-family: 'Roboto', sans-serif;
      background: linear-gradient(135deg,#f4f7ff 0%, #f7eefb 100%);
    }

    .title {
      text-align:center;
      font-size:26px;
      font-weight:700;
      color:#0f172a;
      margin-bottom:18px;
    }

    /* Card */
    .card {
      border-radius:18px;
      padding:26px 18px;
      text-align:center;
      color:#0f172a;
      box-shadow: 0 8px 22px rgba(15,23,42,0.08);
      transition: transform .18s ease, box-shadow .18s ease;
      margin-bottom:14px;
      display:block;
    }
    .card:hover { transform: translateY(-6px); box-shadow: 0 14px 36px rgba(15,23,42,0.12); }
    .card-icon { font-size:34px; margin-bottom:10px; display:block; }
    .card-label { font-size:15px; font-weight:600; }

    /* Buttons / Form inputs */
    .stButton>button { border-radius:12px; padding:10px 18px; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stDateInput>div>div>input {
      border-radius:10px;
    }

    /* Small image placeholder */
    .img-placeholder {
      width:120px;
      height:120px;
      border-radius:10px;
      background:#f1f5f9;
      display:flex;
      align-items:center;
      justify-content:center;
      color:#94a3b8;
    }

    /* Responsive grid wrapper for dashboard cards */
    .dashboard-row { display:flex; gap:18px; flex-wrap:wrap; justify-content:center; margin-bottom:14px; }
    .dashboard-col { flex: 1 1 240px; max-width: 320px; }

    </style>
    """, unsafe_allow_html=True)

# -----------------------
def dashboard_card(icon, label, page, gradient):
    html = f"""
    <a href='?page={page}' style="text-decoration:none;">
      <div class="card" style="background:{gradient};">
        <div class="card-icon">{icon}</div>
        <div class="card-label">{label}</div>
      </div>
    </a>
    """
    st.markdown(html, unsafe_allow_html=True)

# -----------------------
def home_page():
    load_css()
    st.markdown('<div class="title">🚔 Police Record Management System</div>', unsafe_allow_html=True)

    st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-col">', unsafe_allow_html=True)
    dashboard_card("👤", "Suspects", "suspects", "linear-gradient(135deg,#bbdefb,#90caf9)")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dashboard-col">', unsafe_allow_html=True)
    dashboard_card("⚖️", "Crimes", "crimes", "linear-gradient(135deg,#f8bbd0,#f48fb1)")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dashboard-col">', unsafe_allow_html=True)
    dashboard_card("📊", "Reports", "reports", "linear-gradient(135deg,#c8e6c9,#a5d6a7)")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-col">', unsafe_allow_html=True)
    dashboard_card("👮", "Officers", "officers", "linear-gradient(135deg,#ffe0b2,#ffcc80)")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dashboard-col">', unsafe_allow_html=True)
    dashboard_card("🏛️", "Cases", "cases", "linear-gradient(135deg,#d1c4e9,#b39ddb)")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dashboard-col">', unsafe_allow_html=True)
    dashboard_card("⚙️", "Settings", "settings", "linear-gradient(135deg,#f0f4c3,#e6ee9c)")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
def suspects_page():
    load_css()
    st.markdown('<div class="title">👤 Suspect Biodata</div>', unsafe_allow_html=True)

    # Form: create suspect
    with st.form("suspect_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            dob = st.date_input("Date of Birth", value=date(1990,1,1))
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        with col2:
            address = st.text_area("Address")
            phone = st.text_input("Phone Number")
            occupation = st.text_input("Occupation")
        st.markdown("### 📸 Upload Photos (optional)")
        f1, f2, f3 = st.columns(3)
        with f1:
            front_img = st.file_uploader("Front view", type=["jpg","jpeg","png"], key="front")
        with f2:
            left_img = st.file_uploader("Left view", type=["jpg","jpeg","png"], key="left")
        with f3:
            right_img = st.file_uploader("Right view", type=["jpg","jpeg","png"], key="right")

        submitted = st.form_submit_button("Save Suspect")
        if submitted:
            if not name:
                st.error("Name is required.")
            else:
                conn = get_connection(); c = conn.cursor()
                c.execute("""INSERT INTO suspects
                    (name, dob, gender, address, phone, occupation)
                    VALUES (?,?,?,?,?,?)""",
                          (name, dob.isoformat(), gender, address, phone, occupation))
                suspect_id = c.lastrowid
                conn.commit()

                # save photos and update DB
                front_path = left_path = right_path = None
                if front_img:
                    ext = os.path.splitext(front_img.name)[1]
                    front_path = os.path.join(PHOTOS_DIR, f"{suspect_id}_front{ext}")
                    with open(front_path,"wb") as f: f.write(front_img.getbuffer())
                if left_img:
                    ext = os.path.splitext(left_img.name)[1]
                    left_path = os.path.join(PHOTOS_DIR, f"{suspect_id}_left{ext}")
                    with open(left_path,"wb") as f: f.write(left_img.getbuffer())
                if right_img:
                    ext = os.path.splitext(right_img.name)[1]
                    right_path = os.path.join(PHOTOS_DIR, f"{suspect_id}_right{ext}")
                    with open(right_path,"wb") as f: f.write(right_img.getbuffer())

                if any([front_path, left_path, right_path]):
                    c.execute("""UPDATE suspects SET photo_front=?, photo_left=?, photo_right=? WHERE id=?""",
                              (front_path, left_path, right_path, suspect_id))
                    conn.commit()
                conn.close()
                st.success(f"✅ Suspect '{name}' saved (id={suspect_id}).")

    # ------------------- Gallery + Search & Filters -------------------
    st.markdown("## 🔍 Search & Filter Suspects")
    g1, g2 = st.columns([2,1])
    with g1:
        search_name = st.text_input("Search by name (partial)")
    with g2:
        filter_gender = st.selectbox("Gender", ["All","Male","Female","Other"])
    col1, col2 = st.columns(2)
    with col1:
        dob_from = st.date_input("DOB from", value=date(1900,1,1))
    with col2:
        dob_to = st.date_input("DOB to", value=date.today())

    # Build query
    q = """SELECT id, name, dob, gender, phone, occupation, photo_front, photo_left, photo_right, created_at
           FROM suspects WHERE 1=1 """
    params = []
    if search_name:
        q += " AND name LIKE ?"
        params.append(f"%{search_name}%")
    if filter_gender != "All":
        q += " AND gender = ?"
        params.append(filter_gender)
    if dob_from and dob_to:
        q += " AND date(dob) BETWEEN ? AND ?"
        params.append(dob_from.isoformat()); params.append(dob_to.isoformat())
    q += " ORDER BY created_at DESC"

    conn = get_connection(); cur = conn.cursor()
    rows = cur.execute(q, params).fetchall()
    conn.close()

    if not rows:
        st.info("No suspects found for the selected filters.")
    else:
        for r in rows:
            sid, name, dob, gender, phone, occupation, p_front, p_left, p_right, created_at = r
            c1, c2 = st.columns([1,4])
            if p_front and os.path.exists(p_front):
                c1.image(p_front, width=120)
            else:
                c1.markdown('<div class="img-placeholder">No image</div>', unsafe_allow_html=True)
            info_md = f"**{name}**  \n\n{gender} • {occupation}  \n\nDOB: {dob}  \n\nPhone: {phone}  \n\nAdded: {created_at}"
            c2.markdown(info_md)

# -----------------------
def crimes_page():
    load_css()
    st.markdown('<div class="title">⚖️ Crime Records</div>', unsafe_allow_html=True)

    with st.form("crime_form"):
        title = st.text_input("Short title (optional)")
        crime_type = st.text_input("Crime Type (e.g. Robbery, Fraud)")
        occurred_at = st.date_input("Date occurred", value=date.today())
        description = st.text_area("Description / details")
        submitted = st.form_submit_button("Save Crime")
        if submitted:
            if not crime_type:
                st.error("Crime type is required.")
            else:
                conn = get_connection(); c = conn.cursor()
                c.execute("""INSERT INTO crimes (title, crime_type, description, occurred_at)
                             VALUES (?,?,?,?)""",
                          (title, crime_type, description, occurred_at.isoformat()))
                conn.commit(); conn.close()
                st.success("✅ Crime saved.")

    st.markdown("## 🔍 Search & Filter Crimes")
    search_crime = st.text_input("Search by type or keyword")
    cs1, cs2 = st.columns(2)
    with cs1:
        crime_from = st.date_input("Crime from", value=date(2000,1,1))
    with cs2:
        crime_to = st.date_input("Crime to", value=date.today())

    q = "SELECT id, title, crime_type, description, occurred_at, created_at FROM crimes WHERE 1=1 "
    params = []
    if search_crime:
        q += " AND (crime_type LIKE ? OR description LIKE ? OR title LIKE ?)"
        params.extend([f"%{search_crime}%", f"%{search_crime}%", f"%{search_crime}%"])
    if crime_from and crime_to:
        q += " AND date(occurred_at) BETWEEN ? AND ?"
        params.append(crime_from.isoformat()); params.append(crime_to.isoformat())
    q += " ORDER BY created_at DESC"

    conn = get_connection(); cur = conn.cursor()
    rows = cur.execute(q, params).fetchall()
    conn.close()

    if not rows:
        st.info("No crimes found for the selected filters.")
    else:
        for r in rows:
            cid, title, ctype, desc, occurred_at, created_at = r
            st.markdown(f"**{title or ctype}** — {ctype}  \n\n{desc[:300]}  \n\nOccurred: {occurred_at} • Added: {created_at}")

# -----------------------
def reports_page():
    load_css()
    st.markdown('<div class="title">📊 Reports</div>', unsafe_allow_html=True)

    conn = get_connection()
    try:
        df_counts = pd.read_sql_query("SELECT crime_type, COUNT(*) as cnt FROM crimes GROUP BY crime_type", conn)
    except Exception:
        df_counts = pd.DataFrame(columns=["crime_type","cnt"])
    total_suspects = conn.execute("SELECT COUNT(*) FROM suspects").fetchone()[0]
    total_crimes = conn.execute("SELECT COUNT(*) FROM crimes").fetchone()[0]
    conn.close()

    st.metric("Total Suspects", total_suspects)
    st.metric("Total Crimes", total_crimes)

    if not df_counts.empty:
        fig = px.bar(df_counts, x="crime_type", y="cnt", title="Crimes by Type")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No crime data to chart yet.")

    # CSV export example
    export_conn = get_connection()
    df_sus = pd.read_sql_query("SELECT * FROM suspects ORDER BY created_at DESC", export_conn)
    df_cr = pd.read_sql_query("SELECT * FROM crimes ORDER BY created_at DESC", export_conn)
    export_conn.close()
    if not df_sus.empty:
        csv_s = df_sus.to_csv(index=False).encode("utf-8")
        st.download_button("Download Suspects CSV", csv_s, file_name="suspects.csv", mime="text/csv")
    if not df_cr.empty:
        csv_c = df_cr.to_csv(index=False).encode("utf-8")
        st.download_button("Download Crimes CSV", csv_c, file_name="crimes.csv", mime="text/csv")

# -----------------------
def misc_pages(page):
    load_css()
    st.markdown(f"<h2 style='text-align:center'>{page.title()}</h2>", unsafe_allow_html=True)
    st.info("This section is a placeholder. We can add Officers / Cases / Settings screens on request.")

# -----------------------
def main():
    init_db()
    # set default
    if "page" not in st.session_state:
        st.session_state.page = "home"

    # sync page with query params if present
    qp = st.experimental_get_query_params()
    if "page" in qp:
        st.session_state.page = qp.get("page")[0]

    page = st.session_state.page or "home"

    if page == "home":
        home_page()
    elif page == "suspects":
        suspects_page()
    elif page == "crimes":
        crimes_page()
    elif page == "reports":
        reports_page()
    elif page in ("officers","cases","settings"):
        misc_pages(page)
    else:
        st.error("Unknown page. Returning to home.")
        st.experimental_set_query_params(page="home")
        st.session_state.page = "home"

    # back to home link
    if page != "home":
        st.markdown("<br><a href='?page=home'>⬅️ Back to Home</a>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
