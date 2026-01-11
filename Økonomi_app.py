import streamlit as st
import json
import os
import hashlib
from datetime import datetime
import pandas as pd

# ---------- CONFIG ----------
st.set_page_config(page_title="Økonomi App", layout="centered")

# ---------- HELPER FUNKTIONER ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists("users.json"):
        with open("users.json","r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.json","w") as f:
        json.dump(users,f)

def get_data_filename(username):
    now = datetime.now()
    month = now.strftime("%Y-%m")
    return f"data_{username}_{month}.json"

def load_data(username):
    filename = get_data_filename(username)
    if os.path.exists(filename):
        with open(filename,"r") as f:
            return json.load(f)
    return {"løn":0, "udgifter":[]}

def save_data(username, data):
    filename = get_data_filename(username)
    with open(filename,"w") as f:
        json.dump(data,f)

# ---------- LOGIN / OPRET BRUGER MED ST.FORM ----------
users = load_users()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💰 Økonomi App Login / Opret bruger")
    
    with st.form("login_form"):
        username = st.text_input("Brugernavn")
        password = st.text_input("Kodeord", type="password")
        login_btn = st.form_submit_button("Login")
        create_btn = st.form_submit_button("Opret bruger")

    if login_btn:
        if username in users and hash_password(password) == users[username]:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Velkommen, {username}!")
        else:
            st.error("Forkert brugernavn eller kodeord")

    if create_btn:
        if username in users:
            st.error("Brugernavn eksisterer allerede")
        elif username.strip()=="" or password.strip()=="":
            st.error("Brugernavn og kodeord må ikke være tomme")
        else:
            users[username] = hash_password(password)
            save_users(users)
            st.success(f"Bruger {username} oprettet! Log ind nu.")
    st.stop()
else:
    username = st.session_state.username

# ---------- APP UI ----------
st.markdown("""
<style>
body { background-color: black; color: white; }
.stButton>button { background-color: red; color: white; border-radius: 10px; }
input, .stNumberInput input, .stTextInput>div>input { background-color: #222 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ---------- LOAD DATA ----------
data = load_data(username)

st.title(f"💰 {username}'s Økonomi - {datetime.now().strftime('%B %Y')}")

# ---------- LØN ----------
data["løn"] = st.number_input("Løn", value=float(data.get("løn",0)))

# ---------- SESSION STATE TIL UDGIFTER ----------
if "udgifter" not in st.session_state:
    st.session_state.udgifter = data.get("udgifter", [])

# ---------- UDGIFTER ----------
st.subheader("Udgifter")
for i, udgift in enumerate(st.session_state.udgifter):
    col1, col2, col3 = st.columns([3,2,2])
    st.session_state.udgifter[i]["kategori"] = col1.text_input("Kategori", udgift.get("kategori",""), key=f"kategori{i}")
    st.session_state.udgifter[i]["navn"] = col2.text_input("Navn", udgift.get("navn",""), key=f"navn{i}")
    st.session_state.udgifter[i]["beløb"] = col3.number_input("Beløb", value=float(udgift.get("beløb",0)), key=f"beløb{i}")

if st.button("➕ Tilføj udgift"):
    st.session_state.udgifter.append({"kategori":"","navn":"","beløb":0})

# ---------- RESULTAT ----------
st.subheader("Oversigt")
udgifter_sum = sum(u["beløb"] for u in st.session_state.udgifter)
tilbage = data["løn"] - udgifter_sum

# Dynamisk liste efter kategori
kategorier = {}
for u in st.session_state.udgifter:
    cat = u["kategori"].strip() or "Andet"
    if cat not in kategorier:
        kategorier[cat] = []
    kategorier[cat].append(u)

for cat, items in kategorier.items():
    st.markdown(f"**{cat}**")
    for item in items:
        if item["navn"].strip():
            st.write(f"- {item['navn']}: {item['beløb']:.2f} kr")
    cat_sum = sum(i["beløb"] for i in items)
    st.write(f"**Sum {cat}: {cat_sum:.2f} kr**\n")

st.write(f"**Samlede udgifter:** {udgifter_sum:.2f} kr")
st.write(f"**Tilbage:** {tilbage:.2f} kr")

# ---------- GRAFISK OVERSIGT ----------
st.subheader("📊 Grafisk oversigt pr. kategori")
if kategorier:
    cat_data = {cat: sum(i["beløb"] for i in items) for cat, items in kategorier.items()}
    df = pd.DataFrame.from_dict(cat_data, orient="index", columns=["Beløb"])
    st.bar_chart(df)

# ---------- GEM DATA ----------
data["udgifter"] = st.session_state.udgifter
save_data(username, data)

# ---------- LOGOUT ----------
if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""




