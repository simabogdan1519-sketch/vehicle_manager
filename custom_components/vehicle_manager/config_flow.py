"""Config flow for Vehicle Manager."""
from __future__ import annotations

import re
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_CAR_NAME, CONF_MAKE, CONF_MODEL, CONF_YEAR, CONF_PLATE,
    CONF_COUNTRY, CONF_LANGUAGE,
    CONF_INSURANCE_EXPIRY, CONF_CASCO_EXPIRY, CONF_INSPECTION_EXPIRY,
    CONF_ROAD_TAX_EXPIRY, CONF_VIGNETTE_EXPIRY,
    CONF_FIRE_EXTINGUISHER_EXPIRY, CONF_FIRST_AID_KIT_EXPIRY,
    CONF_ODOMETER,
    CONF_OIL_CHANGE_DATE, CONF_OIL_CHANGE_KM, CONF_OIL_CHANGE_INTERVAL,
    CONF_AIR_FILTER_DATE, CONF_AIR_FILTER_KM, CONF_AIR_FILTER_INTERVAL,
    CONF_CABIN_FILTER_DATE, CONF_CABIN_FILTER_KM, CONF_CABIN_FILTER_INTERVAL,
    CONF_TIMING_BELT_DATE, CONF_TIMING_BELT_KM, CONF_TIMING_BELT_INTERVAL,
    CONF_BRAKES_DATE, CONF_BRAKES_KM, CONF_BRAKES_INTERVAL,
    CONF_BATTERY_DATE, CONF_TIRES_DATE, CONF_AC_SERVICE_DATE,
    CONF_GENERAL_SERVICE_DATE, CONF_GENERAL_SERVICE_KM, CONF_GENERAL_SERVICE_INTERVAL,
    CONF_NOTES,
    COUNTRIES, LANGUAGES, COUNTRY_VIGNETTE_NAME,
    DEFAULT_OIL_INTERVAL, DEFAULT_AIR_FILTER_INTERVAL, DEFAULT_CABIN_FILTER_INTERVAL,
    DEFAULT_TIMING_BELT_INTERVAL, DEFAULT_BRAKES_INTERVAL, DEFAULT_GENERAL_SERVICE_INTERVAL,
)

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _date_selector() -> selector.DateSelector:
    return selector.DateSelector()


def _km_selector(default: int = 0) -> selector.NumberSelector:
    return selector.NumberSelector(
        selector.NumberSelectorConfig(min=0, max=9_999_999, step=1, mode="box",
                                      unit_of_measurement="km")
    )


def _year_selector() -> selector.NumberSelector:
    return selector.NumberSelector(
        selector.NumberSelectorConfig(min=1950, max=2030, step=1, mode="box")
    )


def _text_selector() -> selector.TextSelector:
    return selector.TextSelector(selector.TextSelectorConfig(type="text"))


def _textarea_selector() -> selector.TextSelector:
    return selector.TextSelector(selector.TextSelectorConfig(multiline=True))


def _select_selector(options: dict) -> selector.SelectSelector:
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[{"value": k, "label": v} for k, v in options.items()],
            mode="dropdown",
        )
    )


# ─── Step schemas ─────────────────────────────────────────────────────────────

STEP_CAR_SCHEMA = vol.Schema({
    vol.Required(CONF_CAR_NAME): _text_selector(),
    vol.Required(CONF_MAKE): _text_selector(),
    vol.Required(CONF_MODEL): _text_selector(),
    vol.Required(CONF_YEAR, default=2020): _year_selector(),
    vol.Required(CONF_PLATE): _text_selector(),
    vol.Required(CONF_COUNTRY, default="RO"): _select_selector(COUNTRIES),
    vol.Required(CONF_LANGUAGE, default="en"): _select_selector(LANGUAGES),
})

STEP_DOCS_SCHEMA = vol.Schema({
    vol.Optional(CONF_INSURANCE_EXPIRY): _date_selector(),
    vol.Optional(CONF_CASCO_EXPIRY): _date_selector(),
    vol.Optional(CONF_INSPECTION_EXPIRY): _date_selector(),
    vol.Optional(CONF_ROAD_TAX_EXPIRY): _date_selector(),
    vol.Optional(CONF_VIGNETTE_EXPIRY): _date_selector(),
    vol.Optional(CONF_FIRE_EXTINGUISHER_EXPIRY): _date_selector(),
    vol.Optional(CONF_FIRST_AID_KIT_EXPIRY): _date_selector(),
})

