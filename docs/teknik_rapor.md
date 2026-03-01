# TEKNOFEST Model Uydu – Teknik Rapor

## 1. Giriş

Bu belge, TEKNOFEST Model Uydu Yarışması kapsamında geliştirilen otonom model uydu sisteminin tasarım rationale'ını, algoritma seçimlerini ve sistem entegrasyonunu açıklamaktadır.

---

## 2. Sistem Gereksinimleri

| Gereksinim | Değer |
|:---|:---|
| Görev İrtifası | 700 m (AGL) |
| Payload Ayrılma İrtifası | 400 m |
| Hedef İniş Hızı | 12 – 14 m/s |
| Telemetri Frekansı | ≥ 1 Hz |
| RF Haberleşme | LoRa 433 MHz, E32 modül |
| MCU | STM32F446RE (Cortex-M4, 180 MHz) |
| Güç | 3S LiPo (11.1V nominal, 12.6V tam dolu) |

---

## 3. Yazılım Mimarisi

### 3.1 Uçuş Durum Makinesi (FSM)

6 durumlu deterministik FSM:

```
IDLE → ASCENT → DESCENT → SEPARATION → PAYLOAD → RECOVERY
```

Geçiş koşulları barometrik irtifa ve EKF hız tahminlerine dayanmaktadır.
Manuel ayrılma komutu, yer istasyonundan 433 MHz üzerinden gönderilebilir.

### 3.2 Genişletilmiş Kalman Filtresi (EKF)

**Durum vektörü:** `x = [altitude, velocity_z]`

**Ölçüm kaynakları:**
- BMP180 barometrik irtifa sensörü
- MPU6050 ivmeölçer (Z ekseni)

Gaussian gürültü ve sabit ivme kinematiği varsayımıyla Predict-Update döngüsü çalışır. Joseph kovaryans formu ile numerik kararlılık sağlanmıştır.

**Tipik yakınsama:** ~20 adım sonunda hata < 1.5 m

### 3.3 PID İniş Kontrolcüsü

Anti-windup ve IIR türev filtresi içeren ayrık zamanlı PID:

| Parametre | Değer |
|:---|:---|
| Kp | 2.0 |
| Ki | 0.15 |
| Kd | 0.8 |
| Setpoint | 13.0 m/s |
| Çıkış Aralığı | 1000–2000 µs (ESC PWM) |

---

## 4. Telemetri Protokolü

**Format:** `TEAM_ID,PACKET_NO,PRESSURE,ALTITUDE,SPEED,BATTERY`

Veri, CSV formatında hem yer istasyonuna iletilir hem de SD karta kaydedilir.

---

## 5. Donanım Yorumları

**MCU seçim gerekçesi:** STM32F446RE, Cortex-M4 FPU ile float-nokta EKF hesaplarını donanım hızlandırmalı çalıştırabilmektedir. Arduino'ya kıyasla ~10× daha hızlı is yürütme.

**RF Seçim:** LoRa E32-433T20D (20 dBm çıkış gücü, SF12, ~3 km açık alan menzili).

**IMU Seçim:** MPU6050 I2C, DMP (Digital Motion Processor) donanım quaternion hesaplama desteği.

---

## 6. Test Stratejisi

- **Birim Testler:** `pytest` ile `tests/` dizininde (telemetri, FSM, EKF, PID)
- **Entegrasyon Testi:** Tam uçuş profili simülasyonu (`src/main.py --sim`)
- **Donanım Doğrulama:** Serbest düşüş masası testi (5 m), servo ayrılma testi

---

## 7. Referanslar

1. Grewal, M.S. & Andrews, A.P. "Kalman Filtering: Theory and Practice Using MATLAB", Wiley, 2015.
2. STM32F446RE Reference Manual (RM0390), STMicroelectronics.
3. TEKNOFEST Model Uydu Yarışması Şartnamesi 2025, T3 Vakfı.
4. Astrom, K.J. & Hagglund, T. "PID Controllers: Theory, Design, and Tuning", ISA, 1995.
