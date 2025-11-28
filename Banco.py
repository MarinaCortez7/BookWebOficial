import sqlite3

conexao = sqlite3.connect("bookWeb.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE login (
    id_login INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    senha TEXT NOT NULL
);
""")

conexao.commit()
conexao.close()
