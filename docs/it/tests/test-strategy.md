# Strategia di test

La validazione combina compilazione Python, parsing JSON/YAML, controlli HACS e hassfest, regressioni mirate e test runtime su Home Assistant 2026.x. Gli scenari runtime includono installazione pulita, upgrade supportato, setup, reload, unload, riavvio e più config entry.

I test del registry verificano assenza di duplicati e conservazione di unique ID, nomi personalizzati, aree e stato disabled. I test di sicurezza assicurano che setup, migrazione, reload e retry non aprano il cancello e che una config entry non possa comandare un altro gateway.

Assistenti, sanitizzazione, export privati, compatibilità dashboard e risorse Assist gestite sono gate separati. I risultati su dispositivo reale e assistente esterno devono essere registrati come classi di evidenza distinte.