STEP_SERVICE_SCHEMA = vol.Schema({
    vol.Optional(CONF_ODOMETER, default=0): _km_selector(),
    # Oil
    vol.Optional(CONF_OIL_CHANGE_DATE): _date_selector(),
    vol.Optional(CONF_OIL_CHANGE_KM, default=0): _km_selector(),
    vol.Optional(CONF_OIL_CHANGE_INTERVAL, default=DEFAULT_OIL_INTERVAL): _km_selector(),
    # Air filter
    vol.Optional(CONF_AIR_FILTER_DATE): _date_selector(),
    vol.Optional(CONF_AIR_FILTER_KM, default=0): _km_selector(),
    vol.Optional(CONF_AIR_FILTER_INTERVAL, default=DEFAULT_AIR_FILTER_INTERVAL): _km_selector(),
    # Cabin filter
    vol.Optional(CONF_CABIN_FILTER_DATE): _date_selector(),
    vol.Optional(CONF_CABIN_FILTER_KM, default=0): _km_selector(),
    vol.Optional(CONF_CABIN_FILTER_INTERVAL, default=DEFAULT_CABIN_FILTER_INTERVAL): _km_selector(),
    # Timing belt
    vol.Optional(CONF_TIMING_BELT_DATE): _date_selector(),
    vol.Optional(CONF_TIMING_BELT_KM, default=0): _km_selector(),
    vol.Optional(CONF_TIMING_BELT_INTERVAL, default=DEFAULT_TIMING_BELT_INTERVAL): _km_selector(),
    # Brakes
    vol.Optional(CONF_BRAKES_DATE): _date_selector(),
    vol.Optional(CONF_BRAKES_KM, default=0): _km_selector(),
    vol.Optional(CONF_BRAKES_INTERVAL, default=DEFAULT_BRAKES_INTERVAL): _km_selector(),
    # Battery (date only)
    vol.Optional(CONF_BATTERY_DATE): _date_selector(),
    # Tires seasonal swap (date only)
    vol.Optional(CONF_TIRES_DATE): _date_selector(),
    # AC service (date only)
    vol.Optional(CONF_AC_SERVICE_DATE): _date_selector(),
    # General service
    vol.Optional(CONF_GENERAL_SERVICE_DATE): _date_selector(),
    vol.Optional(CONF_GENERAL_SERVICE_KM, default=0): _km_selector(),
    vol.Optional(CONF_GENERAL_SERVICE_INTERVAL, default=DEFAULT_GENERAL_SERVICE_INTERVAL): _km_selector(),
    # Notes
    vol.Optional(CONF_NOTES, default=""): _textarea_selector(),
})


# ─── Config Flow ─────────────────────────────────────────────────────────────

class VehicleManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vehicle Manager."""

    VERSION = 1

    def __init__(self) -> None:
        self._car_data: dict = {}
        self._docs_data: dict = {}

    async def async_step_user(self, user_input: dict | None = None):
        """Step 1 — Basic car info."""
        errors: dict = {}
        if user_input is not None:
            self._car_data = user_input
            return await self.async_step_documents()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_CAR_SCHEMA,
            errors=errors,
        )

    async def async_step_documents(self, user_input: dict | None = None):
        """Step 2 — Document expiry dates."""
        if user_input is not None:
            self._docs_data = user_input
            return await self.async_step_service()

        return self.async_show_form(
            step_id="documents",
            data_schema=STEP_DOCS_SCHEMA,
        )

    async def async_step_service(self, user_input: dict | None = None):
        """Step 3 — Service history."""
        if user_input is not None:
            options = {**self._docs_data, **user_input}
            return self.async_create_entry(
                title=self._car_data[CONF_CAR_NAME],
                data=self._car_data,
                options=options,
            )

        return self.async_show_form(
            step_id="service",
            data_schema=STEP_SERVICE_SCHEMA,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return VehicleManagerOptionsFlow(config_entry)


# ─── Options Flow ─────────────────────────────────────────────────────────────

class VehicleManagerOptionsFlow(config_entries.OptionsFlow):
    """Allow editing all dates/km after initial setup."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry
        self._docs_data: dict = {}

    def _prefill(self, schema: vol.Schema) -> vol.Schema:
        """Return schema with current option values as defaults."""
        opts = self._config_entry.options
        description_placeholders = {}
        new_schema = {}
        for key, validator in schema.schema.items():
            current = opts.get(str(key))
            if current is not None:
                new_schema[vol.Optional(str(key), default=current)] = validator
            else:
                new_schema[key] = validator
        return vol.Schema(new_schema)

    async def async_step_init(self, user_input: dict | None = None):
        """Start with document dates."""
        return await self.async_step_documents()

    async def async_step_documents(self, user_input: dict | None = None):
        if user_input is not None:
            self._docs_data = user_input
            return await self.async_step_service()
        return self.async_show_form(
            step_id="documents",
            data_schema=self._prefill(STEP_DOCS_SCHEMA),
        )

    async def async_step_service(self, user_input: dict | None = None):
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={**self._docs_data, **user_input},
            )
        return self.async_show_form(
            step_id="service",
            data_schema=self._prefill(STEP_SERVICE_SCHEMA),
        )
