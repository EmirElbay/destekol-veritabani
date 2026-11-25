import sqlite3
from UpdateDB import talebi_onayla_ve_stok_dus

conn = sqlite3.connect("veritabani.db")
conn.execute("INSERT INTO Talepler (Ilan_ID, Talep_Eden_ID, Istenen_Adet) VALUES (1, 2, 3)")
conn.commit()
conn.close()

print(talebi_onayla_ve_stok_dus(2))

conn = sqlite3.connect("veritabani.db")
print(conn.execute("SELECT Toplam_Adet, Kalan_Adet, Ilan_Durumu FROM Ilanlar WHERE Ilan_ID = 1").fetchall())
conn.close()