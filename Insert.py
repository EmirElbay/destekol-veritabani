import sqlite3
import json
from UpdateDB import get_connection  # Ana bağlantıyı buradan paylaşıyoruz

# A) Yeni Kullanıcı Kaydı
def kullanici_ekle(ad, soyad, tc_no, email, telefon, rol='Ikisi_De'):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Kullanicilar (Ad, Soyad, TC_No, E_Mail, Telefon, Rol)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ad, soyad, tc_no, email, telefon, rol))
        conn.commit()
        return True, "Kullanıcı başarıyla kaydedildi."
    except sqlite3.IntegrityError:
        return False, "Bu E-posta, TC veya Telefon numarası zaten kayıtlı!"
    finally:
        conn.close()

# B) Yeni Bağış İlanı Açma
def ilan_ekle(sahip_id, ilan_ad, kategori_id, ozellikler_dict, toplam_adet=1):
    conn = get_connection()
    cursor = conn.cursor()
    ozellikler_json = json.dumps(ozellikler_dict, ensure_ascii=False)
    try:
        cursor.execute("""
            INSERT INTO Ilanlar (Sahip_ID, Ilan_Ad, Kategori_ID, Ozellikler, Toplam_Adet, Kalan_Adet)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sahip_id, ilan_ad, kategori_id, ozellikler_json, toplam_adet, toplam_adet))
        conn.commit()
        return True, "Bağış ilanı açıldı, onay bekliyor."
    except sqlite3.Error as e:
        return False, f"Hata: {e}"
    finally:
        conn.close()

# C) Eşyaya Talep Oluşturma
def talep_olustur(ilan_id, talep_eden_id, istenen_adet=1):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Talepler (Ilan_ID, Talep_Eden_ID, Istenen_Adet)
            VALUES (?, ?, ?)
        """, (ilan_id, talep_eden_id, istenen_adet))
        conn.commit()
        return True, "Talebiniz başarıyla iletildi."
    except sqlite3.Error as e:
        return False, f"Hata: {e}"
    finally:
        conn.close()
