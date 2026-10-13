# Livrables et limites vérifiées

## Publié

| Livrable | Preuve |
|---|---|
| Dépôt public | https://github.com/NKZ05/infra-modernisation |
| Project public | https://github.com/users/NKZ05/projects/2 |
| 16 issues avec descriptions, critères et dépendances | https://github.com/NKZ05/infra-modernisation/issues?q=is%3Aissue |
| 4 jalons : S2, S6, S10 et S12 | https://github.com/NKZ05/infra-modernisation/milestones |
| 7 champs personnalisés et Status natif synchronisé | Project ; détails dans verification.json |
| PR contrôle disque, fusionnée | https://github.com/NKZ05/infra-modernisation/pull/17 |
| PR sauvegarde, fusionnée | https://github.com/NKZ05/infra-modernisation/pull/18 |
| Correction du seuil exact après première version | https://github.com/NKZ05/infra-modernisation/commit/431bb2b |
| Tests Ubuntu dans GitHub Actions | https://github.com/NKZ05/infra-modernisation/actions |
| Synthèse S4 : 71 jours-personnes, 6 tâches terminées | README.md et project.json |
| Après fusion : 8 terminées, 3 en cours, 1 bloquée, 4 à faire | Project et verification.json |
| Bonus : ajout automatique des sous-issues | Workflow intégré Auto-add sub-issues to project confirmé actif |

## Vues créées

- [Tableau opérationnel](https://github.com/users/NKZ05/projects/2/views/2)
- [Suivi des charges](https://github.com/users/NKZ05/projects/2/views/3)
- [Roadmap](https://github.com/users/NKZ05/projects/2/views/4)
- [Synthèse de direction](https://github.com/users/NKZ05/projects/2/views/5)
- [Risques élevés](https://github.com/users/NKZ05/projects/2/views/6)
- [Charge globale](https://github.com/users/NKZ05/projects/2/views/7)

## À finaliser dans l’interface avant remise

L’API accessible permet de créer les types de vues, les champs visibles et les filtres. Elle n’expose pas les réglages de regroupement, d’agrégation, de dates de la roadmap ni la création de graphiques Insights.

- Grouper le Kanban par Status si ce n’est pas déjà le regroupement par défaut.
- Grouper la table des charges par Domaine technique et afficher les sommes de Charge estimée ; vérifier 71 jours au total.
- Choisir les champs Date de début et Date de fin prévue dans la Roadmap ; afficher septembre à décembre 2026 et les jalons.
- Grouper la direction par Priorité et placer Critique en tête.
- Créer les trois graphiques Insights depuis les items du Project.
- Activer Item closed → Terminé pour automatiser le Status, si souhaité ; il est actuellement désactivé.
- Vérifier l’accès enseignant et conserver les captures des vues et graphiques.

Les réglages et valeurs de contrôle sont décrits dans [github-configuration.md](github-configuration.md). Ces étapes ne sont pas présentées comme réalisées.
