"""
ground_station.py – PyQt5 Yer İstasyonu Arayüzü
TEKNOFEST Model Uydu Projesi

Özellikler:
 • Canlı telemetri tablosu
 • İrtifa / Hız matplotlib grafikleri
 • FSM durum göstergesi
 • Seri port bağlantısı (gerçek & simülasyon modu)
 • Veri CSV kaydı
"""

import sys
import csv
import time
import random
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QGroupBox, QPushButton, QComboBox, QStatusBar,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter, QFrame
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor, QPalette

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from telemetry import TelemetryHandler
from commands import SatelliteCommandProcessor

# ── Sabitler ────────────────────────────────────────────────────────────────
FSM_STATE_COLORS = {
    "IDLE"      : "#57606a",
    "ASCENT"    : "#2da44e",
    "DESCENT"   : "#fd8c73",
    "SEPARATION": "#f85149",
    "PAYLOAD"   : "#0969da",
    "RECOVERY"  : "#8250df",
}

FSM_STATE_NAMES = {
    0: "IDLE",
    1: "ASCENT",
    2: "DESCENT",
    3: "SEPARATION",
    4: "PAYLOAD",
    5: "RECOVERY",
}

MAX_DATA_POINTS = 300
TELEMETRY_INTERVAL_MS = 500


# ── Grafik widget'ı ──────────────────────────────────────────────────────────
class LivePlot(FigureCanvas):
    def __init__(self, title: str, ylabel: str, color: str, parent=None):
        fig = Figure(figsize=(5, 2.5), facecolor="#0d1117")
        super().__init__(fig)
        self.setParent(parent)

        self.ax = fig.add_subplot(111)
        self.ax.set_facecolor("#161b22")
        self.ax.set_title(title, color="#c9d1d9", fontsize=9)
        self.ax.set_ylabel(ylabel, color="#c9d1d9", fontsize=8)
        self.ax.tick_params(colors="#c9d1d9", labelsize=7)
        for spine in self.ax.spines.values():
            spine.set_edgecolor("#30363d")

        self.line, = self.ax.plot([], [], color=color, linewidth=1.5)
        self._xs: list[float] = []
        self._ys: list[float] = []
        self._start = time.time()

    def append(self, value: float):
        t = time.time() - self._start
        self._xs.append(t)
        self._ys.append(value)
        if len(self._xs) > MAX_DATA_POINTS:
            self._xs.pop(0)
            self._ys.pop(0)
        self.line.set_data(self._xs, self._ys)
        self.ax.relim()
        self.ax.autoscale_view()
        self.draw()


