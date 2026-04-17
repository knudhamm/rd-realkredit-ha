"""Realkredit Danmark integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, API_URL, SCAN_INTERVAL_MINUTES

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Sæt integration op fra config entry."""
    coordinator = RDDataCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Fjern integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class RDDataCoordinator(DataUpdateCoordinator):
    """Henter data fra RD API og deler med alle sensorer."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> list[dict]:
        """Hent data fra RD API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    resp.raise_for_status()
                    return await resp.json(content_type=None)
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Fejl ved hentning af RD data: {err}") from err

