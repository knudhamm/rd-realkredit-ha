"""Config flow — vælg obligationer via UI dropdown."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    SelectOptionDict,
)

from .const import DOMAIN, API_URL, LOAN_TYPE_NAMES

_LOGGER = logging.getLogger(__name__)


def _parse_price(price_str: str) -> float | None:
    """Konverter dansk decimalpris til float."""
    try:
        val = float(price_str.replace(",", "."))
        return val if val > 0 else None
    except (ValueError, AttributeError):
        return None


def _bond_label(bond: dict) -> str:
    """Lav et læsbart label til dropdown: navn + kurs + status."""
    name = bond.get("bondname", "")
    price = _parse_price(bond.get("prices", [{}])[0].get("price", "-1"))
    offer = bond.get("offerprice", -1)
    loan_code = bond.get("loanTypeCode", "")
    type_name = LOAN_TYPE_NAMES.get(loan_code, "")

    kurs_str = f"{price:.2f}" if price else "—"
    status = " ★" if offer and offer > 0 else ""
    return f"{name}  [{type_name}]  kurs {kurs_str}{status}"


async def _fetch_bonds() -> list[dict]:
    """Hent alle obligationer fra RD API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            resp.raise_for_status()
            return await resp.json(content_type=None)


class RDConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow til Realkredit Danmark integration."""

    VERSION = 1

    def __init__(self) -> None:
        self._bonds: list[dict] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Trin 1 — vælg hvilke obligationer der skal oprettes som sensorer."""
        errors: dict[str, str] = {}

        # Hent obligationer første gang
        if not self._bonds:
            try:
                self._bonds = await _fetch_bonds()
            except Exception:
                errors["base"] = "cannot_connect"
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema({}),
                    errors=errors,
                    description_placeholders={"url": API_URL},
                )

        if user_input is not None:
            selected_isins = user_input.get("selected_bonds", [])
            if not selected_isins:
                errors["base"] = "no_bonds_selected"
            else:
                # Gem valgte ISIN-koder i config entry
                return self.async_create_entry(
                    title="Realkredit Danmark",
                    data={"selected_bonds": selected_isins},
                )

        # Byg dropdown options — grupperet efter type
        fast = []
        tilpasning = []
        fkort = []

        for bond in self._bonds:
            isin = bond.get("isinCode", "")
            label = _bond_label(bond)
            opt = SelectOptionDict(value=isin, label=label)
            code = bond.get("loanTypeCode", "")
            if code == "01":
                fast.append(opt)
            elif code == "16":
                tilpasning.append(opt)
            elif code == "09":
                fkort.append(opt)

        # Sorter hver gruppe alfabetisk på label
        for group in (fast, tilpasning, fkort):
            group.sort(key=lambda x: x["label"])

        all_options = fast + tilpasning + fkort

        schema = vol.Schema(
            {
                vol.Required("selected_bonds"): SelectSelector(
                    SelectSelectorConfig(
                        options=all_options,
                        multiple=True,
                        mode=SelectSelectorMode.LIST,
                    )
                )
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Tillad at ændre valgte obligationer efter oprettelse."""
        return RDOptionsFlow(config_entry)


class RDOptionsFlow(config_entries.OptionsFlow):
    """Options flow — ændr valg af obligationer efter oprettelse."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry
        self._bonds: list[dict] = []

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Vis options med nuværende valg pre-selected."""
        errors: dict[str, str] = {}

        if not self._bonds:
            try:
                self._bonds = await _fetch_bonds()
            except Exception:
                errors["base"] = "cannot_connect"

        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={"selected_bonds": user_input.get("selected_bonds", [])},
            )

        current = self._config_entry.options.get(
            "selected_bonds",
            self._config_entry.data.get("selected_bonds", []),
        )

        all_options = []
        for bond in self._bonds:
            isin = bond.get("isinCode", "")
            all_options.append(SelectOptionDict(value=isin, label=_bond_label(bond)))

        schema = vol.Schema(
            {
                vol.Required("selected_bonds", default=current): SelectSelector(
                    SelectSelectorConfig(
                        options=all_options,
                        multiple=True,
                        mode=SelectSelectorMode.LIST,
                    )
                )
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )

