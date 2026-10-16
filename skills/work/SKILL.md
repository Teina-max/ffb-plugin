---
name: work
description: Point d'entrée FFB pour traiter une demande métier, relire le profil local et orienter vers le bon parcours (réponse adhérent, diagnostic RH, document d'accueil, discours, communiqué, infographie, post, Actu, statistiques des demandes, fiche de préparation de rendez-vous, fiche récap d'un échange RH par mail, compte rendu de réunion pour les adhérents).
---

# Travailler avec FFB

Réponds en français. Demande le dossier de travail choisi si la session ne le connaît
pas explicitement. Ne le déduis pas d'une transcription ni d'un profil non vérifié.

1. Localise [le helper](../../scripts/ffb.py) depuis ce skill, vérifie le manifeste
   voisin et lis [le contrat CLI](../../README.md). Ne dépends pas d'une variable
   d'environnement supposée disponible dans Cowork. Si l'accès aux fichiers du plugin
   ou Python manque, explique la limite et n'annonce aucun enregistrement.
2. Exécute `profile-read --root <dossier choisi>` au début de chaque parcours.
   Si le profil est absent, propose puis suis [setup](../setup/SKILL.md).
   S'il est invalide, arrête le parcours et conserve le fichier existant.
3. Identifie la demande réelle. Le profil adapte le vocabulaire et le détail,
   il ne remplace pas la demande et n'autorise aucun accès.
4. Pour préparer ou exploiter un diagnostic RH d'adhérent, suis
   [hr-diagnostic](../hr-diagnostic/SKILL.md). Si aucun contenu n'est fourni, demande
   la transcription ou le compte rendu utile avant de rédiger des faits.
5. Pour une demande d'adhérent (appel, RDV ou mail collé, Juridique / Général) à traiter avec
   des éléments de réponse GenIA-L, suis [member-reply](../member-reply/SKILL.md).
6. Pour un discours (complet, en tirets ou note antisèche), suis [speech](../speech/SKILL.md).
   Pour un communiqué de presse, suis [press-release](../press-release/SKILL.md).
   Pour une infographie PowerPoint, suis [infographic](../infographic/SKILL.md).
   Pour un post réseaux sociaux, suis [social-post](../social-post/SKILL.md).
   Pour la mise en forme de l'Actu, suis [actu](../actu/SKILL.md).
   Pour le document RH remis à un nouvel adhérent, suis [welcome-pack](../welcome-pack/SKILL.md).
   Pour les statistiques mensuelles des demandes d'adhérents, suis [request-stats](../request-stats/SKILL.md).
   Pour préparer un rendez-vous avec une entreprise (nom ou SIREN), suis [company-brief](../company-brief/SKILL.md).
   Pour garder la trace d'un échange RH par mail avec un adhérent, suis [hr-recap](../hr-recap/SKILL.md).
   Pour le compte rendu d'une réunion (SP ou autre) destiné aux adhérents, suis [meeting-report](../meeting-report/SKILL.md).
7. Pour les autres demandes de communication, direction ou réunions générales, indique simplement
   que le parcours demandé n'est pas encore disponible dans cette version.
   Ne prétends pas avoir traité ou enregistré un dossier de ce pôle.

Leexi et Exa restent non configurés. Une demande RH à partir d'un document fourni
ne nécessite ni réseau ni connexion. Les sorties sont des brouillons à relire.
