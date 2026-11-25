import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "veritabani.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")  # Zincirleme silmenin çalışması için şart!
    return conn

def talebi_onayla_ve_stok_dus(talep_id, ilan_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT i.Kalan_Adet, t.Istenen_Adet
            FROM Talepler t
            JOIN Ilanlar i ON i.Ilan_ID = t.Ilan_ID
            WHERE t.Talep_ID = ?
        """, (talep_id,))
        res = cursor.fetchone()
        if not res or res[0] < res[1]:
            return False, "Yetersiz stok veya geçersiz talep!"

        # Stok düşürme ve 'Tukendi' işini trigger'lar yapıyor
        cursor.execute("UPDATE Talepler SET Durum = 'Onaylandi' WHERE Talep_ID = ?", (talep_id,))
        conn.commit()
        return True, "Talep onaylandı."
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Hata: {e}"
    finally:
        conn.close()

def kullanici_guncelle(user_id, yeni_telefon=None, yeni_email=None):
    if not yeni_telefon and not yeni_email:
        return False, "Güncellenecek alan belirtilmedi."
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if yeni_telefon:
            cursor.execute("UPDATE Kullanicilar SET Telefon = ? WHERE User_ID = ?", (yeni_telefon, user_id))
        if yeni_email:
            cursor.execute("UPDATE Kullanicilar SET E_Mail = ? WHERE User_ID = ?", (yeni_email, user_id))
        conn.commit()
        return True, "Kullanıcı bilgileri güncellendi."
    except sqlite3.IntegrityError:
        return False, "Bu telefon veya e-posta başka bir kullanıcıda kayıtlı!"
    finally:
        conn.close()


def ilan_onayla(ilan_id, durum):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Ilanlar SET Onay_Durumu = ? WHERE Ilan_ID = ?", (durum, ilan_id))
        conn.commit()
        return True, "İlan onay durumu güncellendi."
    finally:
        conn.close()

def ilan_ozellikleri_guncelle(ilan_id, yeni_ozellikler_dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Ozellikler FROM Ilanlar WHERE Ilan_ID = ?", (ilan_id,))
        row = cursor.fetchone()
        if not row:
            return False, "İlan bulunamadı."
        mevcut = {}
        if row[0]:
            try:
                mevcut = json.loads(row[0])
            except json.JSONDecodeError:
                pass
        mevcut.update(yeni_ozellikler_dict)
        cursor.execute("UPDATE Ilanlar SET Ozellikler = ? WHERE Ilan_ID = ?",
                       (json.dumps(mevcut, ensure_ascii=False), ilan_id))
        conn.commit()
        return True, "İlan özellikleri güncellendi."
    finally:
        conn.close()


def talep_durumu_guncelle(talep_id, yeni_durum):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Talepler SET Durum = ? WHERE Talep_ID = ?", (yeni_durum, talep_id))
        conn.commit()
        return True, "Talep durumu güncellendi."
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Hata: {e}"
    finally:
        conn.close()


def log_ekle(user_id, islem_turu, detay, ip_adresi=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Sistem_Loglari (User_ID, Islem_Turu, Detay, IP_Adresi)
            VALUES (?, ?, ?, ?)
        """, (user_id, islem_turu, detay, ip_adresi))
        conn.commit()
    finally:
        conn.close()