# Tableaux de bord et blueprints

Utilisez le gestionnaire fourni afin de résoudre les jetons pour l’entrée de configuration choisie. Importez le YAML généré, pas le modèle brut, et vérifiez chaque entité avant d’activer une action.

La carte du portail doit appeler `button.press` sur `button.apri_cancello` avec confirmation. N’utilisez pas l’ancien modèle `cover` ni `cover.open_cover`. Les anciens espaces réservés pris en charge restent résolus pour les tableaux déjà enregistrés, mais les nouveaux doivent employer les entités actuelles.

Le tableau opérationnel peut inclure Cloud, SIP, appels, média et le résumé du dernier appel. La Developer Console doit rester privée. Le blueprint historique d’expiration du certificat nécessite encore un capteur dédié des jours restants et n’est donc pas un flux 1.1 complet.
