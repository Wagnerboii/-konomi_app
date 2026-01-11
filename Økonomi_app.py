import streamlit as st
import json
import os

DATA_FILE = "data.json"

st.set_page_config(page_title="Økonomi App", layout="centered")

# ---------- DATA ----------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"løn": 0, "udgifter": []}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.data, f)

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# ---------- UI ----------
st.title("💰 Økonomi App")

st.markdown("""
<style>
body { background-color: black; color: white; }
.stButton>button {
    background-color: red;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

data["løn"] = st.number_input("Løn", value=float(data["løn"]))

st.subheader("Udgifter")

for i in range(len(data["udgifter"])):
    col1, col2 = st.columns(2)
    data["udgifter"][i] = (
        col1.text_input("Navn", data["udgifter"][i][0], key=f"navn{i}"),
        col2.number_input("Beløb", value=float(data["udgifter"][i][1]), key=f"beløb{i}")
    )

if st.button("➕ Tilføj udgift"):
    data["udgifter"].append(("", 0.0))

# ---------- BEREGNING ----------
udgifter_sum = sum(b for _, b in data["udgifter"])
tilbage = data["løn"] - udgifter_sum

konti = {
    "Mad": tilbage * 0.35,
    "Gæld": tilbage * 0.25,
    "Opsparing": tilbage * 0.25,
    "Fritid": tilbage * 0.15
}

st.subheader("Resultat")
st.write(f"**Tilbage:** {tilbage:.2f} kr")

for k, v in konti.items():
    st.write(f"{k}: {v:.2f} kr")

save_data()
