import sqlite3

def create_db():
    conn = sqlite3.connect("dynamologio.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stratiotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            onoma_epitheto TEXT NOT NULL,
            strat_arithmos TEXT NOT NULL,
            kinito TEXT,
            kathgoria_i TEXT,
            enoplos INTEGER
        )
    """)
    conn.commit()
    conn.close()

def eisagogi_stratioti(onoma, arithmos, kinito, kathgoria_i, enoplos):
    conn = sqlite3.connect("dynamologio.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO stratiotes (onoma_epitheto, strat_arithmos, kinito, kathgoria_i, enoplos)
        VALUES (?, ?, ?, ?, ?)
    """, (onoma, arithmos, kinito, kathgoria_i, enoplos))
    conn.commit()
    conn.close()
