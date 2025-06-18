
import sqlite3
import pandas as pd

# Φόρτωση Excel και καθαρισμός
excel_path = "ΔΥΝΑΜΟΛΟΓΙΟ 16-06-25.xlsx"
start_index = pd.read_excel(excel_path, header=None)[0].eq("Α/Α").idxmax()
df = pd.read_excel(excel_path, header=start_index + 1)

df = df.rename(columns={
    df.columns[0]: "Α/Α",
    df.columns[1]: "Βαθμός",
    df.columns[2]: "Ονοματεπώνυμο",
    df.columns[3]: "ΣΙ",
    df.columns[4]: "Τηλέφωνο",
    df.columns[5]: "ΑΣΜ",
    df.columns[6]: "ΕΣΣΟ",
    df.columns[7]: "Παρατηρήσεις"
}).dropna(subset=["ΑΣΜ", "Ονοματεπώνυμο"])

# Κρατάμε μόνο μοναδικά ΑΣΜ
df = df.drop_duplicates(subset="ΑΣΜ", keep="first")

# Προετοιμασία εγγραφών
records = []
for _, row in df.iterrows():
    records.append((
        str(row["ΑΣΜ"]).strip(),
        str(row["Ονοματεπώνυμο"]).strip(),
        str(row["Βαθμός"]).strip() if pd.notna(row["Βαθμός"]) else None,
        str(row["ΣΙ"]).strip() if pd.notna(row["ΣΙ"]) else None,
        str(row["Τηλέφωνο"]).strip() if pd.notna(row["Τηλέφωνο"]) else None,
        str(row["ΕΣΣΟ"]).strip() if pd.notna(row["ΕΣΣΟ"]) else None,
        str(row["Παρατηρήσεις"]).strip() if pd.notna(row["Παρατηρήσεις"]) else None,
        None,
        None
    ))

# Δημιουργία βάσης
conn = sqlite3.connect("dynamologio_final.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS stratiotes")
cursor.execute("DROP TABLE IF EXISTS katastaseis")

cursor.execute("""
CREATE TABLE katastaseis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    onoma TEXT NOT NULL UNIQUE,
    apaitei_monada BOOLEAN NOT NULL CHECK (apaitei_monada IN (0, 1))
)
""")

cursor.execute("""
CREATE TABLE stratiotes (
    asm TEXT PRIMARY KEY,
    onomateponymo TEXT NOT NULL,
    bathmos TEXT,
    si TEXT,
    tilefono TEXT,
    esso TEXT,
    paratiriseis TEXT,
    katastasi_id INTEGER,
    monada TEXT,
    FOREIGN KEY (katastasi_id) REFERENCES katastaseis(id)
)
""")

base_statuses = [
    ("Παρόντες", 0),
    ("Αδειούχοι", 0),
    ("Διάθεση εντός φρουράς", 1),
    ("Διάθεση εκτός φρουράς", 1),
    ("Ενίσχυση", 1),
    ("ΣΠΕΝ", 1),
    ("Ειδικότητα", 1),
    ("ΚΑΑΥ", 1),
    ("ΕΜΙΝ ΑΓΑ", 0)
]

cursor.executemany("INSERT INTO katastaseis (onoma, apaitei_monada) VALUES (?, ?)", base_statuses)
cursor.executemany("INSERT INTO stratiotes (asm, onomateponymo, bathmos, si, tilefono, esso, paratiriseis, katastasi_id, monada) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", records)

conn.commit()
conn.close()
print("✅ Η βάση δεδομένων δημιουργήθηκε επιτυχώς.")
