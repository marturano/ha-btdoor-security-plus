# Teststrategie

Releasevalidatie combineert Python-compilatie, JSON/YAML-controle, HACS, hassfest, gerichte regressies en Home Assistant 2026.x-runtimetests. Scenario’s omvatten schone installatie, upgrade, setup, reload, unload, herstart en meerdere entries.

Registertests controleren duplicaten en behoud van IDs, namen, gebieden en uitgeschakelde status. Veiligheidstests bewijzen dat automatische paden de poort nooit openen en dat één entry geen andere gateway bestuurt.

Assistenten, opschoning, privé-export, dashboards en Assist-bronnen zijn aparte gates. Bewijs met echte apparaten wordt afzonderlijk vastgelegd.
