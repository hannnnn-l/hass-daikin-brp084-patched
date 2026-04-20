"""Support for Daikin AC binary sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from pydaikin.daikin_base import Appliance

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import ATTR_COMPRESSOR_RUNNING
from .coordinator import DaikinConfigEntry, DaikinCoordinator
from .entity import DaikinEntity


@dataclass(frozen=True, kw_only=True)
class DaikinBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Daikin binary sensor entity."""

    value_func: Callable[[Appliance], bool | None]


BINARY_SENSOR_TYPES: tuple[DaikinBinarySensorEntityDescription, ...] = (
    DaikinBinarySensorEntityDescription(
        key=ATTR_COMPRESSOR_RUNNING,
        translation_key="compressor_running",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_func=lambda device: (
            None
            if device.values.get('compressor_running') is None
            else device.values.get('compressor_running') == '1'
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DaikinConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Daikin binary sensors based on config_entry."""
    daikin_api = entry.runtime_data
    entities: list[DaikinBinarySensor] = []

    if daikin_api.device.values.get('compressor_running') is not None:
        entities.append(
            DaikinBinarySensor(
                daikin_api,
                BINARY_SENSOR_TYPES[0],
            )
        )

    async_add_entities(entities)


class DaikinBinarySensor(DaikinEntity, BinarySensorEntity):
    """Representation of a Daikin binary sensor."""

    entity_description: DaikinBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: DaikinCoordinator,
        description: DaikinBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self.device.mac}-{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return the current state."""
        return self.entity_description.value_func(self.device)
