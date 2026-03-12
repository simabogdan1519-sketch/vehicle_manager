# 🚗 Vehicle Manager — Home Assistant Integration

> Track documents, expiry dates and service intervals for all your vehicles — with full support for 10 EU countries and 8 languages.

![Two vehicle cards side by side](docs/images/screenshot-two-cards.svg)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [HACS (recommended)](#hacs-recommended)
  - [Manual](#manual)
- [Adding a Vehicle](#adding-a-vehicle)
  - [Step 1 — Vehicle Info](#step-1--vehicle-info)
  - [Step 2 — Documents](#step-2--documents)
  - [Step 3 — Service History](#step-3--service-history)
- [Updating Values](#updating-values)
- [Sensors Reference](#sensors-reference)
  - [Document Sensors](#document-sensors)
  - [Service Sensors](#service-sensors)
  - [Odometer Sensor](#odometer-sensor)
- [Sensor Attributes](#sensor-attributes)
- [Status Values](#status-values)
- [Country Support](#country-support)
- [Automation Examples](#automation-examples)
- [Troubleshooting](#troubleshooting)
- [File Structure](#file-structure)

---

## Overview

**Vehicle Manager** is a custom Home Assistant integration that creates a structured set of sensor entities for each vehicle you own. Each sensor tracks a specific document expiry date or service interval, and exposes a `status` attribute (`ok` / `warning` / `critical` / `expired` / `overdue`) that you can use in automations, notifications or the companion [Vehicle Manager Card](README-card.md).

You can add as many vehicles as you like — each vehicle runs as its own config entry and gets its own HA device grouping all its sensors together.

---

## Features

| Category | Details |
|----------|---------|
| 🌍 **Countries** | Romania, Germany, France, Italy, Austria, Spain, Poland, Netherlands, Hungary, Czech Republic |
| 🗣️ **Languages** | English, Romanian, German, French, Italian, Spanish, Polish, Hungarian |
| 📄 **Documents** | Insurance (RCA/OC/RC…), CASCO, Technical Inspection (ITP/TÜV/CT/Revisione/APK…), Road Tax, Vignette/Rovinieta, Fire Extinguisher, First Aid Kit |
| 🔧 **Service items** | Oil Change, Air Filter, Cabin Filter, Timing Belt, Brakes, Battery, Tires, A/C Service, General Service |
| 📊 **Per sensor** | `days remaining` or `km remaining` as state value + full attribute set including `status`, dates, km values |
| 🔄 **Auto-refresh** | Sensors recalculate every 6 hours; full reload on every options update |
| 🏷️ **HA Device** | All sensors for a vehicle are grouped under one HA Device (visible in Settings → Devices) |

---

## Requirements

- Home Assistant **2023.6** or newer
- Python 3.11+ (bundled with HA)
- No external Python dependencies

---

## Installation

### HACS (recommended)

1. Open HACS in your HA sidebar.
2. Go to **Integrations** → click the `⋮` menu → **Custom repositories**.
3. Add the repository URL and set category to **Integration**.
4. Click **Download**.
5. Restart Home Assistant.

### Manual

1. Download or clone this repository.
2. Copy the `custom_components/vehicle_manager/` folder into your HA configuration directory:

```
<config>/
└── custom_components/
    └── vehicle_manager/        ← copy this entire folder
        ├── __init__.py
        ├── manifest.json
        ├── const.py
        ├── config_flow.py
        ├── sensor.py
        ├── strings.json
        └── translations/
            ├── en.json
            ├── ro.json
            ├── de.json
            ├── fr.json
            ├── it.json
            ├── es.json
            ├── pl.json
            └── hu.json
```

3. Restart Home Assistant.

---

## Adding a Vehicle

Go to **Settings → Devices & Services → Add Integration**, search for **Vehicle Manager** and follow the 3-step wizard.

![Config flow — step 1](docs/images/screenshot-config-flow.svg)

### Step 1 — Vehicle Info

| Field | Required | Description |
|-------|----------|-------------|
| **Vehicle Name** | ✅ | Human-readable name, e.g. `Dacia Logan`. Used as the HA device name and to generate the entity slug. |
| **Make (Brand)** | ✅ | Manufacturer, e.g. `Volkswagen` |
| **Model** | ✅ | e.g. `Golf 7` |
| **Year** | ✅ | Year of manufacture |
| **License Plate** | ✅ | Registration number |
| **Country** | ✅ | Used to select country-specific document names (ITP vs TÜV vs CT etc.) and to show the flag emoji |
| **Card Language** | ✅ | Language used in the [Vehicle Card](README-card.md) UI. Does not affect entity names in HA itself. |

### Step 2 — Documents

All fields are optional — leave blank anything that does not apply to your vehicle or country.

| Field | Description |
|-------|-------------|
| **Mandatory Insurance Expiry** | RCA / KFZ-Haftpflicht / OC / WA-verzekering etc. |
| **CASCO / Comprehensive Insurance Expiry** | Optional full-coverage policy |
| **Technical Inspection Expiry** | ITP / TÜV / CT / Revisione / APK / STK etc. |
| **Road Tax Expiry** | Impozit auto / KFZ-Steuer / Bollo auto / IVTM etc. |
| **Vignette Expiry** | Rovinieta / Autobahnvignette / e-TOLL — only shown for countries that have one |
| **Fire Extinguisher Expiry** | Required in some EU countries |
| **First Aid Kit Expiry** | Required in some EU countries |

### Step 3 — Service History

| Field | Description |
|-------|-------------|
| **Current Odometer (km)** | Your vehicle's current mileage — used to calculate km remaining for all service items |
| **Last Oil Change — Date / Km** | Date and odometer at last oil change |
| **Oil Change Interval (km)** | Default: 10 000 km |
| **Last Air Filter — Date / Km** | Default interval: 30 000 km |
| **Last Cabin Filter — Date / Km** | Default interval: 15 000 km |
| **Last Timing Belt — Date / Km** | ⚠️ Safety-critical. Default interval: 120 000 km |
| **Last Brake Check — Date / Km** | Default interval: 50 000 km |
| **Battery Installed Date** | Tracks age — typical battery life is 4–5 years |
| **Last Tire Swap Date** | Summer ↔ Winter swap reminder |
| **Last A/C Service Date** | Freon recharge + sanitization |
| **Last General Service — Date / Km** | Default interval: 15 000 km |
| **Notes** | Free text per vehicle — displayed in the card |

---

## Updating Values

To update any date or km value after initial setup:

1. Go to **Settings → Devices & Services**.
2. Find the **Vehicle Manager** entry for your vehicle.
3. Click **Configure**.
4. Update the values in the 2-step options flow (Documents → Service).

The integration will automatically reload all sensors with the new values.

---

## Sensors Reference

All entity IDs follow the pattern:

```
sensor.vehicle_{slug}_{type}
```

Where `{slug}` is your vehicle name lowercased with spaces replaced by underscores.  
For example: `"Dacia Logan"` → `dacia_logan` → `sensor.vehicle_dacia_logan_insurance`

### Document Sensors

| Entity | State | Unit | Notes |
|--------|-------|------|-------|
| `…_insurance` | Days until expiry | `days` | Negative = expired |
| `…_casco` | Days until expiry | `days` | Negative = expired |
| `…_inspection` | Days until expiry | `days` | Name varies by country |
| `…_road_tax` | Days until expiry | `days` | Name varies by country |
| `…_vignette` | Days until expiry | `days` | Only created for countries with vignettes |
| `…_fire_extinguisher` | Days until expiry | `days` | |
| `…_first_aid_kit` | Days until expiry | `days` | |

> **Note:** If you did not enter a date for a sensor, its state will be `None` (unavailable).

### Service Sensors

| Entity | State | Unit | Notes |
|--------|-------|------|-------|
| `…_oil_change` | km remaining until next change | `km` | Negative = overdue |
| `…_air_filter` | km remaining | `km` | |
| `…_cabin_filter` | km remaining | `km` | |
| `…_timing_belt` | km remaining | `km` | ⚠️ Safety-critical |
| `…_brakes` | km remaining | `km` | |
| `…_battery` | Days since installed | `days` | Higher = older |
| `…_tires` | Days since last swap | `days` | |
| `…_ac_service` | Days since last service | `days` | |
| `…_general_service` | km remaining | `km` | |

**km remaining formula:**  
`km_remaining = interval_km − (current_odometer − odometer_at_last_service)`

### Odometer Sensor

| Entity | State | Unit | HA class |
|--------|-------|------|----------|
| `…_odometer` | Current reading | `km` | `total_increasing` |

---

## Sensor Attributes

Every sensor exposes the following attributes, which are used by the card and are available for automations:

```yaml
# Common attributes on all sensors
status: "ok"          # ok | warning | critical | expired | overdue | unknown
sensor_type: "insurance"
car_name: "Dacia Logan"
country: "RO"
language: "ro"
plate: "B-123-ABC"
make: "Dacia"
model: "Logan"
year: 2019
flag: "🇷🇴"
notes: "Service in March"

# Date sensors add:
date: "2025-04-15"
days_remaining: 18    # null for non-expiry sensors
days_since: null       # populated for battery/tires/ac sensors

# Service sensors add:
last_service_date: "2024-09-10"
last_service_km: 117000
interval_km: 10000
odometer: 127450
km_remaining: 320
days_since_service: 190
km_status: "critical"
```

---

## Status Values

![Status indicator closeup](docs/images/screenshot-status-legend.svg)

| Status | Colour | Date condition | Km condition |
|--------|--------|---------------|-------------|
| `ok` | 🟢 Green | > 30 days remaining | > 3 000 km remaining |
| `warning` | 🟡 Amber | 7 – 30 days remaining | 500 – 3 000 km remaining |
| `critical` | 🔴 Red | 0 – 7 days remaining | 0 – 500 km remaining |
| `expired` | ⛔ Dark red | Past expiry date | — |
| `overdue` | ⛔ Dark red | — | Past interval km |
| `unknown` | ⬜ Grey | No date entered | No km data |

---

## Country Support

| Flag | Country | Insurance name | Inspection name | Road Tax name | Vignette |
|------|---------|---------------|----------------|--------------|---------|
| 🇷🇴 | Romania | RCA | ITP | Impozit auto | Rovinieta |
| 🇩🇪 | Germany | KFZ-Haftpflicht | TÜV / HU | KFZ-Steuer | — |
| 🇫🇷 | France | Assurance RC | Contrôle Technique (CT) | Taxe véhicule | — |
| 🇮🇹 | Italy | RCA | Revisione | Bollo auto | — |
| 🇦🇹 | Austria | KFZ-Haftpflicht | §57a Pickerl | KFZ-Steuer | Autobahnvignette |
| 🇪🇸 | Spain | Seguro obligatorio | ITV | IVTM | — |
| 🇵🇱 | Poland | OC | Przegląd techniczny | Podatek drogowy | e-TOLL |
| 🇳🇱 | Netherlands | WA-verzekering | APK | Wegenbelasting (MRB) | — |
| 🇭🇺 | Hungary | Kötelező biztosítás (KGFB) | Műszaki vizsga | Gépjárműadó | Autópálya-matrica |
| 🇨🇿 | Czech Rep. | Povinné ručení | STK | Silniční daň | Dálniční známka |

> Countries without a vignette system will not have a `vignette` sensor created. You can still add dates for the vignette field in the config flow — they will simply not produce a sensor.

---

## Automation Examples

### Notify X days before any document expires

```yaml
automation:
  - alias: "Vehicle – Insurance expiring soon"
    trigger:
      - platform: numeric_state
        entity_id: sensor.vehicle_dacia_logan_insurance
        below: 30
        above: 0
    condition:
      - condition: template
        value_template: "{{ states('sensor.vehicle_dacia_logan_insurance') | int > 0 }}"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🚗 Insurance expiring"
          message: >
            {{ state_attr('sensor.vehicle_dacia_logan_insurance', 'car_name') }}
            insurance expires in
            {{ states('sensor.vehicle_dacia_logan_insurance') }} days
            ({{ state_attr('sensor.vehicle_dacia_logan_insurance', 'date') }}).
```

### Notify when ITP / TÜV / CT is expired

```yaml
automation:
  - alias: "Vehicle – Inspection expired"
    trigger:
      - platform: state
        entity_id: sensor.vehicle_dacia_logan_inspection
    condition:
      - condition: template
        value_template: >
          {{ state_attr('sensor.vehicle_dacia_logan_inspection', 'status') == 'expired' }}
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ ITP expired!"
          message: "Your ITP has expired. Do not drive until renewed."
```

### Notify when oil change is overdue by more than 500 km

```yaml
automation:
  - alias: "Vehicle – Oil change overdue"
    trigger:
      - platform: numeric_state
        entity_id: sensor.vehicle_dacia_logan_oil_change
        below: -500
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🛢️ Oil change overdue!"
          message: >
            Oil change is
            {{ (states('sensor.vehicle_dacia_logan_oil_change') | int * -1) }} km overdue.
            Last service: {{ state_attr('sensor.vehicle_dacia_logan_oil_change', 'last_service_date') }}.
```

### Daily summary notification for all issues

```yaml
automation:
  - alias: "Vehicle – Daily issues summary"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🚗 Vehicle Manager Summary"
          message: >
            {% set sensors = [
              'sensor.vehicle_dacia_logan_insurance',
              'sensor.vehicle_dacia_logan_inspection',
              'sensor.vehicle_dacia_logan_vignette',
              'sensor.vehicle_dacia_logan_oil_change',
              'sensor.vehicle_dacia_logan_timing_belt'
            ] %}
            {% set issues = sensors | selectattr('state', 'lt', '0') | list %}
            {% if issues | length > 0 %}
              ⚠️ {{ issues | length }} item(s) need attention!
            {% else %}
              ✅ All clear.
            {% endif %}
```

### Persistent notification on dashboard for critical items

```yaml
automation:
  - alias: "Vehicle – Persistent critical alert"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('sensor.vehicle_dacia_logan_inspection', 'status') in ['critical','expired']
          or state_attr('sensor.vehicle_dacia_logan_insurance', 'status') in ['critical','expired'] }}
    action:
      - service: persistent_notification.create
        data:
          title: "🚗 Vehicle – Urgent Action Required"
          message: >
            Check your vehicle documents immediately.
            ITP: {{ states('sensor.vehicle_dacia_logan_inspection') }} days
            | Insurance: {{ states('sensor.vehicle_dacia_logan_insurance') }} days
          notification_id: vehicle_urgent
```

---

## Troubleshooting

**Sensors show `unavailable`**  
→ Make sure HA was fully restarted after copying the integration files.  
→ Check `home-assistant.log` for Python import errors.

**Entity IDs don't match what I expect**  
→ The slug is derived from the **Vehicle Name** field (Step 1). Open the entity in Settings → Entities to confirm its ID.

**Service km remaining shows `None`**  
→ The odometer field (Step 3) must be filled in. Without it, km calculations are not possible.

**Vignette sensor is missing**  
→ Vignette sensors are only created for countries that have a vignette system: Romania, Austria, Poland, Hungary, Czech Republic.

**I want to change the country after setup**  
→ The country is part of the initial config (Step 1), not the options flow. You need to delete the entry and re-add it. Your dates/km are in the options, so note them down first.

---

## File Structure

```
custom_components/vehicle_manager/
├── __init__.py          # Integration setup & reload listener
├── manifest.json        # HA metadata (domain, version, iot_class)
├── const.py             # All constants: field names, country maps, thresholds
├── config_flow.py       # 3-step add flow + 2-step options flow
├── sensor.py            # Sensor entities: VehicleDateSensor, VehicleServiceSensor, VehicleOdometerSensor
├── strings.json         # English UI strings (base file)
└── translations/
    ├── en.json           # English
    ├── ro.json           # Română
    ├── de.json           # Deutsch
    ├── fr.json           # Français
    ├── it.json           # Italiano
    ├── es.json           # Español
    ├── pl.json           # Polski
    └── hu.json           # Magyar
```

---

## License

MIT — free to use, modify and distribute.  
Contributions and pull requests welcome.
