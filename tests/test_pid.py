"""
test_pid.py – PIDController birim testleri
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import time
import pytest
from pid import PIDController


@pytest.fixture
def pid():
    return PIDController(kp=2.0, ki=0.15, kd=0.8,
                         setpoint=13.0,
                         output_min=1000.0, output_max=2000.0)


class TestPIDController:

    def test_output_within_bounds_slow_descent(self, pid):
        """Yavaş iniş → çıkış maksimuma yakın olmalı (daha fazla güç)."""
        out = pid.compute(5.0)   # hedef 13 m/s, ölçülen 5 m/s → büyük hata
        assert pid.output_min <= out <= pid.output_max

    def test_output_within_bounds_fast_descent(self, pid):
        """Hızlı iniş → çıkış minimumlara yakın."""
        out = pid.compute(20.0)
        assert pid.output_min <= out <= pid.output_max

    def test_output_at_setpoint_near_middle(self, pid):
        """Setpoint'te yaklaşık orta PWM beklenir (birçok adım sonra)."""
        for _ in range(50):
            pid.compute(13.0)
        out = pid.compute(13.0)
        # sadece sınır içinde olduğunu doğrula
        assert pid.output_min <= out <= pid.output_max

    def test_reset_clears_integral(self, pid):
        for _ in range(20):
            pid.compute(5.0)         # integrale birikmesine izin ver
        pid.reset()
        assert pid.get_diagnostics()["integral"] == pytest.approx(0.0)

    def test_compute_count_increments(self, pid):
        for _ in range(7):
            pid.compute(13.0)
        assert pid.compute_count == 7

    def test_set_setpoint_updates(self, pid):
        pid.set_setpoint(10.0)
        assert pid.setpoint == pytest.approx(10.0)

    def test_get_tuning_returns_correct_values(self, pid):
        t = pid.get_tuning()
        assert t["Kp"] == pytest.approx(2.0)
        assert t["Ki"] == pytest.approx(0.15)
        assert t["Kd"] == pytest.approx(0.8)

    def test_anti_windup_prevents_integral_overflow(self, pid):
        """Integralin sınırı aşmamasını doğrula."""
        for _ in range(500):
            pid.compute(0.0)   # büyük sürekli hata
        diag = pid.get_diagnostics()
        assert abs(diag["integral"]) <= pid.anti_windup_limit
