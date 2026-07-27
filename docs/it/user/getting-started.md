# Per iniziare

## Installazione
Installa BTDoor Security+ tramite HACS come repository personalizzato oppure copia `custom_components/btdoor_security_plus` nella configurazione di Home Assistant. Riavvia Home Assistant, quindi apri **Impostazioni → Dispositivi e servizi → Aggiungi integrazione** e seleziona BTDoor Security+.

## Configurazione
Usa lo stesso account MyHomeWeb autorizzato dal proprietario e utilizzato dall’app ufficiale Door Entry. Seleziona il gateway corretto e completa il provisioning SIP. Non copiare identità, certificati o credenziali da un’altra installazione.

## Prima verifica
Controlla che gateway e dispositivi logici compaiano una sola volta. Verifica Cloud e SIP, quindi premi `button.apri_cancello` soltanto quando è sicuro azionare il cancello fisico. Setup, reload e riavvio non devono mai aprirlo automaticamente.

Abilita Developer Mode o Support Debug solo durante la diagnosi. I Support Bundle sono sanitizzati ma vanno comunque trattati come privati.
