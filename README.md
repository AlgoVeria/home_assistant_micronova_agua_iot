# Micronova Agua IOT

[![GitHub Release][releases-shield]][releases]
[![Maintainer][maintainer-shield]][maintainer]
[![HACS Custom][hacs-shield]][hacs-url]

Home Assistant integration for controlling heating devices (pellet stoves) connected via the Agua IOT platform of Micronova.

Supports the following vendors (mobile apps):
* Alfaplam
* APP-O BIOEN
* Boreal Home
* Bronpi Home
* Darwin Evolution
* Easy Connect
* Easy Connect Plus
* Easy Connect Poêle
* Elcofire Pellet Home
* Elfire Wifi
* EOSS WIFI
* EvaCalòr - PuntoFuoco
* Fontana Forni
* Fonte Flamme contrôle 1
* Globe-fire
* GO HEAT
* Jolly Mec Wi Fi
* Karmek Wifi
* Klover Home
* LAMINOX Remote Control (2.0)
* Lorflam Home
* Moretti design
* My Corisit
* MyPiazzetta
* MySuperior
* Nina
* Nobis-Fi
* Nordic Fire 2.0
* Ravelli Wi-Fi
* Stufe a pellet Italia
* Thermoflux
* Total Control 3.0 (Extraflame)
* TS Smart
* Wi-Phire

Vendor apps **NOT** compatible (using a different platform or abstraction layer):
* Ravelli Smart Wi-Fi
* Total Control 2.0/1.x

## Screenshots
<img width="671" alt="micronova_screenshot1" src="https://github.com/vincentwolsink/home_assistant_micronova_agua_iot/assets/1639734/4c646550-637d-4e20-bc64-a6977bfee3af">
<img width="330" alt="micronova_screenshot3" src="https://github.com/vincentwolsink/home_assistant_micronova_agua_iot/assets/1639734/3a06b135-eaee-4ff2-94e4-c3da268fb7a9">

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=vincentwolsink&repository=home_assistant_micronova_agua_iot&category=integration)

Or folow these steps:
1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Install the plugin via HACS (Micronova Agua IOT)
3. Add the integration through the home assistant configuration flow

## Local Bluetooth mode

This integration now includes an experimental `Bluetooth` connection mode for Micronova stoves equipped with a local BLE module (for example the Micronova / Navel `T009_*` module seen by Home Assistant).

You can enable this mode via the integration options after setup.

For more information see [BLUETOOTH](docs/BLUETOOTH.md).

## Chrono, maintenance and diagnostic entities

These entities are created only when the stove's register map provides the register, so the list depends on the model.

| Register(s) | Entity | Notes |
|---|---|---|
| `chrono_general_enable_set` | Switch "Chrono" | Configuration |
| `chrono_week_enable_set` | Switch "Chrono Weekly" | Configuration |
| `chrono_pN_enable_set` | Switch "Chrono PN" | Configuration, on stoves with a per-program enable |
| `chrono_pN_start_set`, `chrono_pN_stop_set` | Time "Chrono PN Start/Stop" | 10-minute steps, rounded down; unknown when the slot is not set (144 = 24:00 and above) |
| `chrono_pN_power_set` | Select "Chrono PN Power" | Labels from the stove (e.g. `SIL` = Silent) |
| `chrono_pN_temperature_set` | Number "Chrono PN Temperature" | Step follows the register formula (1 °C or 0.5 °C) |
| `chrono_pN_day_<weekday>_set` | Switch "Chrono PN <Weekday>" | Disabled by default, prefer the `set_chrono_program` service |
| `allarm_reset_set` | Button "Reset Alarm" | Available only while an alarm is active |
| `load_pellet_set` | Button "Load Pellets" | Starts a manual pellet load of "Pellet Load Duration" seconds. Available only while the stove is off (state 0) |
| `load_pellet_set` | Number "Pellet Load Duration" | Configuration, stored in Home Assistant only (nothing is written until the button is pressed). Limited to the `load_pellet_set` maximum of the register map, see below |
| `load_pellet_get` | Sensor "Pellet Load Remaining" | Countdown of the running load, in seconds |
| `load_pellet_max` | Sensor "Pellet Load Maximum" | Diagnostic |
| `w_p_braciere_get` | Binary sensor "Brazier Cleaning Warning" | |
| `w_spegnimento_get` | Binary sensor "Waiting For Shutdown" | |
| `probe_correct_set` | Number "Room Probe Correction" | Configuration, 0.5 °C steps |
| `clock_*_set`, `calendar_*_set` | Sensor "Clock Drift" | Diagnostic: stove clock minus Home Assistant clock, in minutes. Use `aguaiot.sync_clock` to fix it |

The remote control starts a manual load of `load_pellet_max` seconds (200 on a Jolly Mec Botero 2), but the cloud register map declares `load_pellet_set` as 0-100. As writes never go beyond the register map limits, a load started from Home Assistant lasts at most 100 seconds on that stove: press the button again once the countdown is over for a longer load.

The brazier cleaning warning (`w_p_braciere_get`) is acknowledged from the stove or its remote control: writing `cleaning_brazier_set` from the cloud is accepted, but the stove sets the flag back on the next reading.

A stove register that could not be read (raw value `0x8000`) is shown as unknown on the switches and times above.

### Service `aguaiot.set_chrono_program`

Writes one chrono program in a single request. Only the fields given are written; values read from the stove are never written back. Values outside the register map limits are rejected.

```yaml
action: aguaiot.set_chrono_program
target:
  entity_id: climate.my_stove
data:
  program: 1
  start: "06:00:00"
  stop: "22:30:00"
  power: 3
  temperature: 20.5
  days: [monday, tuesday, wednesday, thursday, friday]
```

`days` lists the days on which the program runs; the other days are switched off. An empty list switches the program off on every day.

## Credits

Some parts of the code are based on [py-agua-iot](https://github.com/fredericvl/py-agua-iot)

## Related

For local stove control with custom hardware on the stove bus, take a look at one of these projects.
* https://esphome.io/components/micronova.html
* https://github.com/eni23/micronova-controller
* https://github.com/fabrizioromanelli/Pellet-Stove-Control
* https://github.com/philibertc/micronova_controller
* https://github.com/Shad107/OpenXtraflame

[releases-shield]: https://img.shields.io/github/v/release/vincentwolsink/home_assistant_micronova_agua_iot.svg?style=for-the-badge
[releases]: https://github.com/vincentwolsink/home_assistant_micronova_agua_iot/releases
[maintainer-shield]: https://img.shields.io/badge/maintainer-vincentwolsink-blue.svg?style=for-the-badge
[maintainer]: https://github.com/vincentwolsink
[hacs-shield]: https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge
[hacs-url]: https://github.com/vincentwolsink/home_assistant_micronova_agua_iot
