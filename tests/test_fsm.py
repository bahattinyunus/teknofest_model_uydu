"""
test_fsm.py – FlightStateMachine birim testleri
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from fsm import FlightStateMachine, FlightState


@pytest.fixture
def fsm():
    return FlightStateMachine()


class TestFlightStateMachine:

    def test_initial_state_is_idle(self, fsm):
        assert fsm.state == FlightState.IDLE

    def test_idle_to_ascent_transition(self, fsm):
        state = fsm.update(altitude_m=15.0, vertical_speed_mps=3.0, gps_fix=True)
        assert state == FlightState.ASCENT, "GPS kilidi + irtifa sağlandığında ASCENT'e geçmeli"

    def test_no_transition_without_gps(self, fsm):
        state = fsm.update(altitude_m=20.0, vertical_speed_mps=3.0, gps_fix=False)
        assert state == FlightState.IDLE, "GPS yokken IDLE kalmalı"

    def test_ascent_to_descent(self, fsm):
        fsm.update(15.0, 3.0, True)   # → ASCENT
        state = fsm.update(300.0, -2.0, True)   # hız negatif → DESCENT
        assert state == FlightState.DESCENT

    def test_descent_to_separation(self, fsm):
        fsm.update(15.0,  3.0, True)   # ASCENT
        fsm.update(300.0, -2.0, True)  # DESCENT
        state = fsm.update(399.0, -10.0, True)  # irtifa ≤ 400
        assert state == FlightState.SEPARATION

    def test_separation_to_payload_after_delay(self, fsm):
        import time
        fsm.update(15.0,  3.0,  True)
        fsm.update(300.0, -2.0, True)
        fsm.update(399.0, -10.0, True)   # → SEPARATION
        # Süre geçmeden PAYLOAD'a geçmemeli
        fsm.state_entry_time -= 3.0      # 3 saniye hızlı ileri
        state = fsm.update(350.0, -8.0, True)
        assert state == FlightState.PAYLOAD

    def test_payload_to_recovery(self, fsm):
        # FSM'i doğrudan PAYLOAD durumuna getir
        fsm.state            = FlightState.PAYLOAD
        fsm.separation_done  = True
        state = fsm.update(altitude_m=2.0, vertical_speed_mps=0.1, gps_fix=True)
        assert state == FlightState.RECOVERY

    def test_recovery_is_terminal(self, fsm):
        fsm.state = FlightState.RECOVERY
        state = fsm.update(0.0, 0.0, True)
        assert state == FlightState.RECOVERY

    def test_max_altitude_tracking(self, fsm):
        for alt in [50, 200, 650, 700, 400]:
            fsm.update(alt, 5.0, True)
        assert fsm.max_altitude_m == 700.0

    def test_log_not_empty_after_transitions(self, fsm):
        fsm.update(15.0, 3.0, True)
        fsm.update(300.0, -2.0, True)
        assert len(fsm.get_log()) > 0

    def test_status_dict_keys(self, fsm):
        status = fsm.get_status_dict()
        for key in ("state_id", "state_name", "max_alt_m", "sep_done", "time_in_s"):
            assert key in status
