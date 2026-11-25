from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Senin hazırladığın ve klasörde duran dosyaları ithal ediyoruz
import Insert
import select
import UpdateDB
import Delete
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="DestekOl Bağış Platformu API",
    description="Hem Web hem Mobil frontend ekiplerinin kullanacağı merkezi backend sistemi.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme aşamasında tüm kaynaklara izin verir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. FRONTEND'DEN GELECEK VERİ KALIPLARI (Pydantic Modelleri) ---

class KullaniciEkleModel(BaseModel):
    ad: str
    soyad: str
    tc_no: str
    email: str
    telefon: str
    rol: Optional[str] = "Ikisi_De"

class IlanEkleModel(BaseModel):
    sahip_id: int
    ilan_ad: str
    kategori_id: int
    ozellikler: Dict[str, Any]
    toplam_adet: Optional[int] = 1

class TalepOlusturModel(BaseModel):
    ilan_id: int
    talep_eden_id: int
    istenen_adet: Optional[int] = 1

class KullaniciGuncelleModel(BaseModel):
    user_id: int
    yeni_telefon: Optional[str] = None
    yeni_email: Optional[str] = None

class IlanOzellikGuncelleModel(BaseModel):
    ilan_id: int
    yeni_ozellikler: Dict[str, Any]


# --- 2. API UÇLARI (Endpoints) ---

# --- VERİ EKLEME (POST) ---
@app.post("/api/kullanici/ekle", tags=["Ekleme İşlemleri"])
def api_kullanici_ekle(data: KullaniciEkleModel):
    durum, mesaj = Insert.kullanici_ekle(data.ad, data.soyad, data.tc_no, data.email, data.telefon, data.rol)
    if not durum:
        raise HTTPException(status_code=400, detail=mesaj)
    return {"durum": "basarili", "mesaj": mesaj}

@app.post("/api/ilan/ekle", tags=["Ekleme İşlemleri"])
def api_ilan_ekle(data: IlanEkleModel):
    durum, mesaj = Insert.ilan_ekle(data.sahip_id, data.ilan_ad, data.kategori_id, data.ozellikler, data.toplam_adet)
    if not durum:
        raise HTTPException(status_code=400, detail=mesaj)
    return {"durum": "basarili", "mesaj": mesaj}

@app.post("/api/talep/olustur", tags=["Ekleme İşlemleri"])
def api_talep_olustur(data: TalepOlusturModel):
    durum, mesaj = Insert.talep_olustur(data.ilan_id, data.talep_eden_id, data.istenen_adet)
    if not durum:
        raise HTTPException(status_code=400, detail=mesaj)
    return {"durum": "basarili", "mesaj": mesaj}


# --- VERİ LİSTELEME (GET) ---
@app.get("/api/ilanlar/aktif", tags=["Listeleme İşlemleri"])
def api_aktif_ilanlar():
    veriler = select.aktif_ilanlari_getir()
    return {"durum": "basarili", "ilanlar": veriler}

@app.get("/api/ilanlar/onay-bekleyen", tags=["Listeleme İşlemleri"])
def api_onay_bekleyen_ilanlar():
    veriler = select.onay_bekleyen_ilanlari_getir()
    return {"durum": "basarili", "ilanlar": veriler}

@app.get("/api/sistem/loglar", tags=["Listeleme İşlemleri"])
def api_sistem_loglari(limit: int = Query(50, description="Kaç adet log getirilsin?")):
    veriler = select.sistem_loglarini_getir(limit)
    return {"durum": "basarili", "loglar": veriler}


# --- VERİ GÜNCELLEME (PUT / PATCH) ---
@app.put("/api/kullanici/guncelle", tags=["Güncelleme İşlemleri"])
def api_kullanici_guncelle(data: KullaniciGuncelleModel):
    durum, mesaj = UpdateDB.kullanici_guncelle(data.user_id, data.yeni_telefon, data.yeni_email)
    if not durum:
        raise HTTPException(status_code=400, detail=mesaj)
    return {"durum": "basarili", "mesaj": mesaj}

@app.patch("/api/ilan/onayla/{ilan_id}", tags=["Güncelleme İşlemleri"])
def api_ilan_onayla(ilan_id: int, durum: int = Query(..., description="1: Onayla, 0: Beklet/Reddet")):
    UpdateDB.ilan_onayla(ilan_id, durum)
    return {"durum": "basarili", "mesaj": f"İlan onay durumu {durum} olarak güncellendi."}

@app.post("/api/talep/onayla", tags=["Güncelleme İşlemleri"])
def api_talep_onayla(talep_id: int, ilan_id: int):
    # Senin meşhur stok düşüren akıllı fonksiyonunu çağırıyoruz
    durum, mesaj = UpdateDB.talebi_onayla_ve_stok_dus(talep_id, ilan_id)
    if not durum:
        raise HTTPException(status_code=400, detail=mesaj)
        
    # İşlem başarılı olunca arka plana hemen log ekliyoruz
    UpdateDB.log_ekle(user_id=None, islem_turu="TALEP_ONAYLANDI", detay=f"{talep_id} nolu talep onaylandı, ilan {ilan_id} stoğu düşürüldü.")
    return {"durum": "basarili", "mesaj": mesaj}


# --- VERİ SİLME (DELETE) ---
@app.delete("/api/ilan/sil/{ilan_id}", tags=["Silme İşlemleri"])
def api_ilan_sil(ilan_id: int):
    durum, mesaj = Delete.ilan_sil(ilan_id)
    if not durum:
        raise HTTPException(status_code=400, detail=mesaj)
    return {"durum": "basarili", "mesaj": mesaj}
