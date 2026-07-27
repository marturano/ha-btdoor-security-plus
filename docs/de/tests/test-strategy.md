# Teststrategie

Die Freigabeprüfung kombiniert Python-Kompilierung, JSON/YAML-Prüfung, HACS, hassfest, gezielte Regressionen und Home-Assistant-2026.x-Runtimetests. Szenarien umfassen Neuinstallation, Upgrade, Setup, Reload, Unload, Neustart und mehrere Einträge.

Registry-Tests prüfen Duplikate sowie Erhalt von IDs, Namen, Bereichen und deaktiviertem Zustand. Sicherheitstests stellen sicher, dass automatische Pfade das Tor nie öffnen und ein Eintrag kein anderes Gateway steuert.

Assistenten, Bereinigung, private Exporte, Dashboards und Assist-Ressourcen sind getrennte Gates. Reale Geräte- und Assistentennachweise werden separat erfasst.
