# Daikin AC — BRP084 patched

Home Assistant custom component for Daikin AC units running the **BRP084** DSIOT API
(firmware 2.8.0+ / 3.x, typically FTXM-R / FTXM-W / FTXA-R models).

This is HA core's `daikin` integration (synced to HA 2026.9.3) pinned to a
**fork of `pydaikin`** (upstream 2.20.0 plus FTXM71 diagnostics).

Branch layout, each one sitting on the previous:

1. `upstream-baseline` — core 2026.9.3 verbatim, pydaikin 2.20.0
2. `feature/compressor` — the compressor state, the slice proposed upstream
   as [pydaikin#163]
3. `feature/ha-2026.9-port` — this branch, everything else, local-only

[pydaikin#163]: https://github.com/fredrike/pydaikin/pull/163

The original bug fixes (HEAT mode from HA, power switch, energy sensors,
model/firmware in the device panel) are now in upstream pydaikin
([pydaikin#81], [pydaikin#124]); this build only adds what upstream lacks.

## Extra entities in this build

- **Compressor frequency** (Hz, enabled by default) and **Compressor running**
  binary sensor, from outdoor-unit entity `e_2006`. The climate entity also
  reports `idle` while the compressor is stopped.
- **Runtime today** (minutes).
- Diagnostics: outdoor refrigerant temperature, expansion valve position,
  outdoor fan step, internal heating target (`e_3003/p_0C`).
- Dropped from core: cool/heat energy (always empty on BRP084), the duplicate
  "total energy today" sensor, and "Target humidity" (core reads the measured
  humidity into it).

[pydaikin#81]: https://github.com/fredrike/pydaikin/issues/81
[pydaikin#124]: https://github.com/fredrike/pydaikin/issues/124

## Tests

```bash
uv venv -p 3.14 .venv
uv pip install pytest-homeassistant-custom-component==0.13.366 -e ../pydaikin
.venv/bin/python -m pytest
```

The tests run the integration against a fake BRP084 unit.

## Install

### Via HACS (recommended)

1. HACS → Integrations → three-dot menu → **Custom repositories**
2. Repository: `https://github.com/hannnnn-l/hass-daikin-brp084-patched`
   Type: **Integration**
3. Install it, choose version `v0.7.0-port`, then **restart Home Assistant**.

To compare against plain upstream instead, choose `v0.5.1-upstream`: the same
HA core 2026.9.3 integration with no patches, pinned to pydaikin 2.20.0
(branch `upstream-baseline`).

### Manual

```bash
# On your HA host (SSH / Samba / whatever you use)
cd /config
git clone -b feature/ha-2026.9-port https://github.com/hannnnn-l/hass-daikin-brp084-patched.git /tmp/daikin-patched
mkdir -p custom_components
cp -r /tmp/daikin-patched/custom_components/daikin custom_components/
# Restart HA
```

On first start after install, HA pip-installs the patched `pydaikin` from the
fork (requires `git` on the host — HA OS ships with it). Expect 30–60s of extra
startup time on the RPi.

## Compatibility

- Tested on **Daikin FTXM71WVMA** (firmware 3.12.3).
- Expected to work on any BRP084 unit that exposes outdoor entity `e_2006`
  (most FTXM-R / FTXM-W / FTXA-R series). On units that don't expose `e_2006`,
  the compressor sensor simply won't appear — other fixes still apply.
- Requires Home Assistant 2026.9 or later (the integration code is synced to 2026.9.3).

## Rolling back

```bash
rm -rf /config/custom_components/daikin
# Restart HA — falls back to core integration with stock pydaikin
```

## Upstream

The pydaikin side lives on `feature/brp084-port` in
<https://github.com/hannnnn-l/pydaikin> (upstream v2.20.0 + the FTXM71
diagnostics). Once those land upstream and HA core bumps its pin, this custom
component becomes obsolete — uninstall it and use the core integration.

## License

Same as pydaikin / Home Assistant core (Apache-2.0 / MIT respectively).
