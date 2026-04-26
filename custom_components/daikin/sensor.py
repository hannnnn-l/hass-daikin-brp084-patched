"""Support for Daikin AC sensors."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import override

from pydaikin.daikin_base import Appliance

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    ATTR_COMPRESSOR_FREQUENCY,
    ATTR_COMPRESSOR_RUNTIME_TODAY,
    ATTR_COOL_ENERGY,
    ATTR_EEV_POSITION,
    ATTR_ENERGY_TODAY,
    ATTR_HEAT_ENERGY,
    ATTR_HUMIDITY,
    ATTR_INDOOR_COIL_INLET_TEMP,
    ATTR_INDOOR_COIL_OUTLET_TEMP,
    ATTR_INSIDE_TEMPERATURE,
    ATTR_INTERNAL_HEAT_TARGET,
    ATTR_OUTDOOR_FAN_STEP,
    ATTR_OUTDOOR_HX_TEMP,
    ATTR_OUTDOOR_REFRIGERANT_TEMP,
    ATTR_OUTSIDE_TEMPERATURE,
    ATTR_TARGET_HUMIDITY,
    ATTR_TOTAL_ENERGY_TODAY,
    ATTR_TOTAL_POWER,
)
from .coordinator import DaikinConfigEntry, DaikinCoordinator
from .entity import DaikinEntity


@dataclass(frozen=True, kw_only=True)
class DaikinSensorEntityDescription(SensorEntityDescription):
    """Describes Daikin sensor entity."""

    value_func: Callable[[Appliance], float | None]


SENSOR_TYPES: tuple[DaikinSensorEntityDescription, ...] = (
    DaikinSensorEntityDescription(
        key=ATTR_INSIDE_TEMPERATURE,
        translation_key="inside_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_func=lambda device: device.inside_temperature,
    ),
    DaikinSensorEntityDescription(
        key=ATTR_OUTSIDE_TEMPERATURE,
        translation_key="outside_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_func=lambda device: device.outside_temperature,
    ),
    DaikinSensorEntityDescription(
        key=ATTR_HUMIDITY,
        translation_key="indoor_humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_func=lambda device: device.humidity,
    ),
    DaikinSensorEntityDescription(
        key=ATTR_TARGET_HUMIDITY,
        translation_key="target_humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_func=lambda device: device.humidity,
    ),
    DaikinSensorEntityDescription(
        key=ATTR_TOTAL_POWER,
        translation_key="compressor_estimated_power_consumption",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        value_func=lambda device: round(device.current_total_power_consumption, 2),
    ),
    DaikinSensorEntityDescription(
        key=ATTR_COOL_ENERGY,
        translation_key="cool_energy_consumption",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        entity_registry_enabled_default=False,
        value_func=lambda device: round(device.last_hour_cool_energy_consumption, 2),
    ),
    DaikinSensorEntityDescription(
        key=ATTR_HEAT_ENERGY,
        translation_key="heat_energy_consumption",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        entity_registry_enabled_default=False,
        value_func=lambda device: round(device.last_hour_heat_energy_consumption, 2),
    ),
    DaikinSensorEntityDescription(
        key=ATTR_ENERGY_TODAY,
        translation_key="energy_consumption",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_func=lambda device: round(device.today_energy_consumption, 2),
    ),
    DaikinSensorEntityDescription(
        key=ATTR_COMPRESSOR_FREQUENCY,
        translation_key="compressor_frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        value_func=lambda device: device.compressor_frequency,
    ),
    DaikinSensorEntityDescription(
        key=ATTR_TOTAL_ENERGY_TODAY,
        translation_key="compressor_energy_consumption",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        entity_registry_enabled_default=False,
        value_func=lambda device: round(device.today_total_energy_consumption, 2),
    ),
    DaikinSensorEntityDescription(
        key=ATTR_COMPRESSOR_RUNTIME_TODAY,
        translation_key="compressor_runtime_today",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        value_func=lambda device: device.values.get('today_runtime'),
    ),
    # ----- Diagnostic sensors (BRP084-only, disabled by default) -----
    DaikinSensorEntityDescription(
        key=ATTR_OUTDOOR_REFRIGERANT_TEMP,
        translation_key="outdoor_refrigerant_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
        value_func=lambda device: float(device.values.get('outdoor_refrigerant_temp')),
    ),
    DaikinSensorEntityDescription(
        key=ATTR_OUTDOOR_HX_TEMP,
        translation_key="outdoor_hx_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
        value_func=lambda device: float(device.values.get('outdoor_hx_temp')),
    ),
    DaikinSensorEntityDescription(
        key=ATTR_INDOOR_COIL_INLET_TEMP,
        translation_key="indoor_coil_inlet_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
        value_func=lambda device: float(device.values.get('indoor_coil_inlet_temp')),
    ),
    DaikinSensorEntityDescription(
        key=ATTR_INDOOR_COIL_OUTLET_TEMP,
        translation_key="indoor_coil_outlet_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
        value_func=lambda device: float(device.values.get('indoor_coil_outlet_temp')),
    ),
    DaikinSensorEntityDescription(
        key=ATTR_EEV_POSITION,
        translation_key="eev_position",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_func=lambda device: int(device.values.get('eev_position')),
    ),
    DaikinSensorEntityDescription(
        key=ATTR_OUTDOOR_FAN_STEP,
        translation_key="outdoor_fan_step",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_func=lambda device: int(device.values.get('outdoor_fan_step')),
    ),
    # Firmware's internal heating target (user setpoint + 3-4°C compensation).
    # Disabled by default — primarily a diagnostic for proving the firmware's
    # heating-overshoot bias. Compare against the user setpoint and actual
    # room temp to see how much extra the unit silently aims for.
    DaikinSensorEntityDescription(
        key=ATTR_INTERNAL_HEAT_TARGET,
        translation_key="internal_heat_target",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=False,
        value_func=lambda device: float(device.values.get('internal_heat_target')),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DaikinConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Daikin climate based on config_entry."""
    daikin_api = entry.runtime_data
    sensors = [ATTR_INSIDE_TEMPERATURE]
    if daikin_api.device.support_outside_temperature:
        sensors.append(ATTR_OUTSIDE_TEMPERATURE)
    if daikin_api.device.support_energy_consumption:
        sensors.append(ATTR_ENERGY_TODAY)
        sensors.append(ATTR_COOL_ENERGY)
        sensors.append(ATTR_HEAT_ENERGY)
        sensors.append(ATTR_TOTAL_POWER)
        # ATTR_TOTAL_ENERGY_TODAY intentionally skipped on BRP084 — with the
        # today_energy_consumption fallback we added, it would be a duplicate
        # of ATTR_ENERGY_TODAY (both resolve to the same `datas[-1]/1000`).
    if daikin_api.device.support_humidity:
        sensors.append(ATTR_HUMIDITY)
        # HA core also adds ATTR_TARGET_HUMIDITY here, but its value_func reads
        # device.humidity (not target_humidity) — so on units without humidity
        # control (most FTXM-series) it silently duplicates the measured value
        # under a "Target humidity" label. Omit it to avoid the confusion.
    if daikin_api.device.support_compressor_frequency:
        sensors.append(ATTR_COMPRESSOR_FREQUENCY)
    if daikin_api.device.values.get('today_runtime') is not None:
        sensors.append(ATTR_COMPRESSOR_RUNTIME_TODAY)
    # Diagnostic sensors — only register when their value is populated
    # (units that don't expose the underlying entity simply skip them)
    for values_key, attr_key in (
        ('outdoor_refrigerant_temp', ATTR_OUTDOOR_REFRIGERANT_TEMP),
        ('outdoor_hx_temp',          ATTR_OUTDOOR_HX_TEMP),
        ('indoor_coil_inlet_temp',   ATTR_INDOOR_COIL_INLET_TEMP),
        ('indoor_coil_outlet_temp',  ATTR_INDOOR_COIL_OUTLET_TEMP),
        ('eev_position',             ATTR_EEV_POSITION),
        ('outdoor_fan_step',         ATTR_OUTDOOR_FAN_STEP),
        ('internal_heat_target',     ATTR_INTERNAL_HEAT_TARGET),
    ):
        if daikin_api.device.values.get(values_key) is not None:
            sensors.append(attr_key)

    entities = [
        DaikinSensor(daikin_api, description)
        for description in SENSOR_TYPES
        if description.key in sensors
    ]
    async_add_entities(entities)


class DaikinSensor(DaikinEntity, SensorEntity):
    """Representation of a Sensor."""

    entity_description: DaikinSensorEntityDescription

    def __init__(
        self, coordinator: DaikinCoordinator, description: DaikinSensorEntityDescription
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self.device.mac}-{description.key}"

    @property
    @override
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.entity_description.value_func(self.device)
