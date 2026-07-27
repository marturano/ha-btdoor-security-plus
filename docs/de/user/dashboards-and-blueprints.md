# Dashboards und Blueprints

Verwenden Sie den Dashboard-Manager, damit Vorlagen-Token für den gewählten Konfigurationseintrag aufgelöst werden. Importieren Sie das erzeugte YAML und prüfen Sie jede Entität vor dem Aktivieren von Aktionen.

Die Torkarte muss `button.press` für `button.apri_cancello` mit Bestätigung aufrufen. Verwenden Sie weder das alte `cover`-Modell noch `cover.open_cover`. Unterstützte ältere Platzhalter bleiben für gespeicherte Dashboards erhalten; neue Dashboards nutzen aktuelle Entitäten.

Das Betriebsdashboard kann Cloud, SIP, Anrufe, Medien und die letzte Anrufzusammenfassung enthalten. Die Developer Console bleibt privat. Der historische Zertifikats-Blueprint benötigt noch einen Resttage-Sensor und ist kein vollständig unterstützter 1.1-Ablauf.
