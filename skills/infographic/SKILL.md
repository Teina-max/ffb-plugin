---
name: infographic
description: Transformer un texte de service (social, RH, juridique) en infographie PowerPoint modifiable pour les adhérents (réseaux sociaux, Actu BTP) ou à la demande.
---

# Infographie PowerPoint modifiable

Réponds en français. Ce parcours prépare un brouillon : le service relit avant diffusion.
N'utilise comme faits que le texte fourni.

1. Confirme le dossier de travail explicitement sélectionné. Localise [le helper](../../scripts/ffb.py)
   depuis ce skill, vérifie le manifeste voisin et lis [le contrat CLI](../../README.md).
   Relis le profil avec `profile-read`. S'il est absent, suis [setup](../setup/SKILL.md).
2. Demande le texte source, le service, la destination (réseaux sociaux, Actu BTP, à la
   demande) et le format (carré pour les réseaux, 16:9 sinon). Sans texte, arrête-toi là.
3. Confirme un identifiant stable (par exemple `INFO-2026-05`) et la référence de source
   (`texte:<sujet court>`).
4. Construis le plan selon [le modèle](references/infographic-template.md) : un titre, trois à
   six blocs courts (un chiffre ou une idée chacun, 15 mots au plus), une source, un appel à
   l'action éventuel. Simplifie sans déformer : un chiffre, une date ou une obligation absents
   du texte ne sont pas ajoutés. Une nuance juridique importante reste visible en note.
5. Enregistre le plan via `save-draft` avec le JSON `{draft, department: "communication",
   companyRef: null}` sur stdin, pour garder la trace et permettre le rejeu.
6. Crée ensuite le fichier `.pptx` avec la création de fichiers de l'application, dans le
   dossier de travail : **éléments natifs modifiables** (zones de texte, formes, icônes
   simples), jamais une image unique aplatie ; charte FFB si elle est fournie, sinon sobre et
   contrastée (texte sombre sur fond clair, 24 pt au moins pour les chiffres). Si l'application
   ne peut pas créer de PowerPoint, dis-le et livre seulement le plan enregistré.
7. Affiche `draftPath`, le chemin du `.pptx` s'il a été créé, et le statut **brouillon, à relire
   avant diffusion**. Ne publie rien.
