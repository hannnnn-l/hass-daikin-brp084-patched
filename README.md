# Daikin AC — upstream baseline

Home Assistant's own `daikin` integration, copied verbatim from **HA core 2026.9.3**
and pinned to **pydaikin 2.20.0** (upstream release, 2026-09-18).

This is HA core's `daikin` integration (synced to HA 2026.9.3) pinned to a
**fork of `pydaikin`** (upstream 2.20.0 plus FTXM71 diagnostics).

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

### Via HACS

1. HACS → Integrations → three-dot menu → **Custom repositories**
2. Repository: `https://github.com/hannnnn-l/hass-daikin-brp084-patched`
   Type: **Integration**
3. Install "Daikin AC (BRP084 patched)", then **restart Home Assistant**.

### Manual

```bash
cd /config
git clone https://github.com/hannnnn-l/hass-daikin-brp084-patched.git /tmp/daikin-patched
mkdir -p custom_components
cp -r /tmp/daikin-upstream/custom_components/daikin custom_components/
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
# Restart HA — back to the core integration with its own pinned pydaikin
```

## Compatibility

- Requires Home Assistant 2026.9 or later (the integration code is from 2026.9.3).
- Tested on **Daikin FTXM71WVMA** (adapter firmware 3.12.3).
