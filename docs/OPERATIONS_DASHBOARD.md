# Operations Dashboard

La Beta 3 introduce un primo Operations Center basato esclusivamente su entità native.

1. Apri **Impostazioni → Dashboard → Aggiungi dashboard**.
2. Apri l'editor YAML della nuova dashboard.
3. Incolla `dashboards/btdoor_operations.yaml`.
4. Correggi soltanto gli `entity_id` che Home Assistant ha generato con un nome diverso.

Il nuovo sensore **Riepilogo operativo** concentra in un solo punto stato generale, health score, Cloud, SIP, Dialog, Media, codec e ultima chiamata.


## Assegnazione dispositivi 6.0.0-rc.2c

Il sensore **Riepilogo ultima chiamata** è associato al dispositivo **Monitor Chiamate**. L'`entity_id` e l'ID univoco restano invariati; non è quindi necessario modificare dashboard o automazioni esistenti. Gli attributi relativi a codec, durata e motivo di chiusura restano disponibili sul sensore.

La topologia logica è:

```text
Bticino DS+ Suite
├── Cloud Status
├── SIP Monitor
├── Monitor Chiamate
├── Monitor Multimediale
└── Diagnostica Avanzata (solo Developer Mode)
```
