"""Constants for Daikin."""

DOMAIN = "daikin"

ATTR_TARGET_TEMPERATURE = "target_temperature"
ATTR_INSIDE_TEMPERATURE = "inside_temperature"
ATTR_OUTSIDE_TEMPERATURE = "outside_temperature"

ATTR_TARGET_HUMIDITY = "target_humidity"
ATTR_HUMIDITY = "humidity"

ATTR_COMPRESSOR_FREQUENCY = "compressor_frequency"
ATTR_COMPRESSOR_RUNNING = "compressor_running"
ATTR_COMPRESSOR_RUNTIME_TODAY = "compressor_runtime_today"

# Diagnostic sensors (BRP084-only, all disabled by default in HA)
ATTR_OUTDOOR_REFRIGERANT_TEMP = "outdoor_refrigerant_temp"
ATTR_OUTDOOR_HX_TEMP = "outdoor_hx_temp"
ATTR_EEV_POSITION = "eev_position"
ATTR_OUTDOOR_FAN_STEP = "outdoor_fan_step"
ATTR_INDOOR_COIL_INLET_TEMP = "indoor_coil_inlet_temp"
ATTR_INDOOR_COIL_OUTLET_TEMP = "indoor_coil_outlet_temp"
ATTR_INTERNAL_HEAT_TARGET = "internal_heat_target"

ATTR_ENERGY_TODAY = "energy_today"
ATTR_COOL_ENERGY = "cool_energy"
ATTR_HEAT_ENERGY = "heat_energy"

ATTR_TOTAL_POWER = "total_power"
ATTR_TOTAL_ENERGY_TODAY = "total_energy_today"

ATTR_STATE_ON = "on"
ATTR_STATE_OFF = "off"

KEY_MAC = "mac"
KEY_IP = "ip"

ZONE_NAME_UNCONFIGURED = "-"

TIMEOUT_SEC = 120
