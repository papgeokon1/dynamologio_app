import streamlit as st
from db_manager import create_db, eisagogi_stratioti, pare_stratiotes
import pandas as pd
st.title("📋 Δυναμολόγιο Μονάδας")
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

st.set_page_config(page_title="Δυναμολόγιο Μονάδας", layout="centered")
create_db()

st.title("📋 Δυναμολόγιο Μονάδας")
