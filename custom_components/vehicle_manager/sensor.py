"""Sensor platform for Vehicle Manager."""
from __future__ import annotations

import logging
from datetime import date, timedelta

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.dt as dt_util

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
    SENSOR_INSURANCE, SENSOR_CASCO, SENSOR_INSPECTION, SENSOR_ROAD_TAX,
    SENSOR_VIGNETTE, SENSOR_FIRE_EXTINGUISHER, SENSOR_FIRST_AID_KIT,
    SENSOR_ODOMETER, SENSOR_OIL_CHANGE, SENSOR_AIR_FILTER, SENSOR_CABIN_FILTER,
    SENSOR_TIMING_BELT, SENSOR_BRAKES, SENSOR_BATTERY, SENSOR_TIRES,
    SENSOR_AC_SERVICE, SENSOR_GENERAL_SERVICE,
    COUNTRY_FLAGS, COUNTRY_VIGNETTE_NAME,
    COUNTRY_INSURANCE_NAME, COUNTRY_INSPECTION_NAME, COUNTRY_ROAD_TAX_NAME,
    DAYS_CRITICAL, DAYS_WARNING, KM_CRITICAL, KM_WARNING,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=6)


# ─── Setup ────────────────────────────────────────────────────────────────────

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create all sensor entities for one vehicle."""
    country = entry.data.get(CONF_COUNTRY, "RO")
    sensors: list[SensorEntity] = []

    # ── Document / expiry sensors ────────────────────────────────────────────
    doc_sensors = [
        (SENSOR_INSURANCE, CONF_INSURANCE_EXPIRY,
         COUNTRY_INSURANCE_NAME.get(country, "Insurance"), "mdi:shield-car"),
        (SENSOR_CASCO, CONF_CASCO_EXPIRY, "CASCO", "mdi:shield-check"),
        (SENSOR_INSPECTION, CONF_INSPECTION_EXPIRY,
         COUNTRY_INSPECTION_NAME.get(country, "Inspection"), "mdi:car-wrench"),
        (SENSOR_ROAD_TAX, CONF_ROAD_TAX_EXPIRY,
         COUNTRY_ROAD_TAX_NAME.get(country, "Road Tax"), "mdi:currency-eur"),
        (SENSOR_FIRE_EXTINGUISHER, CONF_FIRE_EXTINGUISHER_EXPIRY,
         "Fire Extinguisher", "mdi:fire-extinguisher"),
        (SENSOR_FIRST_AID_KIT, CONF_FIRST_AID_KIT_EXPIRY,
         "First Aid Kit", "mdi:medical-bag"),
    ]
    if country in COUNTRY_VIGNETTE_NAME:
        doc_sensors.append((
            SENSOR_VIGNETTE, CONF_VIGNETTE_EXPIRY,
            COUNTRY_VIGNETTE_NAME[country], "mdi:highway",
        ))

    for sensor_type, conf_key, label, icon in doc_sensors:
        sensors.append(VehicleDateSensor(entry, sensor_type, conf_key, label, icon))

    # ── Service sensors ───────────────────────────────────────────────────────
    sensors.extend([
        VehicleServiceSensor(
            entry, SENSOR_OIL_CHANGE, "Oil Change",
            "mdi:oil", CONF_OIL_CHANGE_DATE, CONF_OIL_CHANGE_KM, CONF_OIL_CHANGE_INTERVAL,
        ),
        VehicleServiceSensor(
            entry, SENSOR_AIR_FILTER, "Air Filter",
            "mdi:air-filter", CONF_AIR_FILTER_DATE, CONF_AIR_FILTER_KM, CONF_AIR_FILTER_INTERVAL,
        ),
        VehicleServiceSensor(
            entry, SENSOR_CABIN_FILTER, "Cabin Filter",
            "mdi:air-filter", CONF_CABIN_FILTER_DATE, CONF_CABIN_FILTER_KM, CONF_CABIN_FILTER_INTERVAL,
        ),
        VehicleServiceSensor(
            entry, SENSOR_TIMING_BELT, "Timing Belt",
            "mdi:engine", CONF_TIMING_BELT_DATE, CONF_TIMING_BELT_KM, CONF_TIMING_BELT_INTERVAL,
        ),
        VehicleServiceSensor(
            entry, SENSOR_BRAKES, "Brakes",
            "mdi:car-brake-abs", CONF_BRAKES_DATE, CONF_BRAKES_KM, CONF_BRAKES_INTERVAL,
        ),
        VehicleDateSensor(
            entry, SENSOR_BATTERY, CONF_BATTERY_DATE, "Battery", "mdi:battery",
            is_expiry=False,
        ),
        VehicleDateSensor(
            entry, SENSOR_TIRES, CONF_TIRES_DATE, "Tires (last swap)", "mdi:tire",
            is_expiry=False,
        ),
        VehicleDateSensor(
            entry, SENSOR_AC_SERVICE, CONF_AC_SERVICE_DATE, "A/C Service", "mdi:air-conditioner",
            is_expiry=False,
        ),
        VehicleServiceSensor(
            entry, SENSOR_GENERAL_SERVICE, "General Service",
            "mdi:wrench", CONF_GENERAL_SERVICE_DATE, CONF_GENERAL_SERVICE_KM,
            CONF_GENERAL_SERVICE_INTERVAL,
        ),
        VehicleOdometerSensor(entry),
    ])

    async_add_entities(sensors, True)


# ─── Shared device info helper ────────────────────────────────────────────────

def _device_info(entry: ConfigEntry) -> DeviceInfo:
    d = entry.data
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=d.get(CONF_CAR_NAME, "Vehicle"),
        manufacturer=d.get(CONF_MAKE, ""),
        model=f"{d.get(CONF_MODEL, '')} ({d.get(CONF_YEAR, '')})",
        sw_version=d.get(CONF_PLATE, ""),
    )


# ─── Status helper ────────────────────────────────────────────────────────────

def _days_status(days: int | None) -> str:
    if days is None:
        return "unknown"
    if days < 0:
        return "expired"
    if days < DAYS_CRITICAL:
        return "critical"
    if days < DAYS_WARNING:
        return "warning"
    return "ok"


def _km_status(km_remaining: int | None) -> str:
    if km_remaining is None:
        return "unknown"
    if km_remaining < 0:
        return "overdue"
    if km_remaining < KM_CRITICAL:
        return "critical"
    if km_remaining < KM_WARNING:
        return "warning"
    return "ok"


def _combined_status(*statuses: str) -> str:
    priority = ["expired", "overdue", "critical", "warning", "ok", "unknown"]
    for p in priority:
        if p in statuses:
            return p
    return "unknown"


# ─── Date / Expiry Sensor ─────────────────────────────────────────────────────

class VehicleDateSensor(SensorEntity):
    """
    Tracks a single date.
    - is_expiry=True  → state = days until expiry (neg if expired)
    - is_expiry=False → state = days since the event (for battery, tires, ac)
    """

    _attr_should_poll = True
    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        sensor_type: str,
        conf_key: str,
        label: str,
        icon: str,
        is_expiry: bool = True,
    ) -> None:
        self._entry = entry
        self._sensor_type = sensor_type
        self._conf_key = conf_key
        self._label = label
        self._is_expiry = is_expiry
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = "days"

    @property
    def name(self) -> str:
        return self._label

    @property
    def device_info(self) -> DeviceInfo:
        return _device_info(self._entry)

    @property
    def native_value(self) -> int | None:
        date_str = self._entry.options.get(self._conf_key)
        if not date_str:
            return None
        try:
            d = date.fromisoformat(str(date_str))
            delta = (d - date.today()).days
            return delta if self._is_expiry else -delta  # days-since for non-expiry
        except (ValueError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict:
        val = self.native_value
        date_str = self._entry.options.get(self._conf_key)
        d = self._entry.data
        status = _days_status(val) if self._is_expiry else (
            "ok" if val is not None and val < 365
            else "warning" if val is not None else "unknown"
        )
        return {
            "date": date_str,
            "days_remaining": val if self._is_expiry else None,
            "days_since": val if not self._is_expiry else None,
            "status": status,
            "is_expiry": self._is_expiry,
            "sensor_type": self._sensor_type,
            "car_name": d.get(CONF_CAR_NAME),
            "country": d.get(CONF_COUNTRY),
            "language": d.get(CONF_LANGUAGE),
            "plate": d.get(CONF_PLATE),
            "make": d.get(CONF_MAKE),
            "model": d.get(CONF_MODEL),
            "year": d.get(CONF_YEAR),
            "flag": COUNTRY_FLAGS.get(d.get(CONF_COUNTRY, ""), ""),
            "notes": self._entry.options.get(CONF_NOTES, ""),
        }


# ─── Service Sensor (date + km) ───────────────────────────────────────────────

class VehicleServiceSensor(SensorEntity):
    """
    Tracks a service interval with both date and km.
    State = worst status between km_remaining and days_since.
    """

    _attr_should_poll = True
    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        sensor_type: str,
        label: str,
        icon: str,
        date_key: str,
        km_key: str,
        interval_key: str,
    ) -> None:
        self._entry = entry
        self._sensor_type = sensor_type
        self._label = label
        self._date_key = date_key
        self._km_key = km_key
        self._interval_key = interval_key
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = "km"

    @property
    def name(self) -> str:
        return self._label

    @property
    def device_info(self) -> DeviceInfo:
        return _device_info(self._entry)

    def _km_remaining(self) -> int | None:
        opts = self._entry.options
        odometer = opts.get(CONF_ODOMETER)
        last_km = opts.get(self._km_key)
        interval = opts.get(self._interval_key)
        if None in (odometer, last_km, interval) or interval == 0:
            return None
        try:
            return int(interval) - (int(odometer) - int(last_km))
        except (ValueError, TypeError):
            return None

    def _days_since(self) -> int | None:
        date_str = self._entry.options.get(self._date_key)
        if not date_str:
            return None
        try:
            d = date.fromisoformat(str(date_str))
            return (date.today() - d).days
        except (ValueError, TypeError):
            return None

    @property
    def native_value(self) -> int | None:
        return self._km_remaining()

    @property
    def extra_state_attributes(self) -> dict:
        opts = self._entry.options
        d = self._entry.data
        km_rem = self._km_remaining()
        days = self._days_since()
        km_status = _km_status(km_rem)
        status = km_status if km_rem is not None else "unknown"

        return {
            "last_service_date": opts.get(self._date_key),
            "last_service_km": opts.get(self._km_key),
            "interval_km": opts.get(self._interval_key),
            "odometer": opts.get(CONF_ODOMETER),
            "km_remaining": km_rem,
            "days_since_service": days,
            "status": status,
            "km_status": km_status,
            "sensor_type": self._sensor_type,
            "car_name": d.get(CONF_CAR_NAME),
            "country": d.get(CONF_COUNTRY),
            "language": d.get(CONF_LANGUAGE),
            "plate": d.get(CONF_PLATE),
            "make": d.get(CONF_MAKE),
            "model": d.get(CONF_MODEL),
            "year": d.get(CONF_YEAR),
            "flag": COUNTRY_FLAGS.get(d.get(CONF_COUNTRY, ""), ""),
            "notes": opts.get(CONF_NOTES, ""),
        }


# ─── Odometer Sensor ──────────────────────────────────────────────────────────

class VehicleOdometerSensor(SensorEntity):
    """Current odometer reading."""

    _attr_should_poll = True
    _attr_has_entity_name = True
    _attr_icon = "mdi:counter"
    _attr_native_unit_of_measurement = "km"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{SENSOR_ODOMETER}"

    @property
    def name(self) -> str:
        return "Odometer"

    @property
    def device_info(self) -> DeviceInfo:
        return _device_info(self._entry)

    @property
    def native_value(self) -> int | None:
        val = self._entry.options.get(CONF_ODOMETER)
        try:
            return int(val) if val is not None else None
        except (ValueError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict:
        d = self._entry.data
        return {
            "sensor_type": SENSOR_ODOMETER,
            "car_name": d.get(CONF_CAR_NAME),
            "country": d.get(CONF_COUNTRY),
            "language": d.get(CONF_LANGUAGE),
            "plate": d.get(CONF_PLATE),
            "make": d.get(CONF_MAKE),
            "model": d.get(CONF_MODEL),
            "year": d.get(CONF_YEAR),
            "flag": COUNTRY_FLAGS.get(d.get(CONF_COUNTRY, ""), ""),
            "notes": self._entry.options.get(CONF_NOTES, ""),
        }
