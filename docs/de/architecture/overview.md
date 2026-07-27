# Architekturüberblick

Jeder Konfigurationseintrag besitzt eine isolierte Gateway-Runtime. Cloud, SIP/TLS, Dialog, Medien, Ereignisse, Persistenz und Diagnose normalisieren ihren Zustand vor der Nutzung durch Entitäten. Entitätseigenschaften führen keine Netzwerkzugriffe aus.

Globale Dienste und Assist-Intents lösen vor Befehlen einen exakten Eintrag auf. Das physische Gateway ist das Wurzelgerät; Cloud, SIP, Anrufe, Medien und Diagnose sind logische Geräte. Die Alexa / Google Gate Bridge ist ein unabhängiges virtuelles Gerät ohne `via_device`.

Torbefehle erfordern eine ausdrückliche Aktion, erzeugen Audit-Ereignisse und werden nicht blind wiederholt. Diagnose und Support Bundle verwenden zentrale Bereinigung.
