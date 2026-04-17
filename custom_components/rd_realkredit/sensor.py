"""Sensorer for Realkredit Danmark — kurs og effektiv rente."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    LOAN_TYPE_NAMES,
    ATTR_NAVN,
    ATTR_ISIN,
    ATTR_NOMINEL_RENTE,
    ATTR_LOEBETID,
    ATTR_UDBETALINGSKURS,
    ATTR_AABEN,
    ATTR_GRUPPE,
    ATTR_KURS_DATO,
    ATTR_SIDST_OPDATERET,
)
from . import RDDataCoordinator

_LOGGER = logging.getLogger(__name__)


def _parse_price(price_str: str) -> float | None:
    try:
        val = float(str(price_str).replace(",", "."))
        return round(val, 4) if val > 0 else None
    except (ValueError, AttributeError):
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Opret sensorer for hvert valgt ISIN."""
    coordinator: RDDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Valgte ISIN fra config flow (eller options flow)
    selected = entry.options.get(
        "selected_bonds", entry.data.get("selected_bonds", [])
    )

    entities: list[SensorEntity] = []

    for bond in coordinator.data or []:
        isin = bond.get("isinCode", "")
        if isin not in selected:
            continue

        # Kurs-sensor
        entities.append(RDKursSensor(coordinator, bond, entry.entry_id))
        # Effektiv rente-sensor
        entities.append(RDRenteSensor(coordinator, bond, entry.entry_id))

    async_add_entities(entities)


def _safe_name(bondname: str) -> str:
    """Lav et HA-venligt sensor-navn fra obligationsnavn."""
    return bondname.replace(",", ".").replace(" ", "_").lower()


class RDKursSensor(CoordinatorEntity, SensorEntity):
    """Kurssensor — dagskurs (priceRate)."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:bank"
    _attr_suggested_display_precision = 2

    def __init__(
        self,
        coordinator: RDDataCoordinator,
        bond: dict,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._isin = bond["isinCode"]
        self._bond_name = bond.get("bondname", self._isin)
        self._nominel = float(bond.get("nominelInterestRate", 0))
        self._loan_code = bond.get("loanTypeCode", "")

        safe = _safe_name(self._bond_name)
        self._attr_unique_id = f"{entry_id}_kurs_{self._isin}"
        self._attr_name = "Kurs"
        self._attr_has_entity_name = True

    @property
    def _current_bond(self) -> dict | None:
        if not self.coordinator.data:
            return None
        return next(
            (b for b in self.coordinator.data if b.get("isinCode") == self._isin),
            None,
        )

    @property
    def native_value(self) -> float | None:
        bond = self._current_bond
        if not bond:
            return None
        prices = bond.get("prices", [])
        if not prices:
            return None
        return _parse_price(prices[0].get("price", "-1"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        bond = self._current_bond
        if not bond:
            return {}
        offer = bond.get("offerprice", -1)
        prices = bond.get("prices", [])
        return {
            ATTR_NAVN: self._bond_name,
            ATTR_ISIN: self._isin,
            ATTR_NOMINEL_RENTE: self._nominel,
            ATTR_LOEBETID: f"{float(bond.get('termToMaturityYears', 0)):.0f} år",
            ATTR_UDBETALINGSKURS: round(offer, 2) if offer and offer > 0 else None,
            ATTR_AABEN: offer > 0 if offer else False,
            ATTR_GRUPPE: LOAN_TYPE_NAMES.get(self._loan_code, "Ukendt"),
            ATTR_KURS_DATO: prices[0].get("date") if prices else None,
            ATTR_SIDST_OPDATERET: bond.get("lastModified"),
        }

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._isin)},
            name=self._bond_name,
            manufacturer="Realkredit Danmark",
            model=LOAN_TYPE_NAMES.get(self._loan_code, "Obligation"),
            entry_type=None,
        )


class RDRenteSensor(CoordinatorEntity, SensorEntity):
    """Rentesensor — effektiv rente beregnet fra kurs og nominel rente."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:percent"
    _attr_suggested_display_precision = 2

    def __init__(
        self,
        coordinator: RDDataCoordinator,
        bond: dict,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._isin = bond["isinCode"]
        self._bond_name = bond.get("bondname", self._isin)
        self._nominel = float(bond.get("nominelInterestRate", 0))
        self._loan_code = bond.get("loanTypeCode", "")

        self._attr_unique_id = f"{entry_id}_rente_{self._isin}"
        self._attr_name = "Effektiv rente"
        self._attr_has_entity_name = True

    @property
    def _current_bond(self) -> dict | None:
        if not self.coordinator.data:
            return None
        return next(
            (b for b in self.coordinator.data if b.get("isinCode") == self._isin),
            None,
        )

    @property
    def native_value(self) -> float | None:
        bond = self._current_bond
        if not bond:
            return None
        prices = bond.get("prices", [])
        if not prices:
            return None
        kurs = _parse_price(prices[0].get("price", "-1"))
        if not kurs or kurs <= 0 or self._nominel <= 0:
            return None
        # Effektiv rente approx: nominel / kurs * 100
        return round(self._nominel / kurs * 100, 2)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        bond = self._current_bond
        if not bond:
            return {}
        return {
            ATTR_NAVN: self._bond_name,
            ATTR_ISIN: self._isin,
            ATTR_NOMINEL_RENTE: self._nominel,
            ATTR_GRUPPE: LOAN_TYPE_NAMES.get(self._loan_code, "Ukendt"),
        }

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._isin)},
            name=self._bond_name,
            manufacturer="Realkredit Danmark",
            model=LOAN_TYPE_NAMES.get(self._loan_code, "Obligation"),
        )
