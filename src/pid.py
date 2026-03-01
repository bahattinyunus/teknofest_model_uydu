"""
pid.py – PID İniş Hız Kontrolcüsü
TEKNOFEST Model Uydu Projesi

Hedef: 12-14 m/s sabit iniş hızını ESC/Motor PWM sinyaliyle korumak.
Anti-windup, derivative filter ve çıkış sınırlama içerir.
"""

import time


class PIDController:
    """
    Ayrık zamanlı PID kontrolcü.

    Çıkış = Kp*e + Ki*∫e dt + Kd*(de/dt)

    Uydu iniş kontrolü için varsayılan katsayılar:
        Kp = 2.0  (oransal)
        Ki = 0.15 (integral)
        Kd = 0.8  (türev)
    """

    def __init__(self,
                 kp: float = 2.0,
                 ki: float = 0.15,
                 kd: float = 0.8,
                 setpoint: float = 13.0,
                 output_min: float = 1000.0,
                 output_max: float = 2000.0,
                 derivative_filter_hz: float = 10.0,
                 anti_windup_limit: float = 500.0):
        """
        Args:
            kp, ki, kd          : PID katsayıları
            setpoint            : Hedef iniş hızı (m/s, mutlak değer)
            output_min/max      : PWM çıkış sınırları (µs, ESC uyumlu)
            derivative_filter_hz: Türev gürültü filtresi kesme frekansı (Hz)
            anti_windup_limit   : İntegral windup sınırlayıcısı
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint

        self.output_min = output_min
        self.output_max = output_max
        self.anti_windup_limit = anti_windup_limit

        # Durum değişkenleri
        self._integral      = 0.0
        self._prev_error    = 0.0
        self._prev_deriv    = 0.0
        self._last_time     = time.time()

        # 1. dereceden IIR türev filtresi katsayısı
        # alpha = 2πfcΔt / (2πfcΔt + 1)  (fc: kesme frekansı, Δt yaklaşık)
        self._fc = derivative_filter_hz
        self._alpha: float | None = None  # ilk compute() çağrısında hesaplana

        # İstatistik
        self.compute_count = 0
        self.last_output   = 0.0

    def _compute_alpha(self, dt: float) -> float:
        import math
        wc = 2.0 * math.pi * self._fc
        return wc * dt / (wc * dt + 1.0)

    def compute(self, measured_velocity_mps: float) -> float:
        """
        Tek PID adımı.

        Args:
            measured_velocity_mps : EKF'den filtrelenmiş iniş hızı (m/s).
                                    Aşağı yönde pozitif değer beklenir.
        Returns:
            PWM değeri (µs) – ESC'e gönderilecek throttle sinyali.
        """
        now = time.time()
        dt  = now - self._last_time
        if dt <= 0.0:
            dt = 1e-3
        self._last_time = now

        if self._alpha is None:
            self._alpha = self._compute_alpha(dt)

        # Hata: hedef hız - ölçülen hız  (+ ise çok yavaş → güç artır)
        error = self.setpoint - abs(measured_velocity_mps)

        # Oransal terim
        p_term = self.kp * error

        # İntegral terim (anti-windup: clamp)
        self._integral += error * dt
        self._integral = max(-self.anti_windup_limit,
                             min(self.anti_windup_limit, self._integral))
        i_term = self.ki * self._integral

        # Türev terim (filtrelenmiş)
        raw_deriv = (error - self._prev_error) / dt
        self._prev_deriv = (self._alpha * raw_deriv +
                            (1.0 - self._alpha) * self._prev_deriv)
        d_term = self.kd * self._prev_deriv

        self._prev_error  = error
        self.compute_count += 1

        # Çıkış + sınırlama
        output = p_term + i_term + d_term
        output = max(self.output_min, min(self.output_max, output))
        self.last_output = output
        return output

    def reset(self):
        """İntegral ve hata geçmişini sıfırla."""
        self._integral   = 0.0
        self._prev_error = 0.0
        self._prev_deriv = 0.0
        self._last_time  = time.time()
        self._alpha      = None

    def set_setpoint(self, new_setpoint: float):
        """Hedef hızı çalışma zamanında değiştir."""
        self.setpoint = new_setpoint

    def get_tuning(self) -> dict:
        return {
            "Kp"      : self.kp,
            "Ki"      : self.ki,
            "Kd"      : self.kd,
            "setpoint": self.setpoint,
        }

    def get_diagnostics(self) -> dict:
        return {
            "integral"    : round(self._integral, 4),
            "last_error"  : round(self._prev_error, 4),
            "last_output" : round(self.last_output, 1),
            "cycles"      : self.compute_count,
        }
