<!-- hass-standards:header:start -->
# KOCOM Smart Home+ Energy (hass-kocom-smarthome)

A Home Assistant custom integration that connects to a KOCOM Smart Home+ wallpad to retrieve household energy metering data.

**English** | [한국어](README.ko.md)

<!-- hass-standards:badges:start -->
[![Release](https://img.shields.io/github/v/release/eigger/hass-kocom-smarthome?style=flat)](https://github.com/eigger/hass-kocom-smarthome/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5?style=flat)](#installation)
[![Home Assistant minimum](https://img.shields.io/badge/HA-%E2%89%A5%202025.8.0-41BDF5?style=flat)](hacs.json)
[![Tests](https://img.shields.io/github/actions/workflow/status/eigger/hass-kocom-smarthome/tests.yml?branch=main&style=flat&label=Tests)](https://github.com/eigger/hass-kocom-smarthome/actions/workflows/tests.yml)
[![Validate](https://img.shields.io/github/actions/workflow/status/eigger/hass-kocom-smarthome/validate.yml?branch=main&style=flat&label=Validate)](https://github.com/eigger/hass-kocom-smarthome/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/eigger/hass-kocom-smarthome?style=flat)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/eigger/hass-kocom-smarthome/total?style=flat&color=41BDF5&label=Downloads)](https://github.com/eigger/hass-kocom-smarthome/releases)
<!-- hass-standards:badges:end -->
<!-- hass-standards:header:end -->

- After pairing the wallpad with a mobile phone number, the integration periodically retrieves **monthly meter readings** from the apartment server.
- For electricity, heating, hot water, gas and water, it creates sensors for **household consumption / this month's apartment average / estimated charges**.
- Lighting, outlet and heating controls are **not yet** included. Only energy metering is currently supported.

## Sensors

Only items actually metered for the household are created. Some may be absent depending on
the apartment complex, wallpad configuration and fields returned by the apartment server.

| Energy | Unit | device_class | Sensors created |
| --- | --- | --- | --- |
| Electricity | kWh | `energy` | Consumption / apartment average / estimated charges |
| Heating | m³ | — | Consumption / apartment average / estimated charges |
| Hot water | m³ | — | Consumption / apartment average / estimated charges |
| Gas | m³ | `gas` | Consumption / apartment average / estimated charges |
| Water | m³ | `water` | Consumption / apartment average / estimated charges |

- **Consumption** is the household's meter reading; **apartment average** is the average across households in the same complex.
- Sensors are grouped under a **device** representing the wallpad. The device name is the wallpad alias
  configured in the KOCOM app, so a display name might be `Our home Electricity usage`.
- Estimated charge sensors use the currency `KRW`. They represent the estimated total for the period, rather than a unit rate.

Sensor names come from the translation files in [`translations/`](custom_components/kocom_smarthome/translations).
Korean and English are supported, following the Home Assistant language setting.

### Previous-month fallback

The apartment server may withhold the current month's data until its readings are finalized.
The integration then keeps sensors available using **previous-month data**.

- Sensors created from previous-month data have `(previous month)` in their names, such as `Electricity usage (previous month)`.
- If an energy kind has no current-month data at all, its previous-month value also feeds the current-month sensors to avoid gaps in the graph.
- Previous-month sensors use `state_class: total` instead of `total_increasing`, to avoid jumps in the Energy dashboard
  when the month changes.

Each sensor exposes `Registration Date` (the metering year and month) and `Sync date` (the last retrieval time) as attributes.

## Installation

<!-- hass-standards:installation:start -->
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=eigger&repository=hass-kocom-smarthome&category=integration)
<!-- hass-standards:installation:end -->

Requires Home Assistant 2025.8.0 or later. The badge opens the repository in an instance with HACS already installed; complete the download and restart steps below. For a custom repository, select the **Integration** category.

1. Add this repository as a custom repository in HACS, or copy `custom_components/kocom_smarthome`
   into `custom_components/` in your Home Assistant configuration directory.
2. Restart Home Assistant.
3. Select **Settings → Devices & services → Add integration → "코콤 스마트홈+ (에너지)"**.

### Prerequisites

- A **mobile phone number** to register on the wallpad (11 digits without hyphens)
- An **authentication code from the wallpad** (8 digits)

The authentication procedure varies by wallpad model and household. In its settings, select **Mobile phone connection**
(or a similarly named option) to display the code. Complete authentication before the code expires.

> If the number is **already registered** in the KOCOM Smart Home+ app, wallpad authentication is skipped automatically.

## Options

**Settings → Devices & services → 코콤 스마트홈+ (에너지) → Configure**:

| Option | Default | Description |
| --- | --- | --- |
| **Energy scan interval (hours)** | 24 | How often to retrieve meter readings from the apartment server |

Metering data is updated daily, so a shorter interval does not make readings change more often.
Keeping the default is recommended to avoid unnecessary load on the apartment server.

## Debugging

If something goes wrong, add the following to `configuration.yaml`, restart Home Assistant,
and attach the resulting logs to an issue.

```yaml
logger:
  default: info
  logs:
    custom_components.kocom_smarthome: debug
```

Phone numbers, household IDs and apartment server addresses are masked in logs, keeping only their last four characters.
Still, review logs before posting them to an issue.

If the apartment server rejects stored credentials, Home Assistant requests reauthentication. Confirm the prompt to log in again with the saved phone number; a successful refresh updates the existing configuration entry and retains its entities. If the wallpad pairing has been removed, remove the integration and add it again to pair the wallpad.

## Development

See the [development and testing guide (Korean)](docs/development.md).

<!-- hass-standards:support:start -->
## Support

- [Issues](https://github.com/eigger/hass-kocom-smarthome/issues): Report bugs or request features.
- [Discussions](https://github.com/eigger/hass-kocom-smarthome/discussions): Ask questions and share your experience.
<!-- hass-standards:support:end -->

<!-- hass-standards:related-projects:start -->
<!-- hass-standards:related-projects:end -->

<!-- hass-standards:license:start -->
## License

Released under the [MIT License](LICENSE).
<!-- hass-standards:license:end -->
