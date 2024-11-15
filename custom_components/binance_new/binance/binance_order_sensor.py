from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from ..constants import  DEFAULT_COIN_ICON, ATTRIBUTION,  CURRENCY_ICONS, QUOTE_ASSETS
import logging
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)
class BinanceOrderSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Binance Order Sensor."""

    def __init__(self, coordinator, name, order):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = f"{name} {order['symbol']} Order"
        self._symbol = order["symbol"]
        self._state = order["all_orders"]
        self._unit_of_measurement = self._determine_unit(order["symbol"])
        self._attr_unique_id = f"{name}_{order['symbol']}_order"
        self._attr_device_class = "monetary"  # Change to an appropriate device class
        self._coordinator = coordinator
        self._attr_device_info = coordinator.device_info_orders

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return CURRENCY_ICONS.get(self._unit_of_measurement, DEFAULT_COIN_ICON)

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }

    def _determine_unit(self, symbol):
        """Determine the unit of measurement based on the symbol."""
        for quote_asset in QUOTE_ASSETS:
            if symbol.endswith(quote_asset):
                return quote_asset
        return None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        new_order = self._coordinator.data.get("orders", {}).get(self._symbol, {}).get("all_orders")

        if new_order:
            self._state = new_order
        else:
            _LOGGER.error(f"No new order data found for {self._symbol} in {self._name}.")

        self.async_write_ha_state()


    @property
    def is_valid(self):
        """Validate sensor data."""
        try:
            return isinstance(self._state, str) and self._unit_of_measurement is not None
        except Exception as e:
            _LOGGER.error(f"Invalid data for sensor {self._name}: {e}")
            return False
