# DestekOl Bağış Platformu - Backend & Veritabanı API

Bu depo, **DestekOl** projesinin SQLite veritabanı mimarisini, otomatik stok yönetim tetikleyicilerini (trigger) ve FastAPI tabanlı REST API servislerini içerir.

## 🚀 Kurulum ve Çalıştırma (Frontend Ekibi İçin)

Projeyi kendi bilgisayarınızda ayağa kaldırmak için sırasıyla aşağıdaki adımları izleyin:

### 1. Repoyu Bilgisayarınıza Çekin
```bash
git clone https://github.com
cd destekol-veritabani
```

### 2. Gerekli Kütüphaneleri Yükleyin
```bash
pip install -r requirements.txt
```

### 3. Yerel Veritabanını ve Tabloları Oluşturun
*(Veritabanı dosyası `.gitignore` ile gizlenmiştir; ilk çalıştırmada bu komutla kendi yerel veritabanınızı oluşturmalısınız.)*
```bash
python db_setup.py
```

### 4. API Sunucusunu Başlatın
```bash
uvicorn main:app --reload
```

---

## 📚 API Dokümantasyonu ve Test (Swagger UI)

Sunucu çalıştıktan sonra tarayıcınızdan aşağıdaki adrese giderek tüm API uçlarını (endpoint), beklenen JSON formatlarını inceleyebilir ve doğrudan test edebilirsiniz:

👉 **http://127.0.0**

---

## 📂 Proje Yapısı

* `main.py`: FastAPI sunucusu ve tüm HTTP uçları (POST, GET, PUT, PATCH, DELETE)
* `db_setup.py`: Veritabanı tablolarını ve ilişkileri oluşturan kurulum betiği
* `trigger.txt`: Talep onaylandığında veya iptal edildiğinde ilan stoğunu otomatik güncelleyen SQL tetikleyicileri
* `Insert.py` / `select.py` / `UpdateDB.py` / `Delete.py`: Veritabanı CRUD işlem modülleri
