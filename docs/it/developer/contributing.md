# Contribuire

Preserva sicurezza asincrona, isolamento per config entry, identità stabili di dispositivi/entità e sanitizzazione centralizzata. Non eseguire operazioni bloccanti sull’event loop di Home Assistant e non aggiungere chiamate di rete alle proprietà delle entità.

Le modifiche architetturali richiedono un ADR e una voce nell’Engineering Notebook. Aggiorna nello stesso intervento changelog, evidenze di compatibilità e traduzioni. I comandi sul cancello richiedono intento esplicito e non devono mai essere eseguiti durante setup, migrazione, reload o retry.

Il ramo 1.1 è dedicato alla stabilizzazione: non introdurre adapter 1.2 né dichiarare compatibilità con firmware sconosciuti. Ogni nuova stringa inglese deve essere aggiunta a tutte le lingue supportate mantenendo gli stessi placeholder.
