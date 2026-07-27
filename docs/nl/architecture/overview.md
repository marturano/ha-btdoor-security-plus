# Architectuuroverzicht

Elke config-entry bezit een geïsoleerde gateway-runtime. Cloud, SIP/TLS, dialoog, media, gebeurtenissen, opslag en diagnose normaliseren hun status voordat entiteiten die gebruiken. Entiteitseigenschappen voeren geen netwerktoegang uit.

Globale diensten en Assist-intents lossen vóór opdrachten één exacte entry op. De fysieke gateway is het hoofdapparaat; Cloud, SIP, oproepen, media en diagnose zijn logisch. Alexa / Google Gate Bridge is een onafhankelijk virtueel apparaat zonder `via_device`.

Poortopdrachten vereisen expliciete actie, produceren auditgebeurtenissen en worden niet blind herhaald. Diagnose en Support Bundle gebruiken centrale opschoning.
