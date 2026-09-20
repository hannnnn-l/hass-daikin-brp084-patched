# Daikin AC — upstream baseline

Home Assistant's own `daikin` integration, copied verbatim from **HA core 2026.9.3**
and pinned to **pydaikin 2.20.0** (upstream release, 2026-09-18).

There are no patches in this branch. Its only purpose is to test the current
upstream code before HA core ships it: HA 2026.9.x still bundles pydaikin 2.19.1.

Use it to see what BRP084 support looks like without any local changes, then
compare against the `feature/ha-2026.9-port` branch, which adds the FTXM71
compressor and refrigerant-circuit entities on top of the same base.

## What to expect on a BRP084 unit

Works (all fixed upstream during 2026):
- switching to Heat from the climate card
- the power switch / `climate.turn_on`
- today's energy and the estimated power draw
- model and firmware version in the device panel

Not available:
- compressor frequency — upstream does not read it on BRP084, so the sensor is
  never created, and the climate entity can never report `idle`
- compressor running, runtime today, and the refrigerant-circuit diagnostics

Present but not useful:
- "Target humidity" repeats the measured humidity (an HA core bug)
- "Cool/Heat energy" have no data on BRP084 (disabled by default)

pydaikin 2.20.0 also supports econo, powerful, comfort airflow, outdoor quiet,
vane position, dry comfort offset and compressor temperature on BRP084, but HA
core does not expose any of them as entities yet.

## Install

### Via HACS

1. HACS → three-dot menu → **Custom repositories**
2. Repository: `https://github.com/hannnnn-l/hass-daikin-brp084-patched`, type **Integration**
3. Install, pick version `v0.5.0-upstream`, then restart Home Assistant.

### Manual

```bash
cd /config
git clone -b upstream-baseline https://github.com/hannnnn-l/hass-daikin-brp084-patched.git /tmp/daikin-upstream
mkdir -p custom_components
cp -r /tmp/daikin-upstream/custom_components/daikin custom_components/
# Restart HA
```

HA installs `pydaikin==2.20.0` from PyPI on the first start after install.

## Rolling back

```bash
rm -rf /config/custom_components/daikin
# Restart HA — back to the core integration with its own pinned pydaikin
```

## Compatibility

- Requires Home Assistant 2026.9 or later (the integration code is from 2026.9.3).
- Tested on **Daikin FTXM71WVMA** (adapter firmware 3.12.3).
