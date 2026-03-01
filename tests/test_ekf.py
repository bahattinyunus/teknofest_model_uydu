"""
test_ekf.py – ExtendedKalmanFilter birim testleri
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from ekf import ExtendedKalmanFilter


@pytest.fixture
def ekf():
    f = ExtendedKalmanFilter(dt=0.1)
    f.initialize(0.0, 0.0)
    return f


class TestExtendedKalmanFilter:

    def test_initial_state_is_zero(self, ekf):
        assert ekf.altitude == pytest.approx(0.0, abs=1e-6)
        assert ekf.velocity == pytest.approx(0.0, abs=1e-6)

    def test_step_returns_dict_with_keys(self, ekf):
        result = ekf.step(baro_alt_m=10.0, accel_z_mps2=0.5)
        for key in ("filtered_altitude_m", "filtered_velocity_mps", "P_diag", "cycle"):
            assert key in result

    def test_altitude_converges_to_true_value(self, ekf):
        """100 adım aynı irtifayı ver – filtre yakınsamalı."""
        true_alt = 300.0
        for _ in range(100):
            ekf.step(baro_alt_m=true_alt, accel_z_mps2=0.0)
        assert ekf.altitude == pytest.approx(true_alt, abs=2.0)

    def test_velocity_estimation_positive_climb(self, ekf):
        """Tırmanma sırasında hız pozitif tahmini olmalı."""
        for step in range(50):
            ekf.step(baro_alt_m=float(step * 2), accel_z_mps2=0.5)
        assert ekf.velocity > 0.0

    def test_cycle_count_increments(self, ekf):
        for i in range(10):
            ekf.step(100.0, 0.0)
        assert ekf.cycle_count == 10

    def test_initialize_resets_state(self, ekf):
        ekf.step(500.0, 2.0)
        ekf.initialize(100.0, 5.0)
        assert ekf.altitude == pytest.approx(100.0)
        assert ekf.velocity == pytest.approx(5.0)
        assert ekf.cycle_count == 0

    def test_covariance_decreases_over_time(self, ekf):
        p_init = ekf.P[0, 0]
        for _ in range(50):
            ekf.step(200.0, 0.0)
        assert ekf.P[0, 0] < p_init, "Kovaryans ölçümlerle azalmalı"

    def test_noisy_measurements_stay_bounded(self, ekf):
        import random
        ekf.initialize(400.0, -10.0)
        for _ in range(100):
            noisy_alt = 400.0 + random.gauss(0, 5)
            ekf.step(noisy_alt, 0.0)
        assert 380.0 < ekf.altitude < 420.0, "Gürültülü ölçümlerde filtre kararlı olmalı"
