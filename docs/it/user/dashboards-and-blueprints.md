# Dashboard e blueprint

Usa il gestore dashboard dell’integrazione affinché i token del modello siano risolti per la config entry selezionata. Importa lo YAML generato, non il modello grezzo. Verifica ogni entità risolta prima di abilitare schede che eseguono azioni.

La scheda cancello deve chiamare `button.press` su `button.apri_cancello` e dovrebbe richiedere conferma. Non usare il vecchio modello `cover` né `cover.open_cover`. Le dashboard già salvate possono contenere placeholder legacy supportati, ma le nuove devono usare le entità correnti.

La dashboard operativa può includere Cloud, SIP, Gestione chiamate, Monitor multimediale e riepilogo ultima chiamata. Developer Console e diagnostica avanzata devono restare private.

Il blueprint storico per la scadenza del certificato richiede un sensore dedicato dei giorni residui. Finché tale entità non sarà implementata, non va presentato come flusso 1.1 pienamente supportato.