# ── Ana pencere ──────────────────────────────────────────────────────────────
class GroundStation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEKNOFEST Model Uydu – Yer İstasyonu v1.0")
        self.setMinimumSize(1100, 700)
        self._apply_dark_theme()

        self.telemetry = TelemetryHandler()
        self._packet_count = 0
        self._csv_path: Path | None = None
        self._csv_writer = None
        self._csv_file   = None
        self.cmd_processor = SatelliteCommandProcessor()

        self._build_ui()
        self._init_csv()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(TELEMETRY_INTERVAL_MS)

    # ── UI İnşası ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # Başlık çubuğu
        header = QHBoxLayout()
        title_lbl = QLabel("🛰  TEKNOFEST MODEL UYDU – YER İSTASYONU")
        title_lbl.setFont(QFont("Consolas", 13, QFont.Bold))
        title_lbl.setStyleSheet("color:#58a6ff;")
        header.addWidget(title_lbl)
        header.addStretch()

        # Bağlantı kontrolleri
        self.port_combo = QComboBox()
        self.port_combo.addItems(["SİMÜLASYON", "COM3", "COM4", "COM5", "/dev/ttyUSB0"])
        self.port_combo.setStyleSheet("background:#21262d; color:#c9d1d9; border:1px solid #30363d; padding:3px;")
        self.connect_btn = QPushButton("▶  BAĞLAN")
        self.connect_btn.setStyleSheet("background:#238636; color:white; border-radius:4px; padding:5px 14px; font-weight:bold;")
        self.connect_btn.clicked.connect(self._toggle_connection)
        header.addWidget(QLabel("Port:"))
        header.addWidget(self.port_combo)
        header.addWidget(self.connect_btn)
        root.addLayout(header)

        # ── FSM durum göstergesi
        self.fsm_lbl = QLabel("  FSM: IDLE  ")
        self.fsm_lbl.setFont(QFont("Consolas", 10, QFont.Bold))
        self.fsm_lbl.setAlignment(Qt.AlignCenter)
        self.fsm_lbl.setStyleSheet(f"background:{FSM_STATE_COLORS['IDLE']}; color:white; border-radius:6px; padding:4px;")
        root.addWidget(self.fsm_lbl)

        # ── Komut Girişi [YENİ v1.4.0]
        cmd_layout = QHBoxLayout()
        self.cmd_input = QComboBox()
        self.cmd_input.setEditable(True)
        self.cmd_input.addItems(["Ayrılmayı başlat", "Sistemi kapat", "Durumu raporla"])
        self.cmd_input.setStyleSheet("background:#21262d; color:#c9d1d9; border:1px solid #30363d; padding:3px;")
        self.cmd_send_btn = QPushButton("🚀 GÖNDER")
        self.cmd_send_btn.setStyleSheet("background:#1f6feb; color:white; border-radius:4px; padding:5px 14px; font-weight:bold;")
        self.cmd_send_btn.clicked.connect(self._send_command)
        cmd_layout.addWidget(QLabel("Komut:"))
        cmd_layout.addWidget(self.cmd_input)
        cmd_layout.addWidget(self.cmd_send_btn)
        root.addLayout(cmd_layout)

        # ── Ana splitter
        splitter = QSplitter(Qt.Horizontal)

        # Sol: Telemetri tablosu
        left_group = QGroupBox("📡  Canlı Telemetri Verileri")
        left_group.setStyleSheet(self._group_style())
        left_layout = QVBoxLayout(left_group)

        self.tbl = QTableWidget(8, 3)
        self.tbl.setHorizontalHeaderLabels(["Parametre", "Değer", "Birim"])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl.setStyleSheet("background:#0d1117; color:#c9d1d9; gridline-color:#21262d; font-family:Consolas;")
        rows = [
            ("Takım No",   "–", "–"),
            ("Paket No",   "0", "#"),
            ("İrtifa",     "0.00", "m"),
            ("EKF İrtifa", "0.00", "m"),
            ("Hız",        "0.00", "m/s"),
            ("Sıcaklık",   "–", "°C"),
            ("Voltaj",     "–", "V"),
            ("GPS",        "–", "lat, lon"),
        ]
        for r, (p, v, u) in enumerate(rows):
            self.tbl.setItem(r, 0, QTableWidgetItem(p))
            self.tbl.setItem(r, 1, QTableWidgetItem(v))
            self.tbl.setItem(r, 2, QTableWidgetItem(u))

        left_layout.addWidget(self.tbl)
        splitter.addWidget(left_group)

        # Sağ: Grafikler
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.alt_plot  = LivePlot("İrtifa (m)",    "m",     "#58a6ff")
        self.vel_plot  = LivePlot("Hız (m/s)",     "m/s",   "#3fb950")
        self.batt_plot = LivePlot("Voltaj (V)",    "V",     "#d29922")

        right_layout.addWidget(self.alt_plot)
        right_layout.addWidget(self.vel_plot)
        right_layout.addWidget(self.batt_plot)
        splitter.addWidget(right_widget)
        splitter.setSizes([380, 680])
        root.addWidget(splitter)

        # Alt butonlar
        btn_row = QHBoxLayout()
        self.sep_btn = QPushButton("⚡  AYRILMAYI TETİKLE")
        self.sep_btn.setStyleSheet("background:#da3633; color:white; border-radius:4px; padding:5px 14px; font-weight:bold;")
        self.csv_btn = QPushButton("💾  CSV'yi Aç")
        self.csv_btn.setStyleSheet("background:#1f6feb; color:white; border-radius:4px; padding:5px 14px;")
        self.csv_btn.clicked.connect(self._open_csv_folder)
        btn_row.addWidget(self.sep_btn)
        btn_row.addWidget(self.csv_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("color:#8b949e;")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sistem hazır. Bağlanmak için 'BAĞLAN' butonuna tıklayın.")

    # ── Veri Güncelleme ──────────────────────────────────────────────────────
    def _update(self):
        raw = self.telemetry.read_packet_simulation()
        parsed = self.telemetry.parse_packet(raw)
        if "error" in parsed:
            return

        self._packet_count += 1
        alt   = parsed.get("altitude",    0.0)
        speed = parsed.get("speed",       0.0)
        batt  = parsed.get("battery",     0.0)
        temp  = parsed.get("temperature", 25.0)
        state_id = parsed.get("fsm_state", 0)

        # Tablo güncelle
        vals = [
            ("12345", "#"),
            (str(self._packet_count), "#"),
            (f"{alt:.2f}", "m"),
            (f"{alt * 0.98:.2f}", "m"),   # EKF simülasyon farkı
            (f"{speed:.2f}", "m/s"),
            (f"{temp:.1f}", "°C"),
            (f"{batt:.2f}", "V"),
            ("39.9208, 32.8541", "lat,lon"),
        ]
        for r, (v, u) in enumerate(vals):
            self.tbl.item(r, 1).setText(v)
            self.tbl.item(r, 2).setText(u)

        # Grafikler güncelle
        self.alt_plot.append(alt)
        self.vel_plot.append(speed)
        self.batt_plot.append(batt)

        # FSM durumu güncelle
        state_name = FSM_STATE_NAMES.get(state_id, "IDLE")
        color = FSM_STATE_COLORS.get(state_name, "#57606a")
        self.fsm_lbl.setText(f"  FSM: {state_name}  ")
        self.fsm_lbl.setStyleSheet(f"background:{color}; color:white; border-radius:6px; padding:4px; font-weight:bold;")

        # CSV kaydet
        if self._csv_writer:
            self._csv_writer.writerow([
                datetime.now().isoformat(), self._packet_count,
                alt, speed, batt, temp, state_name
            ])

        self.status_bar.showMessage(
            f"Paket #{self._packet_count} | İrtifa: {alt:.1f} m | Hız: {speed:.1f} m/s | {datetime.now().strftime('%H:%M:%S')}"
        )

    def _toggle_connection(self):
        self.status_bar.showMessage("Simülasyon modunda çalışıyor...")

    def _send_command(self):
        text = self.cmd_input.currentText()
        cmd = self.cmd_processor.process_natural_language(text)
        if cmd:
            self.status_bar.showMessage(f"Komut gönderildi: {cmd}")
            if cmd == "TRIGGER_SEPARATION":
                # FSM tetiklemek için burada bir mekanizma (telemetri handler üzerinden vs.) olmalı
                self.fsm_lbl.setText("  FSM: SEPARATION (MANUAL)  ")
                self.fsm_lbl.setStyleSheet(f"background:{FSM_STATE_COLORS['SEPARATION']}; color:white; border-radius:6px; padding:4px; font-weight:bold;")
        else:
            self.status_bar.showMessage("Bilinmeyen komut!")

    def _init_csv(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._csv_path = Path(f"telemetry_{ts}.csv")
        self._csv_file = open(self._csv_path, "w", newline="", encoding="utf-8")
        self._csv_writer = csv.writer(self._csv_file)
        self._csv_writer.writerow(["timestamp", "packet_no", "altitude_m", "speed_mps",
                                   "battery_v", "temperature_c", "fsm_state"])

    def _open_csv_folder(self):
        import subprocess
        if self._csv_path:
            subprocess.Popen(f'explorer /select,"{self._csv_path.resolve()}"')

    def closeEvent(self, event):
        if self._csv_file:
            self._csv_file.close()
        event.accept()

    # ── Yardımcılar ──────────────────────────────────────────────────────────
    def _group_style(self) -> str:
        return ("QGroupBox { color:#c9d1d9; border:1px solid #30363d; border-radius:6px;"
                " margin-top:8px; font-weight:bold; } "
                "QGroupBox::title { subcontrol-origin:margin; left:10px; }")

    def _apply_dark_theme(self):
        self.setStyleSheet(
            "QMainWindow, QWidget { background:#0d1117; color:#c9d1d9; }"
            "QPushButton:hover { opacity:0.85; }"
            "QComboBox QAbstractItemView { background:#21262d; color:#c9d1d9; }"
            "QLabel { color:#c9d1d9; }"
            "QHeaderView::section { background:#161b22; color:#c9d1d9; border:1px solid #30363d; }"
        )


# ── Giriş noktası ────────────────────────────────────────────────────────────
def run():
    app = QApplication(sys.argv)
    app.setApplicationName("Teknofest Yer İstasyonu")
    window = GroundStation()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
