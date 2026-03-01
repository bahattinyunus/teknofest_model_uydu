# Değişiklik Geçmişi (CHANGELOG)

Tüm önemli değişiklikler bu dosyada belgelenmiştir.
Format: [Keep a Changelog](https://keepachangelog.com/tr/1.0.0/)
Sürümleme: [Semantic Versioning](https://semver.org/)

---

## [1.2.0] – 2026-03-01

### Eklendi
- `src/fsm.py` – 6 durumlu Uçuş Durum Makinesi (IDLE → RECOVERY)
- `src/ekf.py` – 2D Genişletilmiş Kalman Filtresi (barometrik + ivmeölçer füzyonu)
- `src/pid.py` – Anti-windup PID iniş hız kontrolcüsü (ESC PWM çıkışı)
- `src/ground_station.py` – PyQt5 canlı telemetri GUI (grafik + CSV kayıt)
- `tests/test_fsm.py` – FSM birim testleri (11 test senaryosu)
- `tests/test_ekf.py` – EKF birim testleri (8 test senaryosu)
- `tests/test_pid.py` – PID birim testleri (8 test senaryosu)
- `tests/test_telemetry.py` – Telemetri birim testleri (8 test senaryosu)
- `docs/teknik_rapor.md` – Sistem tasarım teknik raporu
- `docs/kullanim_kilavuzu.md` – Kurulum ve çalıştırma kılavuzu
- `docs/hardware_specifications.md` – Donanım BOM ve elektrik bütçesi
- `hardware/3D_Models/README.md` – Şasi baskı parametreleri
- `hardware/PCB_Layout/README.md` – Devre şema block diyagramı
- `LICENSE` – MIT lisansı
- `CONTRIBUTING.md` – Katkı rehberi
- 🌍 README'ye Küresel Rakip Analizi bölümü eklendi (ESA, AIAA, WCRC, Teknofest)
- 🎨 Teknofest temalı yeni banner görseli

### Değiştirildi
- `src/main.py` tamamen yeniden yazıldı: `--gui` ve `--port` argümanları, renkli konsol çıktısı, EKF + PID + FSM entegrasyonu

---

## [1.1.0] – 2026-02-28

### Eklendi
- `assets/banner.png` – Yüksek çözünürlüklü proje banner görüntüsü
- README.md'ye İçindekiler tablosu ve detaylı Mermaid mimari diyagramı

---

## [1.0.0] – 2026-02-25

### Eklendi
- İlk commit: `src/main.py` ve `src/telemetry.py` iskelet kodları
- `README.md` temel dokümantasyon
- `requirements.txt`, `.gitignore` yapılandırma dosyaları
- `assets/`, `docs/`, `hardware/`, `tests/` dizin yapısı
