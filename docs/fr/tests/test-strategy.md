# Stratégie de test

La validation combine compilation Python, analyse JSON/YAML, HACS, hassfest, régressions ciblées et tests runtime Home Assistant 2026.x. Les scénarios couvrent installation propre, mise à niveau, configuration, rechargement, déchargement, redémarrage et plusieurs entrées.

Les tests de registre vérifient l’absence de doublons et la conservation des identifiants, noms, zones et états désactivés. Les tests de sécurité garantissent qu’aucun chemin automatique n’ouvre le portail et qu’une entrée ne commande pas une autre passerelle.

Assistants, nettoyage, exports privés, tableaux et ressources Assist sont des contrôles distincts. Les preuves sur appareil réel restent séparées.
