# PCB Şema ve Layout Notları

Bu dizin, KiCad devre şemaları ve baskı devre layout dosyalarını içermektedir.

## Devre Açıklaması

Ana PCB, STM32 Nucleo-64 üzerine kurulan bir **Shield** tasarımıdır.
Ayrı bir şase montaj kartı olarak üretilmiştir.

### Blok Diyagramı

```
[3S LiPo 11.1V]
     │
     ├─→ [5V Reg (MP2307)]→ STM32, GPS, Sensörler
     └─→ [BEC (6V)]        → Servo
         └─→ [ESC 1 & 2]   → Motorlar

[STM32F446RE]
     ├─→ I2C  → MPU6050, BMP180
     ├─→ UART1→ GPS
     ├─→ UART2→ LoRa E32
     ├─→ PWM  → ESC1, ESC2, Servo
     └─→ SPI  → SD Kart
```

## Koruma Önlemleri

| Risk | Önlem |
|:---|:---|
| Ters kutuplaşma | SS14 Schottky diyot |
| Aşırı akım | 3A sigorta (XT30) |
| RF paraziti | RF modül ground plane izolasyonu |
| Titreşim | Tüm konnektörlerde MX1.25 kilit |

## Dosyalar

> **Not:** KiCad dosyaları IP koruması nedeniyle henüz eklenmemiştir.

- `main_shield.kicad_sch` *(yakında)*
- `main_shield.kicad_pcb` *(yakında)*
- `gerber/` *(yakında)*
