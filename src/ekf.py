"""
ekf.py – Genişletilmiş Kalman Filtresi (Extended Kalman Filter)
TEKNOFEST Model Uydu Projesi

Durum Vektörü: x = [altitude(m), vertical_velocity(m/s)]
Ölçüm Vektörü: z = [barometric_altitude(m), accel_vertical(m/s^2)]

Referans: Grewal & Andrews, "Kalman Filtering: Theory and Practice" (2015)
"""

import numpy as np
import time


class ExtendedKalmanFilter:
    """
    2 boyutlu EKF: barometrik irtifa + ivmeölçer füzyonu.

    Durumlar:
        x[0] = altitude    (m,   AGL)
        x[1] = velocity_z  (m/s, yukarı pozitif)

    Gürültü parametreleri:
        Q : Süreç gürültüsü kovaryansı
        R : Ölçüm gürültüsü kovaryansı
    """

    def __init__(self,
                 dt: float = 0.1,
                 process_noise_std: float = 0.5,
                 baro_noise_std: float = 1.0,
                 accel_noise_std: float = 0.3):
        """
        Args:
            dt                : Örnekleme periyodu (saniye)
            process_noise_std : Süreç gürültüsü std (m/s²)
            baro_noise_std    : Baro irtifa ölçüm gürültüsü std (m)
            accel_noise_std   : İvmeölçer ölçüm gürültüsü std (m/s²)
        """
        self.dt = dt

        # Durum vektörü  [altitude, velocity_z]
        self.x = np.zeros((2, 1))

        # Hata kovaryans matrisi
        self.P = np.eye(2) * 100.0

        # Durum geçiş matrisi  (sabit ivme modeli)
        # x(k+1) = F * x(k) + w
        self.F = np.array([
            [1.0, dt],
            [0.0, 1.0]
        ])

        # Süreç gürültüsü kovaryansı
        q = process_noise_std ** 2
        self.Q = np.array([
            [0.25 * dt**4 * q, 0.5 * dt**3 * q],
            [ 0.5 * dt**3 * q,        dt**2 * q]
        ])

        # Ölçüm matrisi  H : z = H * x
        # z[0] = altitude (barometrik) → doğrudan x[0]
        # z[1] = velocity (türev)      → doğrudan x[1]
        self.H = np.eye(2)

        # Ölçüm gürültüsü kovaryansı
        self.R = np.diag([baro_noise_std**2, accel_noise_std**2])

        # Telemetri
        self.last_update_time: float = time.time()
        self.cycle_count: int = 0

    # ── Tahmin (Predict) ─────────────────────────────────────────────────────
    def predict(self):
        """Durum tahmini: Newton'un kinematiği ile ileri yürüt."""
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        self.cycle_count += 1

    # ── Güncelleme (Update) ──────────────────────────────────────────────────
    def update(self, z_baro_m: float, z_velocity_est_mps: float):
        """
        Ölçüm güncellemesi.

        Args:
            z_baro_m           : Ham barometrik irtifa (m)
            z_velocity_est_mps : İvmeölçerden türetilmiş hız tahmini (m/s)
        """
        z = np.array([[z_baro_m], [z_velocity_est_mps]])

        # Yenilik (inovasyon)
        y = z - self.H @ self.x

        # Yenilik kovaryansı
        S = self.H @ self.P @ self.H.T + self.R

        # Kalman kazancı
        K = self.P @ self.H.T @ np.linalg.inv(S)

        # Durum güncellemesi
        self.x = self.x + K @ y

        # Kovaryans güncellemesi (Joseph formu – numerik kararlılık)
        I = np.eye(2)
        self.P = (I - K @ self.H) @ self.P @ (I - K @ self.H).T + K @ self.R @ K.T

        self.last_update_time = time.time()

    # ── Ana Adım (Tek Çağrı) ─────────────────────────────────────────────────
    def step(self, baro_alt_m: float, accel_z_mps2: float) -> dict:
        """
        Tek çağrıda tahmin + güncelleme.

        Args:
            baro_alt_m    : Barometrik irtifa (m)
            accel_z_mps2  : Dikey ivme (m/s², yerçekimi çıkarılmış)

        Returns:
            dict: filtered_altitude, filtered_velocity
        """
        # İvme → hız entegrasyonu (hız ölçümü olarak kullan)
        vel_est = self.x[1, 0] + accel_z_mps2 * self.dt

        self.predict()
        self.update(baro_alt_m, vel_est)

        return self.get_state()

    # ── Başlatma ─────────────────────────────────────────────────────────────
    def initialize(self, initial_alt_m: float, initial_vel_mps: float = 0.0):
        """İlk konumla filtre sıfırla."""
        self.x = np.array([[initial_alt_m], [initial_vel_mps]])
        self.P = np.diag([4.0, 1.0])   # başlangıç belirsizliği
        self.cycle_count = 0

    # ── Durum Okuma ──────────────────────────────────────────────────────────
    @property
    def altitude(self) -> float:
        return float(self.x[0, 0])

    @property
    def velocity(self) -> float:
        return float(self.x[1, 0])

    def get_state(self) -> dict:
        return {
            "filtered_altitude_m"  : round(self.altitude, 3),
            "filtered_velocity_mps": round(self.velocity, 3),
            "P_diag"               : [round(self.P[0, 0], 4), round(self.P[1, 1], 4)],
            "cycle"                : self.cycle_count,
        }
