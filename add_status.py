
import sqlite3

DB_PATH = "dynamologio_final.db"

# Η κατάσταση που θέλουμε να προσθέσουμε
new_status = ("Προσκεκολλημένοι", 0)  # (όνομα, απαιτεί μονάδα)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Έλεγχος αν υπάρχει ήδη
cursor.execute("SELECT COUNT(*) FROM katastaseis WHERE onoma = ?", (new_status[0],))
exists = cursor.fetchone()[0]

if exists:
    print("✅ Η κατάσταση υπάρχει ήδη στη βάση.")
else:
    cursor.execute("INSERT INTO katastaseis (onoma, apaitei_monada) VALUES (?, ?)", new_status)
    conn.commit()
    print("✅ Η κατάσταση 'Προσκεκολλημένοι' προστέθηκε επιτυχώς.")

conn.close()
