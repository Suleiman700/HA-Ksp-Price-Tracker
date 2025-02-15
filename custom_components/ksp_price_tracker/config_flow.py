import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_ITEM_ID, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL

class KSPPriceTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            return self.async_create_entry(
                title=f"KSP Item {user_input[CONF_ITEM_ID]}",
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ITEM_ID): str,
                vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int
            }),
            errors=errors,
        )