from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
import aiohttp
import async_timeout
import asyncio
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_ITEM_ID, CONF_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,he;q=0.7',
    'lang': 'he',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
}

COOKIES = {
    'language': 'he',
    'store': 'shipment',
    'lang': 'he',
}

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the KSP Price Tracker component."""
    hass.data.setdefault(DOMAIN, {})
    
    async def handle_refresh(call: ServiceCall) -> None:
        """Handle the refresh service call."""
        item_id = call.data.get("item_id")
        
        # If item_id is provided, refresh only that item
        if item_id:
            for entry_id, coordinator in hass.data[DOMAIN].items():
                if coordinator.data and str(item_id) == str(coordinator.config_entry.data[CONF_ITEM_ID]):
                    await coordinator.async_refresh()
                    break
        # If no item_id, refresh all items
        else:
            for coordinator in hass.data[DOMAIN].values():
                await coordinator.async_refresh()

    # Register our custom service
    hass.services.async_register(
        DOMAIN,
        "refresh_price",
        handle_refresh,
        schema=vol.Schema({
            vol.Optional("item_id"): cv.string,
        })
    )
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up KSP Price Tracker from a config entry."""
    _LOGGER.debug("Starting async_setup_entry for %s", entry.entry_id)
    
    item_id = entry.data[CONF_ITEM_ID]
    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, 60)

    async def async_update_data():
        """Fetch data from KSP API."""
        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession(headers=HEADERS, cookie_jar=aiohttp.CookieJar()) as session:
                    # First set the cookies
                    for name, value in COOKIES.items():
                        session.cookie_jar.update_cookies({name: value})
                    
                    # Make the request with referer specific to the item
                    url = f"https://ksp.co.il/m_action/api/item/{item_id}?tt=0"
                    headers = {**HEADERS, 'referer': f'https://ksp.co.il/web/item/{item_id}'}
                    
                    _LOGGER.debug("Fetching data from: %s", url)
                    async with session.get(url, headers=headers) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"Error fetching data: {response.status}")
                        
                        data = await response.json()
                        
                        if 'result' not in data or 'data' not in data['result']:
                            raise UpdateFailed("Invalid data format received from API")
                            
                        return {
                            "price": data["result"]["data"]["price"],
                            "eilatPrice": data["result"]["data"]["eilatPrice"],
                            "name": data["result"]["data"]["name"],
                            "link": data["seo"]["myUrl"],
                        }
                        
        except asyncio.TimeoutError:
            raise UpdateFailed("Timeout while fetching data")
        except Exception as err:
            raise UpdateFailed(f"Error fetching KSP data: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"KSP price for item {item_id}",
        update_method=async_update_data,
        update_interval=timedelta(minutes=update_interval),
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady from err

    hass.data[DOMAIN][entry.entry_id] = coordinator
    coordinator.config_entry = entry  # Store the config entry for service calls
    
    await hass.config_entries.async_forward_entry_setup(entry, "sensor")
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading entry %s", entry.entry_id)
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True