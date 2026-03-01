"""
test_telemetry.py – TelemetryHandler birim testleri
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from telemetry import TelemetryHandler


@pytest.fixture
def handler():
    return TelemetryHandler()


class TestTelemetryHandler:

    def test_read_packet_simulation_returns_string(self, handler):
        packet = handler.read_packet_simulation()
        assert isinstance(packet, str), "Paket str türünde olmalı"

    def test_packet_has_six_fields(self, handler):
        packet = handler.read_packet_simulation()
        fields = packet.split(",")
        assert len(fields) == 6, f"6 alan bekleniyor, {len(fields)} bulundu"

    def test_parse_returns_dict_with_all_keys(self, handler):
        packet = handler.read_packet_simulation()
        parsed = handler.parse_packet(packet)
        assert "error" not in parsed
        for key in ("team_id", "timestamp", "pressure", "altitude", "speed", "battery"):
            assert key in parsed, f"'{key}' anahtarı eksik"

    def test_altitude_in_valid_range(self, handler):
        for _ in range(20):
            p = handler.parse_packet(handler.read_packet_simulation())
            assert 0.0 <= p["altitude"] <= 700.0, \
                f"İrtifa geçersiz aralıkta: {p['altitude']}"

    def test_battery_in_valid_range(self, handler):
        for _ in range(20):
            p = handler.parse_packet(handler.read_packet_simulation())
            assert 10.0 <= p["battery"] <= 12.6, \
                f"Voltaj geçersiz aralıkta: {p['battery']}"

    def test_parse_malformed_packet_returns_error(self, handler):
        result = handler.parse_packet("bad,data")
        assert "error" in result, "Hatalı paket 'error' döndürmeli"

    def test_team_id_is_integer(self, handler):
        p = handler.parse_packet(handler.read_packet_simulation())
        assert isinstance(p["team_id"], int)

    def test_pressure_in_valid_range(self, handler):
        for _ in range(20):
            p = handler.parse_packet(handler.read_packet_simulation())
            assert 950.0 <= p["pressure"] <= 1050.0, \
                f"Basınç geçersiz: {p['pressure']}"
