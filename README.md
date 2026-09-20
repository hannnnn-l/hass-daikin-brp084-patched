# Daikin AC — BRP084 compressor state

HA core 2026.9.3's `daikin` integration (branch `upstream-baseline`) plus one
thing: the outdoor compressor state, read from DSIOT entity `e_2006`.

This is the slice intended for upstream. The pydaikin side lives on
`brp084-compressor-frequency` in <https://github.com/hannnnn-l/pydaikin>.

## What it changes

- pydaikin fills `values['cmpfreq']` from `e_2006/p_04` (little-endian uint16,
  Hz) and `values['compressor_running']` from `e_2006/p_01`
- **Compressor frequency** sensor now appears, and is enabled by default (core
  ships it disabled)
- **Compressor running** binary sensor (new `binary_sensor` platform)
- The climate entity reports `idle` instead of `heating`/`cooling` whenever the
  compressor is stopped — core derives that from the compressor frequency, so
  it starts working on its own

Nothing else differs from `upstream-baseline`: no diagnostic sensors, no
runtime sensor, no entity renames. Those live on `feature/ha-2026.9-port`.

## Install

HACS → custom repository `https://github.com/hannnnn-l/hass-daikin-brp084-patched`
→ version `v0.6.0-compressor` → restart. HA installs pydaikin from git on the
first start after install, so expect 30-60s of extra startup time.

Roll back by picking `v0.5.1-upstream` again, or `rm -rf
/config/custom_components/daikin` for the stock core integration.

## What to check on the unit

1. `sensor.*_compressor_frequency` exists and moves: 0 Hz when the compressor
   is stopped, tens of Hz while it modulates
2. `binary_sensor.*_compressor_running` follows it
3. The climate card shows "Idle" once the compressor stops in Heat mode
4. Nothing else regressed against `v0.5.1-upstream`

## Tests

```bash
uv venv -p 3.14 .venv
uv pip install pytest-homeassistant-custom-component==0.13.366 -e ../pydaikin
.venv/bin/python -m pytest
```

Seven end-to-end tests drive the integration against a simulated BRP084 unit,
including the idle-when-stopped case.

## Compatibility

- Requires Home Assistant 2026.9 or later.
- Verified on **Daikin FTXM71WVMA**, adapter firmware 3.12.3. Units that do not
  expose `e_2006` simply get no compressor entities.
