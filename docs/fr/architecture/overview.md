# Vue d’ensemble de l’architecture

Chaque entrée de configuration possède un runtime de passerelle isolé. Cloud, SIP/TLS, dialogues, média, événements, persistance et diagnostics normalisent leur état avant consommation par les entités. Les propriétés d’entité ne lancent aucun accès réseau.

Les services globaux et les intents Assist résolvent une entrée précise avant toute commande. La passerelle physique est l’appareil racine ; Cloud, SIP, appels, média et diagnostics sont logiques. Alexa / Google Gate Bridge est un appareil virtuel indépendant sans `via_device`.

Les commandes du portail exigent une action explicite, produisent un audit et ne sont pas relancées à l’aveugle. Diagnostics et Support Bundles utilisent un nettoyage centralisé.
