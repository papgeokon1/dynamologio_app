import streamlit as st
from db_manager import create_db, eisagogi_stratioti, pare_stratiotes
import pandas as pd

st.set_page_config(page_title="Δυναμολόγιο Μονάδας", layout="centered")
create_db()

st.title("📋 Δυναμολόγιο Μονάδας")

st.header("➕ Καταχώρηση Στρατιώτη")
with st.form("form_stratioti"):
    onoma = st.text_input("Ονοματεπώνυμο")
    arithmos = st.text_input("Στρατιωτικός Αριθμός")
    kinito = st.text_input("Κινητό")
    kathgoria = st.selectbox("Κατηγορία Ι", ["Ι1", "Ι2", "Ι3", "Ι4"])
    enoplos = st.radio("Ένοπλος;", ["Ναι", "Όχι"])
    submitted = st.form_submit_button("Αποθήκευση")

    if submitted:
        if not onoma or not arithmos:
            st.error("Συμπλήρωσε τα υποχρεωτικά πεδία.")
        else:
            enoplos_val = 1 if enoplos == "Ναι" else 0
            eisagogi_stratioti(onoma, arithmos, kinito, kathgoria, enoplos_val)
            st.success("✅ Ο στρατιώτης καταχωρήθηκε με επιτυχία.")

st.divider()
st.header("👥 Προβολή Στρατιωτών")

rows = pare_stratiotes()
if rows:
    df = pd.DataFrame(rows, columns=["ID", "Ονοματεπώνυμο", "ΑΜ", "Κινητό", "Ι", "Ένοπλος"])
    df["Ένοπλος"] = df["Ένοπλος"].apply(lambda x: "Ναι" if x == 1 else "Όχι")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Δεν υπάρχουν εγγραφές.")
