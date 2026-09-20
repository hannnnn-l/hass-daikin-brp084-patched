"""End-to-end tests for the compressor state, against a fake BRP084 unit.

The fake answers /dsiot/multireq the way a real unit does: op=2 reads return
the current state, op=3 writes update it. Every test goes through HA's config
entry setup, so it exercises the local pydaikin checkout as well.
"""

import json

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMockResponse,
)

from homeassistant.components.climate import HVACAction, HVACMode
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

HOST = "192.0.2.10"
MAC = "112233445566"
URL = f"http://{HOST}/dsiot/multireq"


class FakeUnit:
    """Minimal stateful BRP084 unit."""

    def __init__(self):
        self.writes = []
        # (entity path under dgc_status) -> {pn: pv}
        self.indoor = {
            "e_A002": {"p_01": "01"},  # power on
            "e_3001": {
                "p_01": "0100",  # heat
                "p_02": "32",  # cool setpoint 25
                "p_03": "2C",  # heat setpoint 22
                "p_1D": "2C",
                "p_09": "0A00",
                "p_0A": "0A00",
                "p_26": "0A00",
                "p_28": "0A00",
                **{f"p_{n}": "000000" for n in ("05", "06", "07", "08", "20", "21", "22", "23", "24", "25")},
            },
            "e_A00B": {"p_01": "18", "p_02": "3C"},  # room 24 °C, 60 %
            "e_A001": {"p_01": "414D564131374D585446"},
            "e_3003": {"p_0C": "32"},  # internal heat target 25 °C
            "e_2015_02": {"p_02": "3802", "p_03": "2803"},
        }
        self.outdoor = {
            "e_A00D": {"p_01": "10"},  # 8 °C
            "e_2006": {"p_01": "01", "p_04": "3400", "p_0B": "8C00", "p_25": "3200"},
            "e_2005": {"p_01": "E001"},
            "e_2008": {"p_01": "0700"},
        }

    @staticmethod
    def _tree(entities, root):
        return {
            "pn": "dgc_status",
            "pch": [
                {
                    "pn": root,
                    "pch": [
                        {"pn": e, "pch": [{"pn": k, "pv": v} for k, v in props.items()]}
                        for e, props in entities.items()
                    ],
                }
            ],
        }

    def status(self):
        return {
            "responses": [
                {"fr": "/dsiot/edge/adr_0100.dgc_status", "pc": self._tree(self.indoor, "e_1002"), "rsc": 2000},
                {"fr": "/dsiot/edge/adr_0200.dgc_status", "pc": self._tree(self.outdoor, "e_1003"), "rsc": 2000},
                {
                    "fr": "/dsiot/edge/adr_0100.i_power.week_power",
                    "pc": {
                        "pn": "week_power",
                        "pch": [
                            {"pn": "today_runtime", "pv": 95},
                            {"pn": "datas", "pv": [0, 0, 0, 0, 0, 0, 3100]},
                        ],
                    },
                    "rsc": 2000,
                },
                {
                    "fr": "/dsiot/edge.adp_i",
                    "pc": {"pn": "adp_i", "pch": [{"pn": "mac", "pv": MAC}, {"pn": "ver", "pv": "3_12_3"}]},
                    "rsc": 2000,
                },
            ]
        }

    def apply(self, payload):
        for req in payload["requests"]:
            target = self.indoor if "adr_0100" in req["to"] else self.outdoor
            for ent in req["pc"]["pch"]:  # e_1002 / e_1003
                for sub in ent["pch"]:
                    for prop in sub["pch"]:
                        target.setdefault(sub["pn"], {})[prop["pn"]] = prop["pv"]
                        self.writes.append((sub["pn"], prop["pn"], prop["pv"]))

    async def handle(self, method, url, data):
        payload = json.loads(data) if isinstance(data, (str, bytes)) else data
        if any(r.get("op") == 3 for r in payload["requests"]):
            self.apply(payload)
            body = {"responses": []}
        else:
            body = self.status()
        return AiohttpClientMockResponse(method, url, json=body)


