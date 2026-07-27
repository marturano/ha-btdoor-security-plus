# Dashboards en blueprints

Gebruik de dashboardmanager zodat sjabloontokens voor de gekozen config-entry worden opgelost. Importeer de gegenereerde YAML en controleer alle entiteiten voordat acties worden ingeschakeld.

De poortkaart moet `button.press` op `button.apri_cancello` met bevestiging uitvoeren. Gebruik niet het oude `cover`-model of `cover.open_cover`. Ondersteunde oude placeholders blijven werken voor opgeslagen dashboards; nieuwe dashboards gebruiken actuele entiteiten.

Het operationele dashboard kan Cloud, SIP, oproepen, media en de laatste oproepsamenvatting tonen. Developer Console blijft privé. De historische certificaat-blueprint vereist nog een sensor voor resterende dagen en is daarom geen volledig ondersteunde 1.1-workflow.
