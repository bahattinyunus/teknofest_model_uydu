# Kullanım Kılavuzu – TEKNOFEST Model Uydu Yer İstasyonu

## Gereksinimler

```
Python >= 3.10
pip install -r requirements.txt
```

## Kurulum

```powershell
git clone https://github.com/bahattinyunus/teknofest_model_uydu.git
cd teknofest_model_uydu
python -m venv env
.\env\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Çalıştırma Modları

### 1. Konsol Simülasyon Modu
```powershell
python src/main.py
```
Renkli konsol çıktısı, FSM + EKF + PID entegreli.

### 2. PyQt5 Grafik Arayüz (GUI)
```powershell
python src/main.py --gui
```
Canlı grafik, telemetri tablosu ve CSV kayıt.

### 3. Gerçek Donanım Modu
```powershell
python src/main.py --port COM3
```
LoRa modülün bağlı olduğu seri portu belirtin.

## Testleri Çalıştırma

```powershell
pip install pytest
pytest tests/ -v
```

## Sık Sorulan Sorular

**S: LoRa modülüm tanınmıyor?**
A: Aygıt Yöneticisi → COM portları kısmından doğru portu bulun. CH340 sürücüsü gerekiyorsa [buradan](https://sparks.gogo.co.nz/ch340.html) indirin.

**S: PyQt5 kurulum hatası alıyorum?**
A: `pip install PyQt5==5.15.9` ile sabit versiyonu deneyin.

**S: CSV verilerini nerede bulabilirim?**
A: Program çalıştırıldığı dizinde `telemetry_YYYYMMDD_HHMMSS.csv` olarak oluşturulur.
