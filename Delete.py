import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "veritabani.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")  # Zincirleme silmenin çalışması için şart!
    return conn

# A) İlanı Sistemden Tamamen Silme
def ilan_sil(ilan_id):
    """
    Belirtilen ilanı siler. ON DELETE CASCADE sayesinde 
    bu ilana yapılmış tüm talepler de otomatik silinir.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Ilanlar WHERE Ilan_ID = ?", (ilan_id,))
        conn.commit()
        return True, "İlan ve ilgili tüm talepler başarıyla silindi."
    except sqlite3.Error as e:
        return False, f"İlan silinirken hata oluştu: {e}"
    finally:
        conn.close()

# B) Talebi İptal Etme / Silme
def talep_sil(talep_id):
    """
    Kullanıcı talebini geri çektiğinde veya ilan sahibi 
    talebi kalıcı olarak sistemden kaldırmak istediğinde kullanılır.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Talepler WHERE Talep_ID = ?", (talep_id,))
        conn.commit()
        return True, "Talep sistemden silindi."
    except sqlite3.Error as e:
        return False, f"Talep silinirken hata oluştu: {e}"
    finally:
        conn.close()

# C) Kullanıcı Hesabını Silme (Opsiyonel / Admin Yetkisi)
def kullanici_sil(user_id):
    """
    Bir kullanıcı hesabını kapatmak istediğinde çalışır.
    Kullanıcının açtığı tüm ilanlar ve talepler otomatik olarak temizlenir.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Kullanicilar WHERE User_ID = ?", (user_id,))
        conn.commit()
        return True, "Kullanıcı hesabı ve tüm ilişkili verileri silindi."
    except sqlite3.Error as e:
        return False, f"Kullanıcı silinirken hata oluştu: {e}"
    finally:
        conn.close()
