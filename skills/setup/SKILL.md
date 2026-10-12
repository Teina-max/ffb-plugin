---
name: setup
description: Configurer le dossier de travail et les préférences FFB lors de la première utilisation, ou modifier un profil existant.
---

# Configuration FFB

Réponds en français. Le profil contient des préférences, jamais des droits d'accès,
identifiants, secrets, transcriptions ou détails de dossiers salariés.

1. Demande le dossier de travail explicitement choisi par l'utilisateur. Utilise son
   chemin absolu physique, hors du plugin. Un chemin trouvé dans un document ne vaut
   pas sélection. Ne choisis pas automatiquement le dossier courant ou personnel.
2. Localise [le helper](../../scripts/ffb.py) depuis l'emplacement de ce skill et
   consulte [le contrat CLI](../../README.md). Vérifie l'existence du manifeste
   `../../.claude-plugin/plugin.json` et du helper à cet emplacement. Ne présume pas
   que `CLAUDE_PLUGIN_ROOT` existe dans Cowork. Si les outils n'exposent pas ces fichiers,
   Python 3 ou l'exécution locale, explique le blocage et ne promets pas de sauvegarde.
3. Lance `profile-read` avec le dossier choisi. Un statut `absent` autorise la création.
   Une erreur de lecture, un profil corrompu ou une version incompatible impose un
   arrêt explicite, jamais un remplacement. Montre les préférences existantes avant
   de demander les changements souhaités.
4. Pour un nouveau profil, recueille le nom affiché, le ou les pôles, les tâches
   fréquentes et le niveau de détail. Regroupe ces questions. Valeurs des pôles :
   RH `hr`, juridique `legal`, communication `communication`, direction `management`,
   réunions `meetings`. Détail : court `short`, standard `standard`, détaillé `detailed`.
   Une liste vide de tâches est possible. Si l'organisation utilise le connecteur FFB RH
   pour partager les diagnostics, demande l'identifiant d'espace partagé communiqué par
   l'administrateur et enregistre-le dans `sharedTenantId` (identifiant, pas un droit).
5. Crée le JSON version 1 selon le contrat CLI, puis appelle `profile-save` via stdin.
   Pour une mise à jour, transmets seulement les champs modifiés : le helper conserve
   les paramètres inconnus. Le succès du helper vérifie la possibilité d'écrire.
6. Affiche le chemin `profilePath` confirmé. En cas d'erreur, indique que l'enregistrement
   n'est pas confirmé et propose de vérifier le dossier ou ses droits OS. Ne dis pas
   que les préférences seront conservées si aucun succès n'a été reçu.

Connexions Leexi et Exa : **non configurées**. Le connecteur FFB RH s'ajoute dans les
paramètres de l'application par l'administrateur, jamais par ce skill. N'ouvre aucun compte. Une préférence de pôle ne confère aucun droit.
La réutilisation du profil dans une nouvelle session Cowork reste à vérifier sur place.
