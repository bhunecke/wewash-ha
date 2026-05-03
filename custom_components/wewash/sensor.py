from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from datetime import datetime, timezone
from . import DOMAIN

SENSORS = [
    ("availableWashers", "Available Washers", "mdi:washing-machine"),
    ("availableDryers",  "Available Dryers",  "mdi:tumble-dryer"),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    if coordinator.data:
        for room in coordinator.data.get("laundry_rooms", []):
            for key, name, icon in SENSORS:
                entities.append(WeWashSensor(coordinator, room, key, name, icon))
        
        entities.append(WeWashReservationStatusSensor(coordinator, entry.entry_id))
        entities.append(WeWashReservationApplianceSensor(coordinator, entry.entry_id))
        entities.append(WeWashReservationTimeSensor(coordinator, entry.entry_id))
        entities.append(WeWashReservationTimeoutSensor(coordinator, entry.entry_id))
        entities.append(WeWashReservationPriceSensor(coordinator, entry.entry_id))
        entities.append(WeWashReservationRoomSensor(coordinator, entry.entry_id))

    async_add_entities(entities)


class WeWashReservationBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry_id}_reservation")},
            name="Reservation",
            manufacturer="WeWash",
            model="Reservation",
        )

    def _get_active_reservation(self):
        if not self.coordinator.data or not self.coordinator.data.get("reservations"):
            return None
        return self.coordinator.data["reservations"][0]

class WeWashReservationStatusSensor(WeWashReservationBaseSensor):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator, entry_id)
        self._attr_name = "Reservation Active"
        self._attr_icon = "mdi:ticket-confirmation"
        self._attr_unique_id = f"wewash_{entry_id}_reservation_status"

    @property
    def native_value(self):
        res = self._get_active_reservation()
        return res.get("status").lower() if res and res.get("status") else None

class WeWashReservationApplianceSensor(WeWashReservationBaseSensor):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator, entry_id)
        self._attr_name = "Appliance Name"
        self._attr_icon = "mdi:washing-machine"
        self._attr_unique_id = f"wewash_{entry_id}_reservation_appliance"

    @property
    def native_value(self):
        res = self._get_active_reservation()
        return res.get("applianceShortName") if res else None

class WeWashReservationTimeSensor(WeWashReservationBaseSensor):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator, entry_id)
        self._attr_name = "Status Changed"
        self._attr_icon = "mdi:clock-time-four"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_unique_id = f"wewash_{entry_id}_reservation_time"

    @property
    def native_value(self):
        res = self._get_active_reservation()
        if not res or not res.get("statusChangedTimestamp"):
            return None
        return datetime.fromtimestamp(res["statusChangedTimestamp"] / 1000, tz=timezone.utc)

class WeWashReservationTimeoutSensor(WeWashReservationBaseSensor):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator, entry_id)
        self._attr_name = "Status Timeout"
        self._attr_icon = "mdi:clock-alert"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_unique_id = f"wewash_{entry_id}_reservation_timeout"

    @property
    def native_value(self):
        res = self._get_active_reservation()
        if not res or not res.get("timeoutTimestamp"):
            return None
        return datetime.fromtimestamp(res["timeoutTimestamp"] / 1000, tz=timezone.utc)

class WeWashReservationPriceSensor(WeWashReservationBaseSensor):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator, entry_id)
        self._attr_name = "Reservation Price"
        self._attr_icon = "mdi:cash"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_unique_id = f"wewash_{entry_id}_reservation_price"

    @property
    def native_value(self):
        res = self._get_active_reservation()
        return res.get("price") if res else None

    @property
    def native_unit_of_measurement(self):
        res = self._get_active_reservation()
        return res.get("currency") if res else None

class WeWashReservationRoomSensor(WeWashReservationBaseSensor):
    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator, entry_id)
        self._attr_name = "Laundry Room"
        self._attr_icon = "mdi:map-marker"
        self._attr_unique_id = f"wewash_{entry_id}_reservation_room"

    @property
    def native_value(self):
        res = self._get_active_reservation()
        if res and res.get("laundryRoom"):
            return res["laundryRoom"].get("name")
        return None


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
        if not self.coordinator.data or not self.coordinator.data.get("laundry_rooms"):
            return None
        room = next(
            (r for r in self.coordinator.data["laundry_rooms"] if r["id"] == self._room_id),
            None,
        )
        if room is None:
            return None
        return room["serviceAvailability"].get(self._key)