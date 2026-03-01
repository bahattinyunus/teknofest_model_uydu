# Donanım Özellikleri – TEKNOFEST Model Uydu

## Bileşen Listesi (BOM)

| Bileşen | Model | Adet | Açıklama |
|:---|:---|:---:|:---|
| **MCU** | STM32F446RE (Nucleo-64) | 1 | Cortex-M4, 180 MHz, FPU |
| **IMU** | MPU6050 | 1 | 6-eksen hızlanmametre + jiroskop, I2C |
| **Barometer** | BMP180 | 1 | Basınç + sıcaklık, I2C |
| **GPS** | NEO-6M | 1 | UART, 10 Hz, 2.5m CEP |
| **RF Modül** | Ebyte E32-433T20D | 2 | LoRa 433 MHz, 20 dBm, ~3 km menzil |
| **Servo** | MG90S | 1 | Payload ayrılma mekanizması |
| **ESC** | 30A BLHeli_S | 2 | Fırçasız motor kontrolü |
| **Pil** | 3S LiPo 1500 mAh | 1 | 11.1V nominal, 50C |
| **SD Kart Modülü** | Micro-SD SPI | 1 | Veri kaydı |
| **Buzzer** | Pasif 5V | 1 | Kurtarma sinyali |

## Elektrik Bütçesi

| Kaynak | Maks. Akım | Ortalama |
|:---|:---|:---|
| STM32 + Çevre | 150 mA | 80 mA |
| MPU6050 | 3.9 mA | 3.9 mA |
| GPS NEO-6M | 67 mA | 45 mA |
| LoRa TX Piksi | 120 mA | 20 mA |
| Servo (pasif) | 10 mA | 10 mA |
| **Toplam** | **~350 mA** | **~160 mA** |

**Pil Ömrü Tahmini:** 1500 mAh / 160 mA ≈ **9.4 saat** (görev süresi <30 dk, güvenli marj sağlar)

## Arabirimler

```
STM32F446RE
  ┣━━ I2C1  → MPU6050 (SDA: PB7, SCL: PB6)
  ┣━━ I2C1  → BMP180  (SDA: PB7, SCL: PB6) [aynı bus]
  ┣━━ USART1 → GPS NEO-6M (TX: PA9, RX: PA10)
  ┣━━ USART2 → LoRa E32   (TX: PA2, RX: PA3, M0: PA4, M1: PA5)
  ┣━━ TIM1   → ESC PWM1   (PA8)
  ┣━━ TIM1   → ESC PWM2   (PA9)
  ┣━━ TIM2   → Servo       (PA0)
  ┣━━ SPI1   → SD Kart    (SCK: PA5, MISO: PA6, MOSI: PA7, CS: PA4)
  ┗━━ GPIO   → Buzzer     (PC13)
```
