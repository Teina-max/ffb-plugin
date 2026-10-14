---
name: request-stats
description: Tableau de statistiques mensuel des demandes d'adhérents (volumes, thèmes, service, canal), calculé à partir du fichier de suivi des demandes, pour la direction.
---

# Statistiques mensuelles des demandes

Réponds en français. Ce parcours lit le fichier de suivi `suivi-demandes.csv` du dossier de
travail et produit un tableau ; il ne modifie jamais le suivi.

1. Confirme le dossier de travail explicitement sélectionné. Localise [le helper](../../scripts/ffb.py)
   depuis ce skill, vérifie le manifeste voisin et lis [le contrat CLI](../../README.md).
   Relis le profil avec `profile-read`. S'il est absent, suis [setup](../setup/SKILL.md).
2. Demande le mois voulu (format `AAAA-MM`). Sans précision, propose le mois précédent et
   attends la confirmation.
3. Lance `request-stats --root <dossier> --month <AAAA-MM>`.
4. Présente le résultat en tableaux courts : total du mois, répartition par service, par
   canal, puis par thème (du plus fréquent au moins fréquent). Si `ignored` est supérieur à
   0, signale ce nombre de lignes du suivi sans date lisible ni colonnes complètes, à
   corriger dans le fichier.
5. Affiche `statsPath` : le tableau s'ouvre dans Excel. Relancer le même mois le remplace.
6. Les délais de réponse ne sont pas calculables : le suivi ne contient pas encore la date
   d'envoi de la réponse. Dis-le si on te les demande, sans les estimer.

En cas d'erreur (suivi absent, en-tête modifié, mois invalide), affiche le message du helper
et n'invente aucun chiffre. Les thèmes sont regroupés sans tenir compte des majuscules ;
deux libellés différents pour un même sujet restent comptés séparément.
