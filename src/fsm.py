"""
fsm.py – Uçuş Durum Makinesi (Flight State Machine)
TEKNOFEST Model Uydu Projesi

Durum Geçiş Diyagramı:
  IDLE(0) → ASCENT(1) → DESCENT(2) → SEPARATION(3) → PAYLOAD(4) → RECOVERY(5)
"""

from enum import IntEnum
import time


class FlightState(IntEnum):
    IDLE       = 0   # Bekleme / Kalibrasyon
    ASCENT     = 1   # Yükselme fazı
    DESCENT    = 2   # Model Uydu İnişi (serbest düşüş / paraşüt)
    SEPARATION = 3   # Payload ayrılma (400m)
    PAYLOAD    = 4   # Görev yükü aktif iniş
    RECOVERY   = 5   # Kurtarma / Konumlandırma


class FlightStateMachine:
    """
    Uydu içi yazılım için deterministik uçuş durum makinesi.
    Her döngüde `update()` çağrılarak sensör verileriyle durum güncellenir.
    """

    # ── Eşik Değerleri ────────────────────────────────────────────────────────
    ASCENT_ALT_THRESHOLD_M  = 10.0   # Yükselme tespiti için minimum irtifa (m)
    DESCENT_SPEED_THRESHOLD = -0.5   # Düşüş için dikey hız eşiği (m/s)
    SEPARATION_ALT_M        = 400.0  # Payload ayrılma irtifası (m)
    LANDED_ALT_THRESHOLD_M  = 5.0    # Yere iniş tespiti (m)
    LANDED_SPEED_THRESHOLD  = 0.5    # Yere iniş hız eşiği (|m/s|)

    def __init__(self):
        self.state            = FlightState.IDLE
        self.prev_state       = None
        self.state_entry_time = time.time()
        self.max_altitude_m   = 0.0
        self.separation_done  = False
        self._log: list[str]  = []

    # ── Durum Yönetimi ────────────────────────────────────────────────────────
    def _transition(self, new_state: FlightState):
        if new_state != self.state:
            self._log_event(f"GEÇİŞ: {self.state.name} → {new_state.name}")
            self.prev_state       = self.state
            self.state            = new_state
            self.state_entry_time = time.time()

    def _log_event(self, msg: str):
        entry = f"[FSM][{time.strftime('%H:%M:%S')}] {msg}"
        self._log.append(entry)
        print(entry)

    def time_in_state(self) -> float:
        """Mevcut durumda geçen süre (saniye)."""
        return time.time() - self.state_entry_time

    # ── Ana Güncelleme Döngüsü ────────────────────────────────────────────────
    def update(self, altitude_m: float, vertical_speed_mps: float,
               gps_fix: bool = True) -> FlightState:
        """
        Sensör okumaları ile durumu güncelle.

        Args:
            altitude_m          : Barometrik / EKF irtifası (metre, AGL)
            vertical_speed_mps  : EKF dikey hız (+ yukarı, - aşağı)
            gps_fix             : GPS sinyali var mı?

        Returns:
            Mevcut FlightState
        """
        # İrtifa maksimumunu takip et
        if altitude_m > self.max_altitude_m:
            self.max_altitude_m = altitude_m

        # ── Durum Geçiş Mantığı ───────────────────────────────────────────
        if self.state == FlightState.IDLE:
            if altitude_m > self.ASCENT_ALT_THRESHOLD_M and gps_fix:
                self._transition(FlightState.ASCENT)

        elif self.state == FlightState.ASCENT:
            if vertical_speed_mps < self.DESCENT_SPEED_THRESHOLD:
                self._transition(FlightState.DESCENT)

        elif self.state == FlightState.DESCENT:
            if altitude_m <= self.SEPARATION_ALT_M and not self.separation_done:
                self._transition(FlightState.SEPARATION)

        elif self.state == FlightState.SEPARATION:
            # Mekanik ayrılma için minimum 2 saniye bu durumda kal
            if self.time_in_state() >= 2.0:
                self.separation_done = True
                self._transition(FlightState.PAYLOAD)

        elif self.state == FlightState.PAYLOAD:
            if (altitude_m <= self.LANDED_ALT_THRESHOLD_M and
                    abs(vertical_speed_mps) < self.LANDED_SPEED_THRESHOLD):
                self._transition(FlightState.RECOVERY)

        elif self.state == FlightState.RECOVERY:
            pass  # Terminal durum – buzzer aktif, GPS yayını

        return self.state

    # ── Yardımcı Metotlar ─────────────────────────────────────────────────────
    def trigger_separation(self):
        """Manuel ayrılma komutu (yer istasyonundan gelen komut)."""
        if self.state in (FlightState.DESCENT, FlightState.SEPARATION):
            self._log_event("Manuel ayrılma komutu alındı!")
            self._transition(FlightState.SEPARATION)

    def get_status_dict(self) -> dict:
        return {
            "state_id"   : int(self.state),
            "state_name" : self.state.name,
            "max_alt_m"  : round(self.max_altitude_m, 2),
            "sep_done"   : self.separation_done,
            "time_in_s"  : round(self.time_in_state(), 1),
        }

    def get_log(self) -> list[str]:
        return self._log.copy()
