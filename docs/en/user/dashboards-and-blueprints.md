# Dashboards and blueprints

Use the dashboard manager supplied by the integration so template tokens are resolved against the selected config entry. Import the rendered YAML, not the raw template. Verify every resolved entity before enabling cards that perform actions.

The gate card must call `button.press` on `button.apri_cancello` and should require confirmation. Do not use the retired gate `cover` model or `cover.open_cover`. Existing stored dashboards may contain legacy placeholders; the resolver preserves supported compatibility aliases, but new dashboards must use current entities.

The Operations dashboard can include Cloud, SIP, Call Manager, Multimedia Monitor and the Last Call Summary. Developer Console and advanced diagnostic entities should remain private.

A certificate-expiry blueprint exists in historical material but requires a dedicated remaining-days sensor. Until that entity is implemented, it must not be presented as a fully supported 1.1 workflow.
