# Changelog

## 1.1.1

- A failed first energy poll (for example an unreachable apartment server) no longer puts the entry into setup retry. The integration loads, retries every 5 minutes until the first success, then returns to the configured interval; sensors are created when the first response arrives.
- Authentication failures during setup still start reauthentication.

## 1.0.1

- Adopt shared repository standards and SHA-pinned validation/test workflows.
- Add real Home Assistant setup, sensor, configuration, migration and unload coverage for minimum HA 2025.8.0 and current HA 2026.10.2.
- Provide English and Korean documentation with HACS installation links and a local energy-meter icon.
- Classify the integration as energy meter monitoring.
- Add reauthentication with the saved phone number, refreshing the existing entry while retaining entities.
- Prevent server responses and household identifiers from appearing in error messages; report rejected stored credentials as authentication failures.

The minimum supported Home Assistant version remains 2025.8.0. Existing configuration entries and entity identifiers are retained. Restart Home Assistant after updating through HACS. If the server rejects stored credentials, confirm Home Assistant's reauthentication prompt to refresh them with the saved phone number. If wallpad pairing has been removed, remove and add the integration again to pair the wallpad. Physical wallpad, apartment-server and Home Assistant UI validation has not been performed for this release.
