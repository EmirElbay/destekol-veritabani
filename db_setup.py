from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "veritabani.db"

sql = r"""PRAGMA foreign_keys = ON;

-- 1. KULLANICILAR TABLOSU (Tüm istatistikleri ve rolleri tek yerde topladık)
CREATE TABLE IF NOT EXISTS Kullanicilar (
    User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Ad TEXT NOT NULL,
    Soyad TEXT NOT NULL,
    TC_No TEXT UNIQUE,
    E_Mail TEXT UNIQUE,
    Telefon TEXT UNIQUE CHECK (
        Telefon IS NULL OR (
            length(trim(Telefon)) BETWEEN 10 AND 11 
            AND Telefon NOT GLOB '*[^0-9]*'
        )
    ),
    -- Rol Kontrolü: Bagisci, Alan veya İkisi De olabilir
    Rol TEXT CHECK (Rol IN ('Bagisci', 'BagisAlan', 'Ikisi_De')) DEFAULT 'Ikisi_De',
    
    -- İstatistikler (Ayrı tablolara gerek kalmadan temiz yönetim)
    Bagis_Yapma_Sayisi INTEGER DEFAULT 0,
    
    Bagis_Alma_Sayisi INTEGER DEFAULT 0,
    Puan_Durumu INTEGER DEFAULT 0,
    Kayit_Tarihi DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. KATEGORİLER TABLOSU
CREATE TABLE IF NOT EXISTS Kategoriler (
    Kategori_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Kategori_Ad TEXT NOT NULL UNIQUE,
    Aciklama TEXT
);

-- 3. İLANLAR TABLOSU (Bağışlanan Eşyalar)
CREATE TABLE IF NOT EXISTS Ilanlar (
    Ilan_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Sahip_ID INTEGER NOT NULL,
    Ilan_Ad TEXT NOT NULL,
    Kategori_ID INTEGER NOT NULL,          -- TEXT yerine Kategori tablosuna bağladık
    Ozellikler TEXT,
    Toplam_Adet INTEGER NOT NULL DEFAULT 1, -- Örn: 5 adet
    Kalan_Adet INTEGER NOT NULL CHECK (Kalan_Adet >= 0 AND Kalan_Adet <= Toplam_Adet),
    Onay_Durumu INTEGER NOT NULL DEFAULT 0,  -- Admin onayı (0: Bekliyor, 1: Onaylandı)
    Ilan_Durumu TEXT CHECK (Ilan_Durumu IN ('Aktif', 'Tukendi', 'Pasif')) DEFAULT 'Aktif',
    Kayit_Tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Sahip_ID) REFERENCES Kullanicilar(User_ID) ON DELETE CASCADE,
    FOREIGN KEY (Kategori_ID) REFERENCES Kategoriler(Kategori_ID)
);

-- 4. TALEPLER TABLOSU (Miktar düşüşünü tetikleyecek hareketler)
CREATE TABLE IF NOT EXISTS Talepler (
    Talep_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Ilan_ID INTEGER NOT NULL,
    Talep_Eden_ID INTEGER NOT NULL,
    Istenen_Adet INTEGER NOT NULL DEFAULT 1, -- Örn: 2 adet istendi
    
    -- Talep Durumu Kontrolü
    Durum TEXT CHECK (Durum IN ('Beklemede', 'Onaylandi', 'Reddedildi', 'Teslim_Edildi')) DEFAULT 'Beklemede',
    Talep_Tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (Ilan_ID) REFERENCES Ilanlar(Ilan_ID) ON DELETE CASCADE,
    FOREIGN KEY (Talep_Eden_ID) REFERENCES Kullanicilar(User_ID) ON DELETE CASCADE
);

-- 5. BULUŞMALAR TABLOSU 
CREATE TABLE IF NOT EXISTS Bulusmalar (
    Bulusma_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Talep_ID INTEGER NOT NULL UNIQUE,       -- Hangi talebe ait buluşma (Birebir ilişki)
    
    -- Konum Bilgileri
    Bulusma_Adresi TEXT NOT NULL,          -- Örn: "Atatürk Parkı Girişi"
    Enlem REAL,                            -- GPS Opsiyonel
    Boylam REAL,                           -- GPS Opsiyonel
    
    -- Zaman Bilgisi
    Bulusma_Tarihi TEXT NOT NULL,          -- Örn: "2026-10-25 14:30"
    
    -- Süreç / Durum Kontrolü
    Durum TEXT CHECK (
        Durum IN ('Randevu_Olusturuldu', 'Tamamlandi', 'Iptal_Edildi', 'Gelinmedi')
    ) DEFAULT 'Randevu_Olusturuldu',
    
    -- Güvenlik Detayı
    Teslim_Kodu TEXT,                       -- Eşyayı teslim ederken girilecek onay kodu
    
    FOREIGN KEY (Talep_ID) REFERENCES Talepler(Talep_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Sistem_Loglari (
    Log_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    User_ID INTEGER,                       -- İşlemi yapan kullanıcı (Admin veya normal üye)
    Islem_Turu TEXT NOT NULL,              -- Örn: 'TALEP_ONAYLANDI', 'STOK_DUSURULDU', 'GIRIS_YAPILDI'
    Detay TEXT,                            -- Örn: '5 nolu talep onaylandı, ilan stoğu 2 azaltıldı.'
    IP_Adresi TEXT,                        -- Güvenlik için opsiyonel
    Zaman_Damgasi DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID) REFERENCES Kullanicilar(User_ID) ON DELETE SET NULL
);

"""

# Veritabanı bağlantısı ve çalıştırılması
conn = None
try:
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(sql)
    with open(BASE_DIR / "trigger.txt", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.commit()
    print("Veritabanı ve tüm tablolar başarıyla oluşturuldu abi!")
except sqlite3.Error as e:
    print(f"Bir hata oluştu: {e}")
finally:
    if conn:
        conn.close()


