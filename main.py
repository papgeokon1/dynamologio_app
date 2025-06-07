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

st.divider()
st.header("📁 Μαζική Εισαγωγή από Excel")

uploaded_file = st.file_uploader("Ανέβασε αρχείο Excel με στρατιώτες", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Ανάγνωση με σωστή παράκαμψη κεφαλίδων
        df_excel = pd.read_excel(uploaded_file, skiprows=4)

        # Φιλτράρισμα απαραίτητων στηλών
        required_columns = ["ΟΜΟΜΑΤΕΠΩΝΥΜΟ", "ΑΜ", "ΤΗΛΕΦΩΝΟ", "ΚΑΤΗΓΟΡΙΑ", "ΔΝ"]
        if all(col in df_excel.columns for col in required_columns):
            st.success("✅ Το αρχείο διαβάστηκε επιτυχώς!")
            st.dataframe(df_excel[required_columns], use_container_width=True)

            if st.button("📤 Εισαγωγή όλων στη βάση"):
                counter = 0
                for _, row in df_excel.iterrows():
                    if pd.isna(row["ΟΜΟΜΑΤΕΠΩΝΥΜΟ"]) or pd.isna(row["ΑΜ"]):
                        continue
                    onoma = str(row["ΟΜΟΜΑΤΕΠΩΝΥΜΟ"]).strip()
                    am = str(row["ΑΜ"]).strip()
                    kinito = str(row["ΤΗΛΕΦΩΝΟ"]).strip() if not pd.isna(row["ΤΗΛΕΦΩΝΟ"]) else ""
                    kathgoria = str(row["ΚΑΤΗΓΟΡΙΑ"]).strip()
                    enoplos = 1 if str(row["ΔΝ"]).strip().upper() == "ΝΑΙ" else 0

                    eisagogi_stratioti(onoma, am, kinito, kathgoria, enoplos)
                    counter += 1

                st.success(f"✅ Εισήχθησαν {counter} στρατιώτες στη βάση.")
        else:
            st.error("❌ Το αρχείο δεν περιέχει τις απαιτούμενες στήλες.")
    except Exception as e:
        st.error(f"⚠️ Σφάλμα κατά την ανάγνωση του αρχείου: {e}")
