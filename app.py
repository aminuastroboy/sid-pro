import streamlit as st
import sqlite3
import os

# ==================================
# Database setup
# ==================================
def get_connection():
    conn = sqlite3.connect("police_rms.db")
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS suspects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    dob TEXT,
                    gender TEXT,
                    address TEXT,
                    phone TEXT,
                    occupation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

# ==================================
# CSS Styling (Material Design style)
# ==================================
def load_css():
    st.markdown("""
        <style>
        /* App background */
        .stApp {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            font-family: 'Roboto', sans-serif;
        }

        /* Section headers */
        h1, h2, h3 {
            color: #f5f5f5 !important;
            font-weight: 500;
        }

        /* General card style */
        .card {
            background: white;
            color: #333;
            padding: 1.2rem;
            border-radius: 16px;
            margin: 15px 5px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.2s ease-in-out;
            text-align: center;
        }
        .card:hover {
            transform: translateY(-6px);
            box-shadow: 0 10px 28px rgba(0,0,0,0.25);
        }

        /* Homepage grid */
        .homepage {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        /* Links inside cards */
        .card a {
            text-decoration: none;
            color: #2a5298;
            font-weight: bold;
            font-size: 1.1rem;
        }

        /* Gallery images */
        .suspect-img {
            border-radius: 12px;
            margin: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.25);
            transition: transform 0.2s;
        }
        .suspect-img:hover {
            transform: scale(1.05);
        }
        </style>
    """, unsafe_allow_html=True)

# ==================================
# Homepage
# ==================================
def home():
    load_css()
    st.markdown("<h1>🚔 Police Record Management System</h1>", unsafe_allow_html=True)

    st.markdown('<div class="homepage">', unsafe_allow_html=True)

    cards = [
        ("👤", "Suspects", "?page=suspects"),
        ("⚖️", "Crimes", "?page=crimes"),
        ("📊", "Reports", "?page=reports"),
        ("👮", "Officers", "?page=officers"),
        ("🏛️", "Cases", "?page=cases"),
        ("⚙️", "Settings", "?page=settings"),
    ]

    for icon, title, link in cards:
        st.markdown(f'<div class="card">{icon}<br><a href="{link}">{title}</a></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ==================================
# Suspects Page
# ==================================
def suspects_page():
    load_css()
    st.markdown("<h2>👤 Suspect Biodata</h2>", unsafe_allow_html=True)

    with st.form("suspect_form"):
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name")
                dob = st.date_input("Date of Birth")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            with col2:
                phone = st.text_input("Phone Number")
                occupation = st.text_input("Occupation")
                address = st.text_area("Address")

        st.markdown("### 📸 Upload Suspect Photos")
        col1, col2, col3 = st.columns(3)
        with col1:
            front_img = st.file_uploader("Front View", type=["jpg","jpeg","png"], key="front")
        with col2:
            left_img = st.file_uploader("Left View", type=["jpg","jpeg","png"], key="left")
        with col3:
            right_img = st.file_uploader("Right View", type=["jpg","jpeg","png"], key="right")

        submitted = st.form_submit_button("💾 Save Suspect")

        if submitted:
            conn = get_connection()
            c = conn.cursor()
            c.execute("INSERT INTO suspects (name,dob,gender,address,phone,occupation) VALUES (?,?,?,?,?,?)",
                      (name, dob, gender, address, phone, occupation))
            suspect_id = c.lastrowid

            os.makedirs("photos", exist_ok=True)
            if front_img:
                with open(f"photos/{suspect_id}_front.jpg","wb") as f: f.write(front_img.getbuffer())
            if left_img:
                with open(f"photos/{suspect_id}_left.jpg","wb") as f: f.write(left_img.getbuffer())
            if right_img:
                with open(f"photos/{suspect_id}_right.jpg","wb") as f: f.write(right_img.getbuffer())

            conn.commit()
            conn.close()
            st.success("✅ Suspect saved with photos!")

    # Gallery + Search
    st.markdown("### 🔎 Search Suspects")
    search = st.text_input("Search by name, phone, or occupation")

    conn = get_connection()
    c = conn.cursor()
    if search:
        c.execute("SELECT * FROM suspects WHERE name LIKE ? OR phone LIKE ? OR occupation LIKE ? ORDER BY created_at DESC",
                  (f"%{search}%", f"%{search}%", f"%{search}%"))
    else:
        c.execute("SELECT * FROM suspects ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        suspect_id, name, dob, gender, address, phone, occupation, created_at = row
        st.markdown(f'<div class="card"><b>{name}</b> — {gender}, {occupation}<br>'
                    f'📅 {dob} | 📞 {phone} | 🏠 {address}</div>', unsafe_allow_html=True)
        img_row = st.columns(3)
        for i, pos in enumerate(["front", "left", "right"]):
            path = f"photos/{suspect_id}_{pos}.jpg"
            if os.path.exists(path):
                img_row[i].image(path, width=150, caption=pos.capitalize(), use_container_width=False)

# ==================================
# Placeholder pages
# ==================================
def crimes_page():
    load_css()
    st.markdown("<h2>⚖️ Crimes</h2>", unsafe_allow_html=True)
    st.info("Coming soon...")

def reports_page():
    load_css()
    st.markdown("<h2>📊 Reports</h2>", unsafe_allow_html=True)
    st.info("Coming soon...")

def officers_page():
    load_css()
    st.markdown("<h2>👮 Officers</h2>", unsafe_allow_html=True)
    st.info("Coming soon...")

def cases_page():
    load_css()
    st.markdown("<h2>🏛️ Cases</h2>", unsafe_allow_html=True)
    st.info("Coming soon...")

def settings_page():
    load_css()
    st.markdown("<h2>⚙️ Settings</h2>", unsafe_allow_html=True)
    st.info("Coming soon...")

# ==================================
# Main App
# ==================================
init_db()
query_params = st.query_params

if "page" in query_params:
    page = query_params["page"]
    if page == "suspects":
        suspects_page()
    elif page == "crimes":
        crimes_page()
    elif page == "reports":
        reports_page()
    elif page == "officers":
        officers_page()
    elif page == "cases":
        cases_page()
    elif page == "settings":
        settings_page()
    else:
        home()
else:
    home()
