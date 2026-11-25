import sqlite3
from UpdateDB import get_connection

# A) Ana Sayfada Onaylı ve Aktif İlanları Listeleme
def aktif_ilanlari_getir():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Ilan_ID, Ilan_Ad, Kalan_Adet, Ozellikler 
        FROM Ilanlar 
        WHERE Onay_Durumu = 1 AND Ilan_Durumu = 'Aktif'
        ORDER BY Kayit_Tarihi DESC
    """)
    ilanlar = cursor.fetchall()
    conn.close()
    return ilanlar

# B) Admin Panelinde Onay Bekleyen İlanları Listeleme
def onay_bekleyen_ilanlari_getir():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.Ilan_ID, k.Ad || ' ' || k.Soyad AS Sahip, i.Ilan_Ad, i.Toplam_Adet 
        FROM Ilanlar i
        JOIN Kullanicilar k ON i.Sahip_ID = k.User_ID
        WHERE i.Onay_Durumu = 0
    """)
    ilanlar = cursor.fetchall()
    conn.close()
    return ilanlar

# C) Güvenlik Loglarını Listeleme
def sistem_loglarini_getir(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Log_ID, Islem_Turu, Detay, Zaman_Damgasi 
        FROM Sistem_Loglari 
        ORDER BY Zaman_Damgasi DESC LIMIT ?
    """, (limit,))
    loglar = cursor.fetchall()
    conn.close()
    return loglar