@pytest.fixture
def unit(aioclient_mock, monkeypatch):
    # Skip pydaikin's UDP discovery lookup of the host.
    monkeypatch.setattr("pydaikin.factory.get_name", lambda _host: None)
    fake = FakeUnit()
    aioclient_mock.post(URL, side_effect=fake.handle)
    return fake


async def _setup(hass: HomeAssistant):
    entry = MockConfigEntry(domain="daikin", unique_id=MAC, data={CONF_HOST: HOST, "mac": MAC})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    registry = er.async_get(hass)
    ids = {
        e.unique_id: e.entity_id
        for e in er.async_entries_for_config_entry(registry, entry.entry_id)
    }
    return entry, ids


async def test_entities_created_with_values(hass: HomeAssistant, unit):
    """All patched entities exist, are enabled and report decoded values."""
    _, ids = await _setup(hass)

    expected = {
        f"{MAC}-compressor_frequency": "52.0",
        f"{MAC}-compressor_running": "on",
        f"{MAC}-energy_today": "3.1",
        f"{MAC}-inside_temperature": "24.0",
        f"{MAC}-outside_temperature": "8.0",
    }
    for unique_id, state in expected.items():
        assert unique_id in ids, f"missing entity {unique_id}"
        assert hass.states.get(ids[unique_id]).state == state, unique_id

    registry = er.async_get(hass)
    frequency = registry.async_get(ids[f"{MAC}-compressor_frequency"])
    assert frequency.disabled_by is None, "compressor frequency must be enabled"


async def test_device_info(hass: HomeAssistant, unit):
    """Device panel shows the decoded model and firmware version."""
    from homeassistant.helpers import device_registry as dr

    entry, _ = await _setup(hass)
    device = dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)[0]
    assert device.model == "AMVA17MXTF"
    assert device.sw_version == "3.12.3"


async def test_climate_reports_heat(hass: HomeAssistant, unit):
    """Heat mode shows as HEAT (not HEAT_COOL) and the action follows the compressor."""
    _, ids = await _setup(hass)
    state = hass.states.get(ids[MAC])
    assert state.state == HVACMode.HEAT
    assert state.attributes["hvac_action"] == HVACAction.HEATING
    assert state.attributes["temperature"] == 22.0


async def test_set_heat_mode_writes_mode(hass: HomeAssistant, unit):
    """Switching to HEAT from HA writes power on + mode 0100 on the wire."""
    unit.indoor["e_3001"]["p_01"] = "0200"  # start in cool
    _, ids = await _setup(hass)
    await hass.services.async_call(
        "climate", "set_hvac_mode", {"entity_id": ids[MAC], "hvac_mode": "heat"}, blocking=True
    )
    assert ("e_3001", "p_01", "0100") in unit.writes
    assert hass.states.get(ids[MAC]).state == HVACMode.HEAT


async def test_turn_on_from_off(hass: HomeAssistant, unit):
    """climate.turn_on on a powered-off unit sends a power-on write."""
    unit.indoor["e_A002"]["p_01"] = "00"
    _, ids = await _setup(hass)
    assert hass.states.get(ids[MAC]).state == HVACMode.OFF
    await hass.services.async_call("climate", "turn_on", {"entity_id": ids[MAC]}, blocking=True)
    assert ("e_A002", "p_01", "01") in unit.writes
    assert hass.states.get(ids[MAC]).state == HVACMode.HEAT


async def test_setpoint_on_off_unit_keeps_power(hass: HomeAssistant, unit):
    """Changing the setpoint while off must not switch the unit on."""
    unit.indoor["e_A002"]["p_01"] = "00"
    _, ids = await _setup(hass)
    await hass.services.async_call(
        "climate", "set_temperature", {"entity_id": ids[MAC], "temperature": 23}, blocking=True
    )
    assert not any(w[0] == "e_A002" for w in unit.writes)


async def test_idle_when_compressor_stopped(hass: HomeAssistant, unit):
    """With the compressor at 0 Hz the climate action is idle."""
    unit.outdoor["e_2006"].update({"p_01": "00", "p_04": "0000"})
    _, ids = await _setup(hass)
    assert hass.states.get(ids[MAC]).attributes["hvac_action"] == HVACAction.IDLE
    assert hass.states.get(ids[f"{MAC}-compressor_running"]).state == "off"
