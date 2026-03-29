from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from . import DOMAIN

SENSORS = [
    ("availableWashers", "Available Washers", "mdi:washing-machine"),
    ("availableDryers",  "Available Dryers",  "mdi:tumble-dryer"),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    if coordinator.data:
        for room in coordinator.data:
            for key, name, icon in SENSORS:
                entities.append(WeWashSensor(coordinator, room, key, name, icon))

    async_add_entities(entities)


class WeWashSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, room, key, name, icon):
        super().__init__(coordinator)
        self._room_id = room["id"]
        self._key = key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"wewash_{self._room_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(self._room_id))},
            name=room["name"],
            manufacturer="WeWash",
            model="Laundry Room",
        )

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        room = next(
            (r for r in self.coordinator.data if r["id"] == self._room_id),
            None,
        )
        if room is None:
            return None
        return room["serviceAvailability"].get(self._key)