# Panoramica dell’architettura

Ogni config entry Home Assistant possiede un runtime gateway isolato. I componenti Cloud, SIP/TLS, dialogo, multimedia, eventi, persistenza e diagnostica normalizzano lo stato prima che venga consumato dalle piattaforme entità. Le proprietà delle entità eseguono solo letture locali e non avviano accessi di rete.

Servizi globali e intent Assist risolvono una config entry precisa prima di inviare un comando. Il gateway fisico è il dispositivo radice; Cloud, SIP, chiamate, multimedia e diagnostica sono dispositivi logici. Alexa / Google Gate Bridge è un dispositivo virtuale indipendente senza `via_device`.

I comandi cancello richiedono un’azione esplicita, generano eventi di audit e non vengono ritentati alla cieca. Diagnostica e Support Bundle usano una sanitizzazione centralizzata.
