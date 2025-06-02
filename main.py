import tkinter as tk
from tkinter import ttk, messagebox
from db_manager import create_db, eisagogi_stratioti

create_db()

def apothikeusi():
    onoma = entry_onoma.get()
    arithmos = entry_arithmos.get()
    kinito = entry_kinito.get()
    kathgoria = combo_i.get()
    enoplos = 1 if var_enoplos.get() else 0

    if not onoma or not arithmos:
        messagebox.showerror("Σφάλμα", "Συμπληρώστε υποχρεωτικά πεδία.")
        return

    eisagogi_stratioti(onoma, arithmos, kinito, kathgoria, enoplos)
    messagebox.showinfo("Επιτυχία", "Ο στρατιώτης καταχωρήθηκε.")
    entry_onoma.delete(0, tk.END)
    entry_arithmos.delete(0, tk.END)
    entry_kinito.delete(0, tk.END)
    combo_i.set('')
    var_enoplos.set(False)

import sqlite3

def provoli_stratioton():
    window = tk.Toplevel(root)
    window.title("Κατάλογος Στρατιωτών")
    window.geometry("700x400")

    tree = ttk.Treeview(window, columns=("ID", "Ονοματεπώνυμο", "ΑΜ", "Κινητό", "Ι", "Ένοπλος"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Ονοματεπώνυμο", text="Ονοματεπώνυμο")
    tree.heading("ΑΜ", text="Αρ. Μητρώου")
    tree.heading("Κινητό", text="Κινητό")
    tree.heading("Ι", text="Κατηγορία Ι")
    tree.heading("Ένοπλος", text="Ένοπλος")

    tree.column("ID", width=30)
    tree.column("Ονοματεπώνυμο", width=180)
    tree.column("ΑΜ", width=100)
    tree.column("Κινητό", width=100)
    tree.column("Ι", width=80)
    tree.column("Ένοπλος", width=80)

    tree.pack(expand=True, fill='both', padx=10, pady=10)

    # Ανάκτηση δεδομένων από τη βάση
    conn = sqlite3.connect("dynamologio.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stratiotes")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        # Μετατροπή 1/0 σε Ναι/Όχι
        enoplos_text = "Ναι" if row[5] == 1 else "Όχι"
        tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], row[4], enoplos_text))
    

# GUI
root = tk.Tk()
root.title("Δυναμολόγιο Μονάδας")
root.geometry("400x350")

tk.Label(root, text="Ονοματεπώνυμο:").pack()
entry_onoma = tk.Entry(root, width=40)
entry_onoma.pack()

tk.Label(root, text="Στρατιωτικός Αριθμός:").pack()
entry_arithmos = tk.Entry(root, width=40)
entry_arithmos.pack()

tk.Label(root, text="Κινητό:").pack()
entry_kinito = tk.Entry(root, width=40)
entry_kinito.pack()

tk.Label(root, text="Κατηγορία Ι (Ι1-Ι4):").pack()
combo_i = ttk.Combobox(root, values=["Ι1", "Ι2", "Ι3", "Ι4"])
combo_i.pack()

var_enoplos = tk.BooleanVar()
tk.Checkbutton(root, text="Ένοπλος", variable=var_enoplos).pack()

tk.Button(root, text="Αποθήκευση", command=apothikeusi, bg='lightgreen').pack(pady=10)

tk.Button(root, text="Προβολή Στρατιωτών", command=provoli_stratioton, bg='lightblue').pack(pady=5)


root.mainloop()
