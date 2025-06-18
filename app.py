import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = r"C:\Users\georg\OneDrive\Υπολογιστής\dynamologio_app\dynamologio_final.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Αρχικοποίηση λίστας ενεργειών
if "pending_actions" not in st.session_state:
    st.session_state.pending_actions = []

def load_stratiotes():
    conn = get_connection()
    query = '''
    SELECT s.asm, s.onomateponymo, s.bathmos, s.si, s.tilefono, s.esso,
           s.paratiriseis, k.onoma AS katastasi, s.monada
    FROM stratiotes s
    LEFT JOIN katastaseis k ON s.katastasi_id = k.id
    ORDER BY s.onomateponymo
    '''
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def load_katastaseis():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM katastaseis", conn)
    conn.close()
    return df

def execute_pending_actions():
    conn = get_connection()
    cursor = conn.cursor()
    for action in st.session_state.pending_actions:
        if action["type"] == "insert":
            cursor.execute("""
                INSERT INTO stratiotes
                (asm, onomateponymo, bathmos, si, tilefono, esso, paratiriseis, katastasi_id, monada)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, action["data"])
        elif action["type"] == "update":
            cursor.execute("""
                UPDATE stratiotes SET
                onomateponymo = ?, bathmos = ?, si = ?, tilefono = ?, esso = ?,
                paratiriseis = ?, katastasi_id = ?, monada = ?
                WHERE asm = ?
            """, (*action["data"], action["asm"]))
        elif action["type"] == "delete":
            cursor.execute("DELETE FROM stratiotes WHERE asm = ?", (action["asm"],))
    conn.commit()
    conn.close()
    st.session_state.pending_actions.clear()

# ---------------------- UI ----------------------
st.title("📋 Διαχείριση Δυναμολόγιου Μονάδας 625 Μ/Π ΤΠ")

katastaseis_df = load_katastaseis()
kat_dict = {row["onoma"]: row["id"] for _, row in katastaseis_df.iterrows()}
df = load_stratiotes()

tab1, tab2, tab3 = st.tabs(["➕ Προσθήκη", "✏️ Επεξεργασία", "❌ Διαγραφή"])

with tab1:
    st.subheader("Προσθήκη Νέου Στρατιώτη")
    with st.form("add_form", clear_on_submit=True):
        asm = st.text_input("ΑΣΜ")
        name = st.text_input("Ονοματεπώνυμο")
        grade = st.text_input("Βαθμός")
        si = st.text_input("ΣΙ")
        phone = st.text_input("Τηλέφωνο")
        esso = st.text_input("ΕΣΣΟ")
        comments = st.text_input("Παρατηρήσεις")
        katastasi = st.selectbox("Κατάσταση", list(kat_dict.keys()))
        monada_required = katastaseis_df[katastaseis_df["onoma"] == katastasi]["apaitei_monada"].values[0]
        monada = st.text_input("Μονάδα/Τοποθεσία") if monada_required else None
        submitted = st.form_submit_button("📥 Προσθήκη στη Λίστα Αλλαγών")
        if submitted:
            st.session_state.pending_actions.append({
                "type": "insert",
                "data": (asm, name, grade, si, phone, esso, comments, kat_dict[katastasi], monada)
            })
            st.success("✅ Ο στρατιώτης προστέθηκε στη λίστα προς αποθήκευση.")

with tab2:
    st.subheader("Επεξεργασία Στρατιώτη")
    selected = st.selectbox("Επιλέξτε στρατιώτη:", df["asm"] + " - " + df["onomateponymo"])
    if selected:
        asm_edit = selected.split(" - ")[0]
        row = df[df["asm"] == asm_edit].iloc[0]

        with st.form("edit_form"):
            name = st.text_input("Ονοματεπώνυμο", value=row["onomateponymo"])
            grade = st.text_input("Βαθμός", value=row["bathmos"])
            si = st.text_input("ΣΙ", value=row["si"])
            phone = st.text_input("Τηλέφωνο", value=row["tilefono"])
            esso = st.text_input("ΕΣΣΟ", value=row["esso"])
            comments = st.text_input("Παρατηρήσεις", value=row["paratiriseis"])
            katastasi = st.selectbox(
                "Κατάσταση", list(kat_dict.keys()),
                index=list(kat_dict.keys()).index(row["katastasi"]) if row["katastasi"] else 0
            )
            monada_required = katastaseis_df[katastaseis_df["onoma"] == katastasi]["apaitei_monada"].values[0]
            monada = st.text_input("Μονάδα/Τοποθεσία", value=row["monada"] or "") if monada_required else ""

            save_edit = st.form_submit_button("📥 Προσθήκη Επεξεργασίας στη Λίστα")
            if save_edit:
                st.session_state.pending_actions.append({
                    "type": "update",
                    "asm": asm_edit,
                    "data": (name, grade, si, phone, esso, comments, kat_dict[katastasi], monada)
                })
                st.success("✏️ Η επεξεργασία προστέθηκε στη λίστα.")

with tab3:
    st.subheader("Διαγραφή Στρατιώτη")
    selected = st.selectbox("Επιλογή για διαγραφή", df["asm"] + " - " + df["onomateponymo"], key="del")
    if selected:
        asm_del = selected.split(" - ")[0]
        if st.button("🗑️ Προσθήκη Διαγραφής στη Λίστα"):
            st.session_state.pending_actions.append({
                "type": "delete",
                "asm": asm_del
            })
            st.warning("🗑️ Ο στρατιώτης προστέθηκε για διαγραφή.")

# --- Κουμπί Αποθήκευσης ---
st.divider()
if st.session_state.pending_actions:
    if st.button("💾 Αποθήκευση Όλων των Αλλαγών"):
        execute_pending_actions()
        st.success("✅ Όλες οι αλλαγές αποθηκεύτηκαν.")
        st.rerun()

else:
    st.info("Δεν υπάρχουν εκκρεμείς αλλαγές προς αποθήκευση.")

# --- Πίνακας ---
st.divider()
st.subheader("📄 Προβολή Στρατιωτών")

# Φίλτρο κατάστασης
katastasi_options = ["Όλες"] + sorted(df["katastasi"].dropna().unique())
selected_filter = st.selectbox("Φιλτράρισμα κατάστασης:", katastasi_options)

if selected_filter != "Όλες":
    filtered_df = df[df["katastasi"] == selected_filter]
else:
    filtered_df = df

st.dataframe(filtered_df, use_container_width=True)

with st.expander("📊 Στατιστικά Καταστάσεων", expanded=True):
    df_stats = load_stratiotes()
    total = len(df_stats)

    st.markdown(f"### 👥 Συνολικός Αριθμός Στρατιωτών: `{total}`")

    katastaseis_counts = df_stats.groupby("katastasi").size().reset_index(name="Πλήθος")
    katastaseis_counts["Ποσοστό"] = (katastaseis_counts["Πλήθος"] / total * 100).round(2).astype(str) + " %"
    katastaseis_counts = katastaseis_counts.rename(columns={"katastasi": "Κατάσταση"})

    st.markdown("#### 📌 Ανά Κατάσταση")
    st.dataframe(katastaseis_counts, use_container_width=True)

    # Ανάλυση για καταστάσεις με μονάδα
    monadikes = [
        "Διάθεση εντός φρουράς",
        "Διάθεση εκτός φρουράς",
        "Ενίσχυση",
        "Ειδικότητα",
        "ΣΠΕΝ",
        "ΚΑΑΥ"
    ]

    for kat in monadikes:
        filtered = df_stats[df_stats["katastasi"] == kat]
        if not filtered.empty:
            st.markdown(f"#### 🧭 {kat} Ανά Μονάδα/Τοποθεσία")
            grouped = filtered.groupby("monada").size().reset_index(name="Πλήθος")
            grouped["Ποσοστό"] = (grouped["Πλήθος"] / total * 100).round(2).astype(str) + " %"
            grouped = grouped.rename(columns={"monada": "Τοποθεσία"})
            st.dataframe(grouped, use_container_width=True)

    # Ειδική περίπτωση ΕΜΙΝ ΑΓΑ (δεν έχει μονάδα αλλά θέλει ξεχωριστή αναφορά)
    emin = df_stats[df_stats["katastasi"] == "ΕΜΙΝ ΑΓΑ"]
    if not emin.empty:
        count = len(emin)
        perc = round(count / total * 100, 2)
        st.markdown(f"#### 📍 ΕΜΙΝ ΑΓΑ: `{count}` άτομα ({perc} %)")

    st.markdown("### 🧾 Στατιστικά κατά ΕΣΣΟ")

    df_esso = df_stats[df_stats["esso"].notna()]
    esso_counts = df_esso.groupby("esso").size().reset_index(name="Πλήθος")
    esso_counts["Ποσοστό"] = (esso_counts["Πλήθος"] / total * 100).round(2).astype(str) + " %"
    esso_counts = esso_counts.sort_values(by="esso")
    esso_counts = esso_counts.rename(columns={"esso": "ΕΣΣΟ"})

    st.dataframe(esso_counts, use_container_width=True)

import xlsxwriter
import io

def export_to_excel(title):
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT s.asm, s.onomateponymo, s.bathmos, s.si, s.tilefono, s.esso, s.paratiriseis,
               k.onoma as katastasi, k.apaitei_monada, s.monada
        FROM stratiotes s
        LEFT JOIN katastaseis k ON s.katastasi_id = k.id
        ORDER BY k.id, s.onomateponymo
    """, conn)
    katastaseis_df = pd.read_sql_query("SELECT * FROM katastaseis", conn)
    conn.close()

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet("Δυναμολόγιο")
        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 0)
        writer.sheets["Δυναμολόγιο"] = worksheet
        row = 0

        bold = workbook.add_format({"bold": True})
        wrap_format = workbook.add_format({
            "text_wrap": True,
            "valign": "top",
            "border": 1,
            "align": "left",
            "indent": 1
        })

        header_format = workbook.add_format({
            "bold": True, "align": "center", "font_size": 14
        })

        column_widths = {
            "ΑΣΜ": 13,
            "Ονοματεπώνυμο": 30,
            "Βαθμός": 10,
            "ΣΙ": 8,
            "Τηλέφωνο": 12,
            "ΕΣΣΟ": 12,
            "Παρατηρήσεις": 16,
            "Μονάδα": 12
        }

        # Προσθήκη τίτλου χρήστη
        worksheet.merge_range(row, 0, row, 7, title, header_format)
        row += 2

        for _, kat in katastaseis_df.iterrows():
            kname = kat["onoma"]
            kdf = df[df["katastasi"] == kname].copy()
            if kdf.empty:
                continue

            if kname in ["Ειδικότητα", "Ενίσχυση", "ΚΑΑΥ"]:
                monades = kdf["monada"].dropna().unique()
                worksheet.write(row, 0, kname.upper(), bold)
                row += 1

                for mon in monades:
                    sub_kdf = kdf[kdf["monada"] == mon].copy()
                    worksheet.write(row, 0, f"Υπομονάδα: {mon}", bold)
                    row += 1

                    sub_kdf = sub_kdf.rename(columns={
                        "asm": "ΑΣΜ", "onomateponymo": "Ονοματεπώνυμο", "bathmos": "Βαθμός",
                        "si": "ΣΙ", "tilefono": "Τηλέφωνο", "esso": "ΕΣΣΟ", "paratiriseis": "Παρατηρήσεις",
                        "monada": "Μονάδα"
                    })

                    cols = ["ΑΣΜ", "Ονοματεπώνυμο", "Βαθμός", "ΣΙ", "Τηλέφωνο", "ΕΣΣΟ", "Παρατηρήσεις", "Μονάδα"]
                    sub_kdf[cols].to_excel(writer, sheet_name="Δυναμολόγιο", startrow=row, index=False)

                    for col_idx, col_name in enumerate(cols):
                        width = column_widths.get(col_name, 15)
                        worksheet.set_column(col_idx, col_idx, width, wrap_format)

                    row += len(sub_kdf) + 2
            else:
                worksheet.write(row, 0, kname.upper(), bold)
                row += 1

                kdf = kdf.rename(columns={
                    "asm": "ΑΣΜ", "onomateponymo": "Ονοματεπώνυμο", "bathmos": "Βαθμός",
                    "si": "ΣΙ", "tilefono": "Τηλέφωνο", "esso": "ΕΣΣΟ", "paratiriseis": "Παρατηρήσεις",
                    "monada": "Μονάδα"
                })

                cols = ["ΑΣΜ", "Ονοματεπώνυμο", "Βαθμός", "ΣΙ", "Τηλέφωνο", "ΕΣΣΟ", "Παρατηρήσεις"]
                if kat["apaitei_monada"]:
                    cols.append("Μονάδα")

                kdf[cols].to_excel(writer, sheet_name="Δυναμολόγιο", startrow=row, index=False)

                for col_idx, col_name in enumerate(cols):
                    width = column_widths.get(col_name, 15)
                    worksheet.set_column(col_idx, col_idx, width, wrap_format)

                row += len(kdf) + 2

        total = len(df)
        worksheet.write(row, 0, f"ΣΥΝΟΛΙΚΟΣ ΑΡΙΘΜΟΣ ΣΤΡΑΤΙΩΤΩΝ: {total}", bold)
        row += 2

        worksheet.write(row, 0, "ΣΤΑΤΙΣΤΙΚΑ ΑΝΑ ΚΑΤΑΣΤΑΣΗ", bold)
        row += 1
        stats = df.groupby("katastasi").size().reset_index(name="Πλήθος")
        stats["Ποσοστό"] = (stats["Πλήθος"] / total * 100).round(2).astype(str) + " %"
        stats.to_excel(writer, sheet_name="Δυναμολόγιο", startrow=row, index=False)
        row += len(stats) + 2

        worksheet.write(row, 0, "ΣΤΑΤΙΣΤΙΚΑ ΑΝΑ ΕΣΣΟ", bold)
        row += 1
        esso_stats = df.groupby("esso").size().reset_index(name="Πλήθος")
        esso_stats.columns = ["ΕΣΣΟ", "Πλήθος"]
        esso_stats["Ποσοστό"] = (esso_stats["Πλήθος"] / total * 100).round(2).astype(str) + " %"
        esso_stats.to_excel(writer, sheet_name="Δυναμολόγιο", startrow=row, index=False)

    output.seek(0)
    return output



# 👉 Προσθήκη στο κάτω μέρος της εφαρμογής
st.subheader("📤 Εξαγωγή Δυναμολόγιου")
filename = st.text_input("Όνομα αρχείου Excel (χωρίς .xlsx)", value="dynamologio_export")
export_title = st.text_input("Τίτλος αρχείου (θα εμφανιστεί στην κορυφή του Excel)", value="Δυναμολόγιο Στρατοπέδου")

if st.button("📥 Εξαγωγή σε Excel"):
    excel_data = export_to_excel(export_title)
    st.download_button("⬇️ Λήψη Excel", data=excel_data.getvalue(), file_name=f"{filename}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
