"""Support for Daikin AC binary sensors."""

from __future__ import annotations

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

COMPRESSOR_RUNNING = BinarySensorEntityDescription(
    key=ATTR_COMPRESSOR_RUNNING,
    translation_key="compressor_running",
    device_class=BinarySensorDeviceClass.RUNNING,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DaikinConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Daikin binary sensors based on config_entry."""
    coordinator = entry.runtime_data
    if getattr(coordinator.device, "support_compressor_running", False):
        async_add_entities([DaikinCompressorRunning(coordinator)])


class DaikinCompressorRunning(DaikinEntity, BinarySensorEntity):
    """Whether the outdoor compressor is currently running."""

    entity_description = COMPRESSOR_RUNNING

    def __init__(self, coordinator: DaikinCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self.device.mac}-{ATTR_COMPRESSOR_RUNNING}"

    @property
    def is_on(self) -> bool | None:
        """Return True while the compressor runs."""
        return self.device.compressor_running
