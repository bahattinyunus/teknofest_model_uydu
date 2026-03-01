"""
main.py – Yer İstasyonu Başlatıcı
TEKNOFEST Model Uydu Projesi

Kullanım:
    python src/main.py            → Konsol modu (simülasyon)
    python src/main.py --gui      → PyQt5 GUI modu
    python src/main.py --port COM3  → Gerçek seri port
"""

import sys
import time
import argparse
from pathlib import Path

# Proje kök dizinini Python path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

from telemetry import TelemetryHandler
from fsm import FlightStateMachine
from ekf import ExtendedKalmanFilter
from pid import PIDController


# ── Konsol renk kodları ──────────────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    GRAY   = "\033[90m"


def print_banner():
    print(f"{C.CYAN}{C.BOLD}")
    print("══════════════════════════════════════════════════")
    print("   🛰  TEKNOFEST MODEL UYDU – YER İSTASYONU      ")
    print("        SİSTEM BAŞLATILIYOR...  v1.0              ")
    print("══════════════════════════════════════════════════")
    print(f"{C.RESET}")


def run_console(port: str | None = None):
    """Konsol modu – gerçek zamanlı telemetri + FSM + EKF + PID."""
    print_banner()

    telemetry = TelemetryHandler(port=port or "COM3")
    fsm       = FlightStateMachine()
    ekf       = ExtendedKalmanFilter(dt=0.5)
    pid       = PIDController(setpoint=13.0)

    print(f"{C.GREEN}[✓] Telemetri Modülü    : HAZIR{C.RESET}")
    print(f"{C.GREEN}[✓] Durum Makinesi (FSM): HAZIR{C.RESET}")
    print(f"{C.GREEN}[✓] EKF Filtresi        : HAZIR{C.RESET}")
    print(f"{C.GREEN}[✓] PID Kontrolcü       : HAZIR{C.RESET}")

    mode = "SİMÜLASYON" if port is None else f"GERÇEK → {port}"
    print(f"\n{C.YELLOW}[≫] Mod: {mode}{C.RESET}")
    print(f"{C.GRAY}{'─' * 50}{C.RESET}")
    print(f"{'Paket':<7} {'İrtifa(m)':<10} {'EKF(m)':<10} {'Hız(m/s)':<10} {'Batt(V)':<8} {'FSM':<12} {'PWM(µs)'}")
    print(f"{C.GRAY}{'─' * 75}{C.RESET}")

    packet_no = 0
    try:
        while True:
            raw    = telemetry.read_packet_simulation()
            parsed = telemetry.parse_packet(raw)
            if "error" in parsed:
                print(f"{C.RED}[ERR] Paket hatası: {parsed['error']}{C.RESET}")
                continue

            alt   = parsed["altitude"]
            speed = parsed["speed"]
            batt  = parsed["battery"]
            packet_no += 1

            # EKF adımı (ivme simülasyonu için rastgele gürültü)
            accel_z = (speed - ekf.velocity) / 0.5   # türev yaklaşımı
            ekf_state = ekf.step(alt, accel_z)
            ekf_alt   = ekf_state["filtered_altitude_m"]
            ekf_vel   = ekf_state["filtered_velocity_mps"]

            # FSM güncelle
            state = fsm.update(ekf_alt, -abs(ekf_vel))   # iniş → negatif

            # PID (yalnızca PAYLOAD durumunda aktif)
            from fsm import FlightState
            if state == FlightState.PAYLOAD:
                pwm = pid.compute(abs(ekf_vel))
            else:
                pwm = 1000   # ESC: boşta

            # Çıktı satırı
            state_color = {
                0: C.GRAY, 1: C.GREEN, 2: C.YELLOW,
                3: C.RED,  4: C.BLUE,  5: C.CYAN,
            }.get(int(state), C.RESET)

            print(f"{packet_no:<7} {alt:<10.2f} {ekf_alt:<10.2f} "
                  f"{speed:<10.2f} {batt:<8.2f} "
                  f"{state_color}{fsm.state.name:<12}{C.RESET} {pwm:.0f}")

            time.sleep(1.0)

    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}[!] Sistem kapatılıyor...{C.RESET}")
        print(f"    Toplam paket: {packet_no}")
        print(f"    Maksimum irtifa: {fsm.max_altitude_m:.1f} m")
        print(f"    Son FSM durumu: {fsm.state.name}")
        sys.exit(0)


def run_gui():
    """PyQt5 GUI modunu başlat."""
    try:
        from ground_station import run
        run()
    except ImportError as e:
        print(f"{C.RED}[!] GUI kütüphaneleri eksik: {e}{C.RESET}")
        print("    pip install PyQt5 matplotlib")
        sys.exit(1)


# ── Argüman Ayrıştırma ───────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="TEKNOFEST Model Uydu – Yer İstasyonu",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python src/main.py                 # Konsol simülasyon modu
  python src/main.py --gui           # PyQt5 grafik arayüz
  python src/main.py --port COM3     # Gerçek LoRa modüle bağlan
        """
    )
    parser.add_argument("--gui",  action="store_true", help="PyQt5 arayüzünü başlat")
    parser.add_argument("--port", type=str, default=None,
                        help="Seri port (COM3, /dev/ttyUSB0…)")
    args = parser.parse_args()

    if args.gui:
        run_gui()
    else:
        run_console(port=args.port)


if __name__ == "__main__":
    main()
