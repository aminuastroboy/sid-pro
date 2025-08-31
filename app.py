import streamlit as st
import sqlite3
import os
from datetime import datetime
import matplotlib.pyplot as plt

# =========================
# DB SETUP
# =========================
DB_FILE = "police_rms.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Suspects table
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

    # Crimes table
    c.execute('''CREATE TABLE IF NOT EXISTS crimes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        date TEXT,
        location TEXT,
        suspect_id INTEGER,
        officer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()

# =========================
# GLOBAL STYLES
# =========================
def load_css():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            font-family: 'Roboto', sans-serif;
        }
        .card {
            background: white;
            color: #333;
            padding: 1.2rem;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.2s ease-in-out;
            text-align: center;
            font-size: 1.1rem;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }
        h1, h2, h3 {
            color: #f5f5f5 !important;
            font-weight: 500;
        }
        .suspect-img {
            border-radius: 12px;
            margin: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.25);
            transition: transform 0.2s;
        }
        .suspect-img:hover { transform: scale(1.05); }
        a { text-decoration: none; color: #1e3c72; }
        </style>
    """, unsafe_allow_html=True)

# =========================
# PAGES
# =========================
def home():
    load_css()
    st.markdown("<h1>🚔 Police Record Management System</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card">👤 <a href="?page=suspects">Suspects</a></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">⚖️ <a href="?page=crimes">Crimes</a></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card">📊 <a href="?page=reports">Reports</a></div>', unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown('<div class="card">👮 <a href="?page=officers">Officers</a></div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="card">🏛️ <a href="?page=cases">Cases</a></div>', unsafe_allow_html=True)
    with col6:
        st.markdown('<div class="card">⚙️ <a href="?page=settings">Settings</a></div>', unsafe_allow_html=True)

def suspects_page():
    load_css()
    st.markdown("<h2>👤 Suspect Biodata</h2>", unsafe_allow_html=True)

    with st.form("suspect_form"):
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
                img_row[i].image(path, width=150, caption=pos.capitalize())

def crimes_page():
    load_css()
    st.markdown("<h2>⚖️ Crimes</h2>", unsafe_allow_html=True)
    with st.form("crime_form"):
        title = st.text_input("Crime Title")
        description = st.text_area("Description")
        date = st.date_input("Date of Incident")
        location = st.text_input("Location")
        suspect_id = st.number_input("Suspect ID (if known)", step=1, min_value=0)
        officer = st.text_input("Officer in Charge")
        submitted = st.form_submit_button("💾 Save Crime")

        if submitted:
            conn = get_connection()
            c = conn.cursor()
            c.execute("INSERT INTO crimes (title,description,date,location,suspect_id,officer) VALUES (?,?,?,?,?,?)",
                      (title, description, date, location, suspect_id, officer))
            conn.commit()
            conn.close()
            st.success("✅ Crime record saved!")

def reports_page():
    load_css()
    st.markdown("<h2>📊 Reports Dashboard</h2>", unsafe_allow_html=True)

    conn = get_connection()
    c = conn.cursor()

    # Totals
    c.execute("SELECT COUNT(*) FROM suspects")
    total_suspects = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM crimes")
    total_crimes = c.fetchone()[0]

    # Gender distribution
    c.execute("SELECT gender, COUNT(*) FROM suspects GROUP BY gender")
    gender_data = c.fetchall()

    # Crimes by officer
    c.execute("SELECT officer, COUNT(*) FROM crimes GROUP BY officer")
    crime_by_officer = c.fetchall()

    conn.close()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="card">👤 Total Suspects: {total_suspects}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="card">⚖️ Total Crimes: {total_crimes}</div>', unsafe_allow_html=True)

    st.markdown("### 👥 Gender Distribution of Suspects")
    if gender_data:
        labels = [row[0] for row in gender_data]
        values = [row[1] for row in gender_data]
        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.info("No suspects available yet.")

    st.markdown("### 👮 Crimes by Officer")
    if crime_by_officer:
        officers = [row[0] for row in crime_by_officer]
        counts = [row[1] for row in crime_by_officer]
        fig, ax = plt.subplots()
        ax.bar(officers, counts)
        ax.set_ylabel("Number of Crimes")
        ax.set_xlabel("Officer")
        ax.set_title("Crimes Assigned per Officer")
        st.pyplot(fig)
    else:
        st.info("No crimes available yet.")

# =========================
# ROUTER
# =========================
PAGES = {
    "home": home,
    "suspects": suspects_page,
    "crimes": crimes_page,
    "reports": reports_page,
}

def main():
    init_db()
    query_params = st.query_params
    page = query_params.get("page", ["home"])[0]
    if page in PAGES:
        PAGES[page]()
    else:
        home()

if __name__ == "__main__":
    main()
