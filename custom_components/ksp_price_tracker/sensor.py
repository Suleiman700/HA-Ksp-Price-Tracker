import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.helpers.entity import EntityCategory
from typing import Any, Dict

from .const import DOMAIN, CONF_ITEM_ID

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    item_id = config_entry.data[CONF_ITEM_ID]

    entities = [
        KSPPriceSensor(coordinator, config_entry.data[CONF_ITEM_ID], "name"),
        KSPPriceSensor(coordinator, config_entry.data[CONF_ITEM_ID], "price"),
        KSPPriceSensor(coordinator, config_entry.data[CONF_ITEM_ID], "eilat_price"),
        KSPPriceSensor(coordinator, config_entry.data[CONF_ITEM_ID], "link"),
    ]
    
    async_add_entities(entities, False)

class KSPPriceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a KSP Price Sensor."""
    
    def __init__(self, coordinator, item_id, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._item_id = item_id
        self._sensor_type = sensor_type
        self._attr_unique_id = f"ksp_{sensor_type}_{item_id}"

        # Set different names and units based on sensor type
        # if sensor_type == "price":
        #     self._attr_name = f"KSP Price {item_id}"
        # else:
        #     self._attr_name = f"KSP Eilat Price {item_id}"
            
        # Set sensor name based on the sensor type, E.g. KSP Name <ITEM_ID> 
        if self._sensor_type == "price":
            self._attr_name = f"KSP Price {item_id}"
        elif self._sensor_type == "eilat_price":
            self._attr_name = f"KSP Eilat Price {item_id}"
        elif self._sensor_type == "name":
            self._attr_name = f"KSP Name {item_id}"
        elif self._sensor_type == "link":
            self._attr_name = f"KSP Link {item_id}"
        else:
            self._attr_name = f"KSP {sensor_type.replace('_', ' ').title()} {item_id}"


        # Set the unit of measurement only for price-related sensors
        if self._sensor_type in ["price", "eilat_price"]:
            self._attr_native_unit_of_measurement = "ILS"
        else:
            self._attr_native_unit_of_measurement = None  # No unit for 'name' sensor

        # Set the icon based on the sensor type
        if self._sensor_type == "price":
            self._attr_icon = "mdi:currency-ils"  # Icon for price in ILS
        elif self._sensor_type == "eilat_price":
            self._attr_icon = "mdi:currency-ils"  # Icon for price in USD
        elif self._sensor_type == "name":
            self._attr_icon = "mdi:shopping"  # Icon for product name
        elif self._sensor_type == "link":
            self._attr_icon = "mdi:link"  # Icon for product name

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional attributes."""
        if self.coordinator.data is None:
            return {}
            
        return {
            "item_name": self.coordinator.data.get("name", ""),
            "item_id": self._item_id,
            "last_update": self.coordinator.last_update_success,
        }

    @property
    def native_value(self):
        """Return the current price."""
        if self.coordinator.data is None:
            return None
            
        if self._sensor_type == "price":
            return self.coordinator.data.get("price")
        elif self._sensor_type == "eilat_price":
            return self.coordinator.data.get("eilatPrice")
        elif self._sensor_type == "name":
            return self.coordinator.data.get("name")  # Fetch product name
        elif self._sensor_type == "link":
            return self.coordinator.data.get("link")  # Fetch product name
